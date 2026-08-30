/* Cognitorium Representation Engine
   Visualisation live · vues coordonnées · pas un générateur de code */

(function () {
  "use strict";

  const MAX = 180;
  const TICK_MS = 280;
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
    playing: true,
    cursor: 0,
    selected: "i-charge",
    layers: { K: true, E: true, I: true },
    onto: FALLBACK_ONTO,
    channels: [],
    hist: [],
    timer: null
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

  function infer(sample, on) {
    const load = clamp((sample.hr - 68) / 48, 0, 1);
    const err = clamp(sample.errors / 7, 0, 1);
    const time = clamp(sample.t / 900, 0, 1);
    const hrvLow = clamp(1 - sample.hrv, 0, 1);

    function est(kid, iid, base, evid, alts) {
      const active = evid.filter(function (e) { return on.has(e); });
      const ratio = evid.length ? active.length / evid.length : 0;
      if (ratio < 0.25) {
        return { id: iid, k: kid, status: "refused", reason: "NO_EVIDENCE", evid: active, alts: alts };
      }
      const p = clamp(base * (0.4 + 0.6 * ratio), 0.06, 0.9);
      const w = 0.1 + (1 - ratio) * 0.16;
      return {
        id: iid, k: kid, status: "estimated",
        p: p, lo: clamp(p - w, 0, 1), hi: clamp(p + w * 0.9, 0, 1),
        evid: active, alts: alts
      };
    }

    return [
      est("k-charge", "i-charge", 0.28 + 0.32 * load + 0.18 * err + 0.14 * time + 0.12 * hrvLow,
        ["e-hr", "e-hrv", "e-temps", "e-erreurs"],
        ["effort", "excitation", "difficulté de tâche"]),
      est("k-activation", "i-activation", 0.22 + 0.55 * load + 0.1 * hrvLow,
        ["e-hr", "e-hrv"],
        ["effort physique", "stress", "déplacement"]),
      est("k-frustration", "i-frustration", 0.12 + 0.55 * err + 0.18 * time,
        ["e-erreurs", "e-temps"],
        ["charge", "consigne ambiguë"]),
      est("k-effort", "i-effort", 0.08 + 0.25 * load,
        ["e-hr"],
        ["activation", "posture"])
    ];
  }

  function seedWalk() {
    S.channels = S.onto.channels.map(function (c) { return Object.assign({}, c); });
    S.hist = [];
    let hr = 86, hrv = 0.62, errors = 0;
    for (let t = 0; t <= 42; t++) {
      hr += (Math.random() - 0.48) * 1.8 + 0.04 * (90 - hr);
      hr = clamp(hr, 72, 112);
      hrv += (Math.random() - 0.5) * 0.04 + 0.02 * (0.55 - hrv);
      hrv = clamp(hrv, 0.25, 0.9);
      if (Math.random() < 0.07) errors += 1;
      const sample = { t: t, hr: hr, hrv: hrv, temps: t, errors: errors };
      sample.estimates = infer(sample, onSet());
      S.hist.push(sample);
    }
    S.cursor = S.hist.length - 1;
  }

  function tick() {
    const last = S.hist[S.hist.length - 1];
    const t = last.t + 1;
    let hr = last.hr + (Math.random() - 0.48) * 1.7 + 0.03 * (91 - last.hr);
    hr = clamp(hr, 72, 114);
    let hrv = clamp(last.hrv + (Math.random() - 0.5) * 0.035, 0.22, 0.92);
    let errors = last.errors + (Math.random() < 0.06 ? 1 : 0);
    const sample = { t: t, hr: hr, hrv: hrv, temps: t, errors: errors };
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
      if (est.evid.indexOf(id) >= 0) {
        set.add(est.id); set.add(est.k);
      }
    });
    return set;
  }

  function layout() {
    const K = S.onto.constructs;
    const E = S.channels;
    const I = (now() && now().estimates) || [];
    const pos = {};
    function spread(list, y, key) {
      const n = list.length;
      list.forEach(function (item, i) {
        const x = 90 + (n === 1 ? 410 : i * 820 / (n - 1));
        pos[key(item)] = { x: x, y: y };
      });
    }
    spread(K, 88, function (k) { return k.id; });
    spread(I, 278, function (e) { return e.id; });
    spread(E, 500, function (c) { return c.id; });
    return pos;
  }

  function drawGraph() {
    const svg = document.getElementById("graph");
    const n = now();
    if (!n) return;
    const pos = layout();
    const rel = related(S.selected);
    const show = S.layers;
    let edges = "";
    n.estimates.forEach(function (est) {
      const pI = pos[est.id], pK = pos[est.k];
      if (pI && pK && show.K && show.I) {
        const hot = rel.has(est.id) || rel.has(est.k);
        edges += '<path class="edge I' + (hot ? " on" : "") + '" d="M' + pK.x + " " + pK.y + " L" + pI.x + " " + pI.y + '"/>';
      }
      if (show.E && show.I && pI) {
        est.evid.forEach(function (eid) {
          const pE = pos[eid];
          if (!pE) return;
          const hot = rel.has(est.id) || rel.has(eid);
          edges += '<path class="edge E' + (hot ? " on" : "") + '" d="M' + pE.x + " " + pE.y + " L" + pI.x + " " + pI.y + '"/>';
        });
      }
    });

    function node(id, label, layer, extra) {
      if (!show[layer] || !pos[id]) return "";
      const p = pos[id];
      const hot = rel.has(id);
      const col = layer === "K" ? "#8db4ff" : layer === "E" ? "#2dd4bf" : "#e4b15a";
      const refused = extra && extra.status === "refused";
      const off = extra && extra.off;
      const stroke = refused ? "#fb7185" : off ? "#3a4660" : col;
      const fill = hot ? stroke : "#0b1020";
      const dash = layer === "I" || off || refused ? " stroke-dasharray=\"4 3\"" : "";
      const r = hot ? 16 : 13;
      return '<g class="node" data-id="' + id + '">' +
        '<circle cx="' + p.x + '" cy="' + p.y + '" r="' + r + '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="2"' + dash + '/>' +
        '<text x="' + p.x + '" y="' + (p.y + 28) + '" text-anchor="middle">' + label + "</text></g>";
    }

    let nodes = "";
    S.onto.constructs.forEach(function (k) { nodes += node(k.id, k.label, "K"); });
    n.estimates.forEach(function (est) {
      const lab = S.onto.constructs.filter(function (k) { return k.id === est.k; })[0];
      nodes += node(est.id, (lab ? lab.label : est.id) + (est.status === "refused" ? " · refus" : ""), "I", est);
    });
    S.channels.forEach(function (c) {
      nodes += node(c.id, c.label + (c.on ? "" : " · off"), "E", { off: !c.on });
    });

    svg.innerHTML =
      '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>' +
      '<text x="24" y="36" fill="#8ea2c9" font-size="11" letter-spacing="2">KNOWLEDGE</text>' +
      '<text x="24" y="226" fill="#8ea2c9" font-size="11" letter-spacing="2">INFERENCE</text>' +
      '<text x="24" y="448" fill="#8ea2c9" font-size="11" letter-spacing="2">EVIDENCE</text>' +
      edges + nodes;

    svg.querySelectorAll(".node").forEach(function (g) {
      g.addEventListener("click", function (ev) {
        ev.stopPropagation();
        S.selected = g.getAttribute("data-id");
        draw();
      });
    });
  }

  function spark(arr, w, h, color) {
    if (!arr.length) return "";
    const min = Math.min.apply(null, arr);
    const max = Math.max.apply(null, arr);
    const span = max - min || 1;
    let d = "";
    arr.forEach(function (v, i) {
      const x = arr.length === 1 ? 0 : i * (w - 4) / (arr.length - 1);
      const y = h - 4 - ((v - min) / span) * (h - 8);
      d += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1) + " ";
    });
    return '<path d="' + d + '" fill="none" stroke="' + color + '" stroke-width="1.6"/>';
  }

  function drawWaves() {
    const root = document.getElementById("waves");
    const keys = [
      { id: "e-hr", key: "hr", label: "FC", unit: "bpm" },
      { id: "e-hrv", key: "hrv", label: "HRV", unit: "" },
      { id: "e-temps", key: "temps", label: "Temps", unit: "s" },
      { id: "e-erreurs", key: "errors", label: "Erreurs", unit: "" }
    ];
    const rel = related(S.selected);
    root.replaceChildren();
    keys.forEach(function (k) {
      const ch = S.channels.filter(function (c) { return c.id === k.id; })[0];
      const on = ch && ch.on;
      const series = on ? S.hist.slice(0, S.cursor + 1).map(function (s) { return s[k.key]; }) : [];
      const last = series.length ? series[series.length - 1] : null;
      const box = document.createElement("div");
      box.className = "wave";
      box.dataset.sel = rel.has(k.id) ? "true" : "false";
      const val = last == null ? "off" : (k.key === "hrv" ? last.toFixed(2) : String(Math.round(last * 10) / 10));
      box.innerHTML = '<div class="meta"><span>' + k.label + '</span><b>' + val + (on && k.unit ? " " + k.unit : "") + "</b></div>" +
        '<svg viewBox="0 0 200 54">' + (on ? spark(series, 200, 54, "#2dd4bf") : "") + "</svg>";
      box.addEventListener("click", function () { S.selected = k.id; draw(); });
      root.appendChild(box);
    });
  }

  function drawFan() {
    const svg = document.getElementById("fan");
    const title = document.getElementById("fan-title");
    let iid = "i-charge";
    if (S.selected && S.selected.indexOf("i-") === 0) iid = S.selected;
    else if (S.selected && S.selected.indexOf("k-") === 0) iid = "i-" + S.selected.slice(2);
    const lab = S.onto.constructs.filter(function (k) { return "i-" + k.id.slice(2) === iid; })[0];
    title.textContent = (lab ? lab.label : "Estimation") + " · fan chart";
    const slice = S.hist.slice(0, S.cursor + 1);
    const pts = slice.map(function (s) {
      const est = s.estimates.filter(function (e) { return e.id === iid; })[0];
      if (!est || est.status !== "estimated") return { y: null, lo: 0, hi: 1 };
      return { y: est.p, lo: est.lo, hi: est.hi };
    });
    const w = 520, h = 170, pl = 28, pr = 8, pt = 10, pb = 18;
    const iw = w - pl - pr, ih = h - pt - pb;
    const x = function (i) { return pl + (pts.length < 2 ? iw / 2 : i * iw / (pts.length - 1)); };
    const y = function (v) { return pt + (1 - v) * ih; };
    let band = "", line = "";
    const ok = [];
    pts.forEach(function (p, i) { if (p.y != null) ok.push({ i: i, p: p }); });
    if (!ok.length) {
      svg.innerHTML = '<text x="28" y="90" fill="#8ea2c9" font-size="12">Refus d’estimer — preuves insuffisantes.</text>';
      return;
    }
    ok.forEach(function (o, n) {
      band += (n ? "L" : "M") + x(o.i).toFixed(1) + " " + y(o.p.hi).toFixed(1) + " ";
    });
    for (let n = ok.length - 1; n >= 0; n--) {
      band += "L" + x(ok[n].i).toFixed(1) + " " + y(ok[n].p.lo).toFixed(1) + " ";
    }
    band += "Z";
    ok.forEach(function (o, n) {
      line += (n ? "L" : "M") + x(o.i).toFixed(1) + " " + y(o.p.y).toFixed(1) + " ";
    });
    svg.innerHTML =
      '<defs><pattern id="hach" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">' +
      '<line x1="0" y1="0" x2="0" y2="6" stroke="rgb(228 177 90 / 0.5)" stroke-width="2"/></pattern></defs>' +
      '<line x1="' + pl + '" x2="' + (w - pr) + '" y1="' + y(0.5).toFixed(1) + '" y2="' + y(0.5).toFixed(1) + '" stroke="#263352" stroke-dasharray="3 4"/>' +
      '<path d="' + band + '" fill="url(#hach)"/>' +
      '<path d="' + line + '" fill="none" stroke="#2dd4bf" stroke-width="2"/>';
  }

  function piste(p, lo, hi) {
    return '<div class="estime" style="--p:' + p + ";--lo:" + lo + ";--hi:" + hi +
      '"><span class="estime-piste"></span><span class="estime-ci"></span><span class="estime-point"></span></div>';
  }

  function bodyMap() {
    const slots = {
      tete: { x: 60, y: 18 },
      visage: { x: 60, y: 32 },
      voix: { x: 60, y: 48 },
      coeur: { x: 60, y: 78 },
      souffle: { x: 86, y: 72 },
      tache: { x: 28, y: 118 }
    };
    let dots = "";
    S.channels.forEach(function (c) {
      const s = slots[c.slot];
      if (!s) return;
      const col = c.on ? "#2dd4bf" : "#3a4660";
      dots += '<circle cx="' + s.x + '" cy="' + s.y + '" r="' + (c.on ? 5 : 3.5) + '" fill="' + col + '" stroke="#0b1020" stroke-width="1"/>';
    });
    return '<svg class="body" viewBox="0 0 120 150" aria-label="Carte des langages">' +
      '<ellipse cx="60" cy="22" rx="14" ry="16" fill="none" stroke="#263352"/>' +
      '<path d="M42 42 L60 50 L78 42 L84 110 L36 110 Z" fill="none" stroke="#263352"/>' +
      '<path d="M36 110 L30 148 M84 110 L90 148" fill="none" stroke="#263352"/>' +
      dots + "</svg>";
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
    let html = '<div class="block"><p class="kicker">Langages · minimisation</p><div class="langs">';
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
        drawLangs();
        document.getElementById("insp-body").innerHTML =
          '<div class="block"><p class="kicker">Carte des signes</p>' + bodyMap() +
          "<p>Points allumés = collecté. Ce n’est pas un jumeau mental.</p></div>";
        draw();
      });
    });
  }

  function drawInsp() {
    const { n, est, k } = currentEstimate();
    if (!n) return;
    const estRoot = document.getElementById("insp-est");
    let html = '<div class="block"><p class="kicker">Inspecteur · ConstructEstimate</p>';
    html += "<h2>" + (k ? k.label : "Observation") + "</h2>";
    if (!est) {
      html += "<p>Sélectionnez un nœud.</p>";
    } else if (est.status === "refused") {
      html += '<div class="refus">Refusal · ' + est.reason + " — le modèle n’invente pas. Rallumez une modalité nécessaire, ou acceptez le silence.</div>";
    } else {
      html += '<div class="row"><span>Estimation</span><b class="ci">' + pct(est.p) + " % · [" + pct(est.lo) + "–" + pct(est.hi) + "]</b></div>";
      html += piste(est.p, est.lo, est.hi);
      html += "<p>Preuves : " + (est.evid.join(", ") || "aucune") + ".</p>";
      html += '<div class="alts">Hypothèses concurrentes : ' + est.alts.join(" · ") + "</div>";
    }
    html += "</div>";
    estRoot.innerHTML = html;

    drawLangs();

    const body = document.getElementById("insp-body");
    if (!body.dataset.ready) {
      body.innerHTML = '<div class="block"><p class="kicker">Carte des signes</p>' + bodyMap() +
        "<p>Points allumés = collecté. Ce n’est pas un jumeau mental.</p></div>";
      body.dataset.ready = "1";
    }

    const obj = {
      construct: est && est.k,
      value: est && est.status === "estimated" ? Number(est.p.toFixed(2)) : null,
      uncertainty: est && est.status === "estimated" ? { lo: Number(est.lo.toFixed(2)), hi: Number(est.hi.toFixed(2)) } : null,
      evidence_ids: est ? est.evid : [],
      temporal_window: { center: "T0+" + n.t + "s", half_width: "1s" },
      status: est ? est.status : "none",
      simulation: true,
      diagnostic_medical: false
    };
    document.getElementById("insp-json").innerHTML =
      '<div class="block"><p class="kicker">Objet HCSM</p><pre class="json">' +
      JSON.stringify(obj, null, 2) + "</pre></div>";
  }

  function drawChrome() {
    const n = now();
    document.getElementById("clock").textContent = fmtT(n ? n.t : 0);
    const live = document.getElementById("live");
    live.dataset.on = S.playing ? "true" : "false";
    live.innerHTML = S.playing ? "<i></i> DIRECT · simulé" : "<i></i> PAUSE";
    const btn = document.getElementById("btn-play");
    btn.textContent = S.playing ? "Pause" : "Lecture";
    btn.setAttribute("aria-pressed", S.playing ? "true" : "false");
    const scrub = document.getElementById("scrub");
    scrub.max = String(Math.max(0, S.hist.length - 1));
    if (document.activeElement !== scrub) scrub.value = String(S.cursor);
    document.getElementById("ctx").textContent =
      "Résolution d’un problème · bureau · sim-001 · " +
      S.channels.filter(function (c) { return c.on; }).length + " langages";
  }

  function draw() {
    drawChrome();
    drawGraph();
    drawWaves();
    drawFan();
    drawInsp();
  }

  function playLoop() {
    if (S.timer) clearInterval(S.timer);
    S.timer = setInterval(function () {
      if (!S.playing) return;
      if (document.hidden) return;
      tick();
    }, TICK_MS);
  }

  async function boot() {
    try {
      const r = await fetch("data/ontology.json", { cache: "no-store" });
      if (r.ok) S.onto = await r.json();
    } catch (e) { /* file:// */ }
    seedWalk();
    draw();
    playLoop();

    document.getElementById("btn-play").addEventListener("click", function () {
      S.playing = !S.playing;
      if (S.playing) S.cursor = S.hist.length - 1;
      drawChrome();
    });
    document.getElementById("scrub").addEventListener("input", function (e) {
      S.playing = false;
      S.cursor = Number(e.target.value);
      draw();
    });
    document.querySelectorAll(".rail [data-layer]").forEach(function (b) {
      b.addEventListener("click", function () {
        const ly = b.getAttribute("data-layer");
        S.layers[ly] = !S.layers[ly];
        b.setAttribute("aria-pressed", S.layers[ly] ? "true" : "false");
        drawGraph();
      });
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
