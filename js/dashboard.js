/* Cognitorium Representation Engine — chrome illustrations + live data */

(function () {
  "use strict";

  const MAX = 180;
  const TICK_MS = 280;
  const VIEWS = {
    accueil: { titre: "Accueil", sub: "Anneaux de couverture et confiance — pas un score de personnalité" },
    cognition: { titre: "Cognition", sub: "Langages collectés et construits estimés" },
    univers: { titre: "Univers", sub: "Constellation knowledge · evidence · inference" },
    signaux: { titre: "Signaux", sub: "Features en direct — aucun tracé brut" },
    temps: { titre: "Temps", sub: "Quatrième dimension · fan chart d’incertitude" }
  };
  const FALLBACK_ONTO = {
    constructs: [
      { id: "k-charge", label: "Charge cognitive", measuredBy: ["e-hr", "e-hrv", "e-temps", "e-erreurs"] },
      { id: "k-activation", label: "Activation", measuredBy: ["e-hr", "e-hrv"] },
      { id: "k-frustration", label: "Frustration", measuredBy: ["e-erreurs", "e-temps"] },
      { id: "k-effort", label: "Effort physique", measuredBy: ["e-hr"] }
    ],
    channels: [
      { id: "e-hr", label: "FC", unite: "bpm", baseline: 68, on: true, slot: "coeur" },
      { id: "e-hrv", label: "HRV", unite: "rel", on: true, slot: "coeur" },
      { id: "e-temps", label: "Temps tâche", unite: "s", on: true, slot: "tache" },
      { id: "e-erreurs", label: "Erreurs", unite: "n", on: true, slot: "tache" },
      { id: "e-resp", label: "Respiration", on: false, slot: "souffle" },
      { id: "e-eeg", label: "EEG / BCI", on: false, slot: "tete" },
      { id: "e-parole", label: "Parole", on: false, slot: "voix" },
      { id: "e-video", label: "Vidéo", on: false, slot: "visage" }
    ]
  };

  const S = {
    playing: true, cursor: 0, selected: "i-charge",
    layers: { K: true, E: true, I: true },
    view: "univers", query: "",
    onto: FALLBACK_ONTO, channels: [], hist: [], timer: null
  };

  function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }
  function pct(x) { return Math.round(x * 100); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function fmtT(sec) {
    const s = Math.max(0, Math.floor(sec));
    return "T0 + " + pad(Math.floor(s / 60)) + ":" + pad(s % 60);
  }
  function onSet() {
    const set = new Set();
    S.channels.forEach(function (c) { if (c.on) set.add(c.id); });
    return set;
  }
  function matchQ(label) {
    if (!S.query) return true;
    return (label || "").toLowerCase().indexOf(S.query) >= 0;
  }

  function infer(sample, on) {
    const load = clamp((sample.hr - 68) / 48, 0, 1);
    const err = clamp(sample.errors / 7, 0, 1);
    const time = clamp(sample.t / 900, 0, 1);
    const hrvLow = clamp(1 - sample.hrv, 0, 1);
    function est(kid, iid, base, evid, alts) {
      const active = evid.filter(function (e) { return on.has(e); });
      const ratio = evid.length ? active.length / evid.length : 0;
      if (ratio < 0.25) return { id: iid, k: kid, status: "refused", reason: "NO_EVIDENCE", evid: active, alts: alts };
      const p = clamp(base * (0.4 + 0.6 * ratio), 0.06, 0.9);
      const w = 0.1 + (1 - ratio) * 0.16;
      return { id: iid, k: kid, status: "estimated", p: p, lo: clamp(p - w, 0, 1), hi: clamp(p + w * 0.9, 0, 1), evid: active, alts: alts };
    }
    return [
      est("k-charge", "i-charge", 0.28 + 0.32 * load + 0.18 * err + 0.14 * time + 0.12 * hrvLow,
        ["e-hr", "e-hrv", "e-temps", "e-erreurs"], ["effort", "excitation", "difficulté de tâche"]),
      est("k-activation", "i-activation", 0.22 + 0.55 * load + 0.1 * hrvLow,
        ["e-hr", "e-hrv"], ["effort physique", "stress", "déplacement"]),
      est("k-frustration", "i-frustration", 0.12 + 0.55 * err + 0.18 * time,
        ["e-erreurs", "e-temps"], ["charge", "consigne ambiguë"]),
      est("k-effort", "i-effort", 0.08 + 0.25 * load, ["e-hr"], ["activation", "posture"])
    ];
  }

  function seedWalk() {
    S.channels = S.onto.channels.map(function (c) { return Object.assign({}, c); });
    S.hist = [];
    let hr = 86, hrv = 0.62, errors = 0;
    for (let t = 0; t <= 42; t++) {
      hr = clamp(hr + (Math.random() - 0.48) * 1.8 + 0.04 * (90 - hr), 72, 112);
      hrv = clamp(hrv + (Math.random() - 0.5) * 0.04 + 0.02 * (0.55 - hrv), 0.25, 0.9);
      if (Math.random() < 0.07) errors += 1;
      const sample = { t: t, hr: hr, hrv: hrv, temps: t, errors: errors };
      sample.estimates = infer(sample, onSet());
      S.hist.push(sample);
    }
    S.cursor = S.hist.length - 1;
  }

  function tick() {
    const last = S.hist[S.hist.length - 1];
    const sample = {
      t: last.t + 1,
      hr: clamp(last.hr + (Math.random() - 0.48) * 1.7 + 0.03 * (91 - last.hr), 72, 114),
      hrv: clamp(last.hrv + (Math.random() - 0.5) * 0.035, 0.22, 0.92),
      temps: last.t + 1,
      errors: last.errors + (Math.random() < 0.06 ? 1 : 0)
    };
    sample.estimates = infer(sample, onSet());
    S.hist.push(sample);
    if (S.hist.length > MAX) S.hist.shift();
    S.cursor = S.hist.length - 1;
    draw();
  }

  function now() { return S.hist[S.cursor] || S.hist[S.hist.length - 1]; }
  function recomputeFrom(i) {
    const on = onSet();
    for (; i < S.hist.length; i++) S.hist[i].estimates = infer(S.hist[i], on);
  }

  function related(id) {
    const set = new Set([id]);
    const n = now();
    if (!n) return set;
    S.onto.constructs.forEach(function (k) {
      if (k.id === id) {
        set.add("i-" + k.id.slice(2));
        (k.measuredBy || []).forEach(function (e) { set.add(e); });
      }
    });
    n.estimates.forEach(function (est) {
      if (est.id === id || est.k === id) {
        set.add(est.id); set.add(est.k);
        est.evid.forEach(function (e) { set.add(e); });
      }
      if (est.evid.indexOf(id) >= 0) { set.add(est.id); set.add(est.k); }
    });
    return set;
  }

  function polar(cx, cy, r, i, n, rot) {
    const a = (rot || -Math.PI / 2) + i * 2 * Math.PI / Math.max(n, 1);
    return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
  }

  function layout(cx, cy) {
    const n = now();
    const pos = { t0: { x: cx, y: cy } };
    S.onto.constructs.forEach(function (k, i) {
      pos[k.id] = polar(cx, cy, 95, i, S.onto.constructs.length, -Math.PI / 2);
    });
    (n ? n.estimates : []).forEach(function (e, i) {
      pos[e.id] = polar(cx, cy, 185, i, 4, -Math.PI / 2 + 0.2);
    });
    S.channels.forEach(function (c, i) {
      pos[c.id] = polar(cx, cy, 285, i, S.channels.length, -Math.PI / 2);
    });
    return pos;
  }

  function stars(w, h) {
    let s = "";
    for (let i = 0; i < 70; i++) {
      const x = (i * 97) % w, y = (i * 53) % h, r = 0.4 + (i % 3) * 0.35;
      s += '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="#8aa" opacity="0.35"/>';
    }
    return s;
  }

  function drawConstellation(svg, w, h) {
    const n = now();
    if (!n || !svg) return;
    const cx = w / 2, cy = h / 2 - 10;
    const pos = layout(cx, cy);
    const rel = related(S.selected);
    const show = S.layers;
    let edges = "";
    n.estimates.forEach(function (est) {
      const pI = pos[est.id], pK = pos[est.k], p0 = pos.t0;
      if (pI && p0 && show.I) {
        edges += '<path class="edge I' + (rel.has(est.id) ? " on" : "") + '" stroke="#e4b15a" stroke-dasharray="4 3" d="M' + p0.x + " " + p0.y + " L" + pI.x + " " + pI.y + '"/>';
      }
      if (pI && pK && show.K && show.I) {
        edges += '<path class="edge K' + (rel.has(est.id) || rel.has(est.k) ? " on" : "") + '" stroke="#60a5fa" d="M' + pK.x + " " + pK.y + " L" + pI.x + " " + pI.y + '"/>';
      }
      if (show.E && show.I && pI) {
        est.evid.forEach(function (eid) {
          const pE = pos[eid];
          if (!pE) return;
          edges += '<path class="edge E' + (rel.has(est.id) || rel.has(eid) ? " on" : "") + '" stroke="#2dd4bf" d="M' + pE.x + " " + pE.y + " L" + pI.x + " " + pI.y + '"/>';
        });
      }
    });

    function node(id, label, layer, extra) {
      if (layer !== "T0" && !show[layer]) return "";
      if (!pos[id]) return "";
      if (!matchQ(label) && S.query) extra = Object.assign({}, extra || {}, { dim: true });
      const p = pos[id];
      const hot = rel.has(id) || id === "t0";
      const col = layer === "K" ? "#60a5fa" : layer === "E" ? "#2dd4bf" : layer === "T0" ? "#22d3ee" : "#e4b15a";
      const refused = extra && extra.status === "refused";
      const off = extra && extra.off;
      const dim = extra && extra.dim;
      const stroke = refused ? "#fb7185" : off ? "#334155" : col;
      const fill = hot ? stroke : "#050814";
      const dash = layer === "I" || off || refused ? " stroke-dasharray=\"4 3\"" : "";
      const r = layer === "T0" ? 18 : hot ? 14 : 10;
      const op = dim ? " opacity=\"0.2\"" : "";
      return '<g class="node" data-id="' + id + '" data-label="' + label + '"' + op + ">" +
        '<circle cx="' + p.x + '" cy="' + p.y + '" r="' + (r + 6) + '" fill="' + stroke + '" opacity="0.12"/>' +
        '<circle cx="' + p.x + '" cy="' + p.y + '" r="' + r + '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="2"' + dash + "/>" +
        '<text x="' + p.x + '" y="' + (p.y + r + 14) + '" text-anchor="middle" fill="#cfe6f5" font-size="11">' + label + "</text></g>";
    }

    let nodes = node("t0", "T0", "T0");
    S.onto.constructs.forEach(function (k) { nodes += node(k.id, k.label, "K"); });
    n.estimates.forEach(function (est) {
      const lab = S.onto.constructs.filter(function (k) { return k.id === est.k; })[0];
      nodes += node(est.id, lab ? lab.label : est.id, "I", est);
    });
    S.channels.forEach(function (c) {
      nodes += node(c.id, c.label + (c.on ? "" : " · off"), "E", { off: !c.on });
    });

    svg.innerHTML = '<defs><filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>' +
      stars(w, h) + edges + nodes;

    svg.querySelectorAll(".node").forEach(function (g) {
      g.addEventListener("click", function (ev) {
        ev.stopPropagation();
        S.selected = g.getAttribute("data-id");
        draw();
      });
      g.addEventListener("mousemove", function (ev) {
        const tip = document.getElementById("tip");
        if (!tip) return;
        const id = g.getAttribute("data-id");
        const est = n.estimates.filter(function (e) { return e.id === id; })[0];
        let html = "<strong>" + g.getAttribute("data-label") + "</strong>";
        if (est && est.status === "estimated") html += "<br>" + pct(est.p) + " % [" + pct(est.lo) + "–" + pct(est.hi) + "]";
        if (est && est.status === "refused") html += "<br>Refusal · " + est.reason;
        tip.innerHTML = html;
        tip.hidden = false;
        const r = svg.getBoundingClientRect();
        tip.style.left = (ev.clientX - r.left + 12) + "px";
        tip.style.top = (ev.clientY - r.top + 12) + "px";
      });
      g.addEventListener("mouseleave", function () {
        const tip = document.getElementById("tip");
        if (tip) tip.hidden = true;
      });
    });
  }

  function spark(arr, w, h, color) {
    if (!arr.length) return "";
    const min = Math.min.apply(null, arr), max = Math.max.apply(null, arr), span = max - min || 1;
    let d = "";
    arr.forEach(function (v, i) {
      const x = arr.length === 1 ? 0 : i * (w - 4) / (arr.length - 1);
      const y = h - 4 - ((v - min) / span) * (h - 8);
      d += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1) + " ";
    });
    return '<path d="' + d + '" fill="none" stroke="' + color + '" stroke-width="1.6"/>';
  }

  function waveKeys() {
    return [
      { id: "e-hr", key: "hr", label: "FC", unit: "bpm" },
      { id: "e-hrv", key: "hrv", label: "HRV", unit: "" },
      { id: "e-temps", key: "temps", label: "Temps", unit: "s" },
      { id: "e-erreurs", key: "errors", label: "Erreurs", unit: "" }
    ];
  }

  function fillWaves(root, h) {
    if (!root) return;
    const rel = related(S.selected);
    root.replaceChildren();
    waveKeys().forEach(function (k) {
      const ch = S.channels.filter(function (c) { return c.id === k.id; })[0];
      const on = ch && ch.on;
      const series = on ? S.hist.slice(0, S.cursor + 1).map(function (s) { return s[k.key]; }) : [];
      const last = series.length ? series[series.length - 1] : null;
      const box = document.createElement("div");
      box.className = "wave";
      box.dataset.sel = rel.has(k.id) ? "true" : "false";
      const val = last == null ? "off" : (k.key === "hrv" ? last.toFixed(2) : String(Math.round(last * 10) / 10));
      box.innerHTML = '<div class="meta"><span>' + k.label + "</span><b>" + val + (on && k.unit ? " " + k.unit : "") + "</b></div>" +
        '<svg viewBox="0 0 240 ' + h + '">' + (on ? spark(series, 240, h, "#2dd4bf") : "") + "</svg>";
      box.addEventListener("click", function () { S.selected = k.id; draw(); });
      root.appendChild(box);
    });
  }

  function fanPath(svg, W, H) {
    if (!svg) return;
    let iid = "i-charge";
    if (S.selected && S.selected.indexOf("i-") === 0) iid = S.selected;
    else if (S.selected && S.selected.indexOf("k-") === 0) iid = "i-" + S.selected.slice(2);
    const lab = S.onto.constructs.filter(function (k) { return "i-" + k.id.slice(2) === iid; })[0];
    const title = document.getElementById("fan-title");
    const titleF = document.getElementById("fan-title-full");
    const t = (lab ? lab.label : "Estimation") + " · fan chart";
    if (title) title.textContent = t;
    if (titleF) titleF.textContent = t;
    const pts = S.hist.slice(0, S.cursor + 1).map(function (s) {
      const est = s.estimates.filter(function (e) { return e.id === iid; })[0];
      if (!est || est.status !== "estimated") return { y: null };
      return { y: est.p, lo: est.lo, hi: est.hi };
    });
    const pl = 28, pr = 8, pt = 8, pb = 16, iw = W - pl - pr, ih = H - pt - pb;
    const x = function (i) { return pl + (pts.length < 2 ? iw / 2 : i * iw / (pts.length - 1)); };
    const y = function (v) { return pt + (1 - v) * ih; };
    const ok = [];
    pts.forEach(function (p, i) { if (p.y != null) ok.push({ i: i, p: p }); });
    if (!ok.length) {
      svg.innerHTML = '<text x="28" y="' + (H / 2) + '" fill="#7f93b3" font-size="12">Refusal — preuves insuffisantes.</text>';
      return;
    }
    let band = "", line = "";
    ok.forEach(function (o, n) { band += (n ? "L" : "M") + x(o.i).toFixed(1) + " " + y(o.p.hi).toFixed(1) + " "; });
    for (let n = ok.length - 1; n >= 0; n--) band += "L" + x(ok[n].i).toFixed(1) + " " + y(ok[n].p.lo).toFixed(1) + " ";
    band += "Z";
    ok.forEach(function (o, n) { line += (n ? "L" : "M") + x(o.i).toFixed(1) + " " + y(o.p.y).toFixed(1) + " "; });
    svg.innerHTML =
      '<defs><pattern id="hach' + W + '" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">' +
      '<line x1="0" y1="0" x2="0" y2="6" stroke="rgb(228 177 90 / 0.5)" stroke-width="2"/></pattern></defs>' +
      '<path d="' + band + '" fill="url(#hach' + W + ')"/>' +
      '<path d="' + line + '" fill="none" stroke="#2dd4bf" stroke-width="2"/>';
  }

  function ringSVG(value, label, sub, color) {
    const r = 52, c = 2 * Math.PI * r, dash = c * clamp(value, 0, 1);
    return '<svg viewBox="0 0 140 140" width="140" height="140">' +
      '<circle cx="70" cy="70" r="' + r + '" fill="none" stroke="#1c2740" stroke-width="10"/>' +
      '<circle cx="70" cy="70" r="' + r + '" fill="none" stroke="' + color + '" stroke-width="10" stroke-linecap="round" ' +
      'stroke-dasharray="' + dash + " " + c + '" transform="rotate(-90 70 70)"/>' +
      '<text x="70" y="66" text-anchor="middle" fill="#e8f4ff" font-size="18" font-family="ui-monospace,monospace">' + label + "</text>" +
      '<text x="70" y="86" text-anchor="middle" fill="#7f93b3" font-size="10">' + sub + "</text></svg>";
  }

  function piste(p, lo, hi) {
    return '<div class="estime" style="--p:' + p + ";--lo:" + lo + ";--hi:" + hi +
      '"><span class="estime-piste"></span><span class="estime-ci"></span><span class="estime-point"></span></div>';
  }

  function bodyMap() {
    const slots = { tete: { x: 60, y: 18 }, visage: { x: 60, y: 32 }, voix: { x: 60, y: 48 }, coeur: { x: 60, y: 78 }, souffle: { x: 86, y: 72 }, tache: { x: 28, y: 118 } };
    let dots = "";
    S.channels.forEach(function (c) {
      const s = slots[c.slot];
      if (!s) return;
      dots += '<circle cx="' + s.x + '" cy="' + s.y + '" r="' + (c.on ? 5 : 3.5) + '" fill="' + (c.on ? "#2dd4bf" : "#334155") + '" stroke="#050814"/>';
    });
    return '<svg class="body" viewBox="0 0 120 150" aria-label="Carte des langages">' +
      '<ellipse cx="60" cy="22" rx="14" ry="16" fill="none" stroke="#1c2a44"/>' +
      '<path d="M42 42 L60 50 L78 42 L84 110 L36 110 Z" fill="none" stroke="#1c2a44"/>' +
      '<path d="M36 110 L30 148 M84 110 L90 148" fill="none" stroke="#1c2a44"/>' + dots + "</svg>";
  }

  function currentEstimate() {
    const n = now();
    if (!n) return { n: null, est: null, k: null };
    const rel = related(S.selected);
    const est = n.estimates.filter(function (e) { return rel.has(e.id); })[0] ||
      n.estimates.filter(function (e) { return e.id === "i-charge"; })[0] || null;
    const k = S.onto.constructs.filter(function (c) { return c.id === (est && est.k); })[0] || null;
    return { n: n, est: est, k: k };
  }

  function drawLangs() {
    const root = document.getElementById("insp-langs");
    if (root.dataset.ready) {
      S.channels.forEach(function (c) {
        const lab = root.querySelector('label[data-ch="' + c.id + '"]');
        const inp = root.querySelector('input[data-ch="' + c.id + '"]');
        if (lab) lab.setAttribute("data-on", c.on ? "true" : "false");
        if (inp && document.activeElement !== inp) inp.checked = c.on;
      });
      return;
    }
    let html = '<div class="block"><p class="kicker">Langages</p><div class="langs">';
    S.channels.forEach(function (c) {
      html += '<label class="lang" data-ch="' + c.id + '" data-on="' + c.on + '"><input type="checkbox" data-ch="' + c.id + '"' +
        (c.on ? " checked" : "") + "> <span><strong>" + c.label + "</strong><small>" + c.slot + "</small></span></label>";
    });
    html += "</div></div>";
    root.innerHTML = html;
    root.dataset.ready = "1";
    root.querySelectorAll("input[data-ch]").forEach(function (inp) {
      inp.addEventListener("change", function () {
        const ch = S.channels.filter(function (c) { return c.id === inp.getAttribute("data-ch"); })[0];
        if (ch) ch.on = inp.checked;
        recomputeFrom(0);
        const body = document.getElementById("insp-body");
        body.innerHTML = '<div class="block"><p class="kicker">Carte des signes</p>' + bodyMap() +
          "<p>Allumé = collecté. Pas un jumeau mental.</p></div>";
        draw();
      });
    });
  }

  function drawInsp() {
    const pack = currentEstimate();
    const n = pack.n, est = pack.est, k = pack.k;
    if (!n) return;
    let html = '<div class="block"><p class="kicker">ConstructEstimate</p><h2>' + (k ? k.label : "Observation") + "</h2>";
    if (!est) html += "<p>Sélectionnez un nœud.</p>";
    else if (est.status === "refused") html += '<div class="refus">Refusal · ' + est.reason + " — le modèle n’invente pas.</div>";
    else {
      html += '<div class="row"><span>Estimation</span><b class="ci">' + pct(est.p) + " % · [" + pct(est.lo) + "–" + pct(est.hi) + "]</b></div>";
      html += piste(est.p, est.lo, est.hi);
      html += "<p>Preuves : " + (est.evid.join(", ") || "aucune") + ".</p>";
      html += '<div class="alts">Concurrentes : ' + est.alts.join(" · ") + "</div>";
    }
    html += "</div>";
    document.getElementById("insp-est").innerHTML = html;
    drawLangs();
    const body = document.getElementById("insp-body");
    if (!body.dataset.ready) {
      body.innerHTML = '<div class="block"><p class="kicker">Carte des signes</p>' + bodyMap() +
        "<p>Allumé = collecté. Pas un jumeau mental.</p></div>";
      body.dataset.ready = "1";
    }
    document.getElementById("insp-json").innerHTML =
      '<div class="block"><p class="kicker">Objet HCSM</p><pre class="json">' + JSON.stringify({
        construct: est && est.k,
        value: est && est.status === "estimated" ? Number(est.p.toFixed(2)) : null,
        uncertainty: est && est.status === "estimated" ? [Number(est.lo.toFixed(2)), Number(est.hi.toFixed(2))] : null,
        evidence_ids: est ? est.evid : [],
        temporal_window: "T0+" + n.t + "s",
        status: est ? est.status : "none",
        simulation: true,
        diagnostic_medical: false
      }, null, 2) + "</pre></div>";
  }

  function drawAccueil() {
    const n = now();
    if (!n) return;
    const on = S.channels.filter(function (c) { return c.on; }).length;
    const glob = n.estimates.filter(function (e) { return e.id === "i-charge"; })[0];
    document.getElementById("ring-cov").innerHTML = ringSVG(on / S.channels.length, on + "/" + S.channels.length, "langages", "#22d3ee");
    const conf = glob && glob.status === "estimated" ? glob.p : 0;
    const sub = glob && glob.status === "estimated" ? "[" + pct(glob.lo) + "–" + pct(glob.hi) + "]" : "refus";
    document.getElementById("ring-conf").innerHTML = ringSVG(conf, glob && glob.status === "estimated" ? pct(conf) + "%" : "—", "confiance " + sub, "#2dd4bf");
    drawConstellation(document.getElementById("graph-mini"), 640, 280);
    const cards = document.getElementById("est-cards");
    cards.replaceChildren();
    n.estimates.forEach(function (est) {
      const lab = S.onto.constructs.filter(function (k) { return k.id === est.k; })[0];
      const el = document.createElement("button");
      el.type = "button";
      el.className = "est-card";
      el.dataset.on = S.selected === est.id ? "true" : "false";
      el.innerHTML = "<div>" + (lab ? lab.label : est.id) + "</div><b>" +
        (est.status === "estimated" ? pct(est.p) + "% [" + pct(est.lo) + "–" + pct(est.hi) + "]" : "Refusal") + "</b>";
      el.addEventListener("click", function () { S.selected = est.id; draw(); });
      cards.appendChild(el);
    });
  }

  function drawCognition() {
    document.getElementById("cog-body").innerHTML = "<p class=\"kicker\">Langages</p>" + bodyMap() +
      "<p>Points cyan = collecté. Les lobes des illustrations Cognitorium ne sont pas des scores.</p>";
    const list = document.getElementById("cog-list");
    const n = now();
    let html = '<p class="kicker">Construits à T0</p>';
    n.estimates.forEach(function (est) {
      const lab = S.onto.constructs.filter(function (k) { return k.id === est.k; })[0];
      html += "<h2>" + (lab ? lab.label : est.id) + "</h2>";
      if (est.status === "estimated") {
        html += '<div class="row"><b class="ci">' + pct(est.p) + "% [" + pct(est.lo) + "–" + pct(est.hi) + "]</b></div>";
        html += piste(est.p, est.lo, est.hi);
      } else html += '<div class="refus">Refusal · ' + est.reason + "</div>";
    });
    list.innerHTML = html;
  }

  function showView(id) {
    S.view = id;
    document.querySelectorAll("[data-panel]").forEach(function (p) { p.hidden = p.getAttribute("data-panel") !== id; });
    document.querySelectorAll(".side nav button").forEach(function (b) {
      if (b.getAttribute("data-view") === id) b.setAttribute("aria-current", "page");
      else b.removeAttribute("aria-current");
    });
    const meta = VIEWS[id];
    document.getElementById("view-title").textContent = meta.titre;
    document.getElementById("view-sub").textContent = meta.sub;
  }

  function drawChrome() {
    const n = now();
    document.getElementById("clock").textContent = fmtT(n ? n.t : 0);
    const live = document.getElementById("live");
    live.dataset.on = S.playing ? "true" : "false";
    live.innerHTML = S.playing ? "<i></i> LIVE" : "<i></i> PAUSE";
    const btn = document.getElementById("btn-play");
    btn.textContent = S.playing ? "Pause" : "Lecture";
    ["scrub", "scrub-full"].forEach(function (id) {
      const el = document.getElementById(id);
      if (!el) return;
      el.max = String(Math.max(0, S.hist.length - 1));
      if (document.activeElement !== el) el.value = String(S.cursor);
    });
    document.getElementById("ctx").textContent = "sim-001 · bureau · " +
      S.channels.filter(function (c) { return c.on; }).length + " langages";
  }

  function draw() {
    drawChrome();
    drawConstellation(document.getElementById("graph"), 1100, 640);
    fillWaves(document.getElementById("waves"), 46);
    fillWaves(document.getElementById("waves-big"), 90);
    fanPath(document.getElementById("fan"), 520, 150);
    fanPath(document.getElementById("fan-full"), 1000, 280);
    drawInsp();
    if (S.view === "accueil") drawAccueil();
    if (S.view === "cognition") drawCognition();
  }

  function playLoop() {
    if (S.timer) clearInterval(S.timer);
    S.timer = setInterval(function () {
      if (!S.playing || document.hidden) return;
      tick();
    }, TICK_MS);
  }

  async function boot() {
    try {
      const r = await fetch("data/ontology.json", { cache: "no-store" });
      if (r.ok) S.onto = await r.json();
    } catch (e) { /* file:// */ }
    seedWalk();
    showView("univers");
    draw();
    playLoop();

    document.getElementById("btn-play").addEventListener("click", function () {
      S.playing = !S.playing;
      if (S.playing) S.cursor = S.hist.length - 1;
      drawChrome();
    });
    function bindScrub(id) {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("input", function (e) {
        S.playing = false;
        S.cursor = Number(e.target.value);
        draw();
      });
    }
    bindScrub("scrub");
    bindScrub("scrub-full");
    document.querySelectorAll("[data-layer]").forEach(function (b) {
      b.addEventListener("click", function () {
        const ly = b.getAttribute("data-layer");
        S.layers[ly] = !S.layers[ly];
        b.setAttribute("aria-pressed", S.layers[ly] ? "true" : "false");
        draw();
      });
    });
    document.querySelectorAll(".side nav [data-view]").forEach(function (b) {
      b.addEventListener("click", function () {
        showView(b.getAttribute("data-view"));
        draw();
      });
    });
    document.getElementById("q").addEventListener("input", function (e) {
      S.query = e.target.value.toLowerCase();
      draw();
    });
    document.addEventListener("keydown", function (e) {
      if (e.code !== "Space") return;
      const tag = e.target.tagName;
      if (tag === "INPUT" || tag === "BUTTON" || tag === "TEXTAREA" || tag === "A") return;
      e.preventDefault();
      S.playing = !S.playing;
      drawChrome();
    });
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
