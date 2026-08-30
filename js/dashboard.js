/* Language Decoder — prototype.
   Les inférences restent des hypothèses. Aucune donnée n'est persistée. */

(function () {
  "use strict";

  const FALLBACK = {
    meta: { type: "simulation", horodatage: "2026-08-30T21:07:00Z", diagnostic_medical: false },
    individu: {
      id: "sim-001",
      anonyme: true,
      ligne_de_base: { frequence_cardiaque_repos: 68, unite: "bpm" }
    },
    contexte: {
      cas: "résolution d'un problème",
      environnement: "bureau, travail individuel",
      duree_tache_min: 14
    },
    langages: [
      { id: "cardio_features", label: "Cardio (caractéristiques)", categorie: "physiologique", collecte: true, necessaire: true, justification: "Écart à la ligne de base, pas le tracé ECG." },
      { id: "comportement_tache", label: "Comportement de tâche", categorie: "comportemental", collecte: true, necessaire: true, justification: "Durée, erreurs, pauses — déjà produites par l'interface." },
      { id: "respiration", label: "Respiration", categorie: "physiologique", collecte: false, necessaire: false, justification: "Non nécessaire pour ce cas d'étude." },
      { id: "eeg_bci", label: "EEG / BCI", categorie: "neurophysiologique", collecte: false, necessaire: false, justification: "Signal sensible, hors finalité actuelle." },
      { id: "parole_audio", label: "Parole (audio)", categorie: "langagier", collecte: false, necessaire: false, justification: "Enregistrement vocal non requis." },
      { id: "video_visage", label: "Vidéo / visage", categorie: "comportemental", collecte: false, necessaire: false, justification: "Biométrie forte, écartée par minimisation." }
    ],
    signaux: {
      frequence_cardiaque: { valeur: 92, unite: "bpm", vs_baseline: "elevee", ecart_bpm: 24, qualite: 0.86, langue: "cardio_features", label: "Fréquence cardiaque" },
      variabilite_cardiaque: { valeur: "diminution relative", unite: null, vs_baseline: "diminution", qualite: 0.74, langue: "cardio_features", label: "Variabilité cardiaque" },
      temps_sur_tache: { valeur: 14, unite: "min", qualite: 1, langue: "comportement_tache", label: "Temps sur tâche" },
      erreurs_recentes: { valeur: 3, unite: "count", qualite: 1, langue: "comportement_tache", label: "Erreurs récentes" }
    },
    hypotheses: [
      { id: "charge_cognitive", etat: "charge cognitive élevée", confiance: 0.68, intervalle: [0.52, 0.79], preuves: ["frequence_cardiaque", "variabilite_cardiaque", "temps_sur_tache", "erreurs_recentes"] },
      { id: "frustration", etat: "frustration possible", confiance: 0.42, intervalle: [0.21, 0.58], preuves: ["erreurs_recentes", "temps_sur_tache"] },
      { id: "activation", etat: "activation physiologique modérée", confiance: 0.57, intervalle: [0.38, 0.71], preuves: ["frequence_cardiaque", "variabilite_cardiaque"] },
      { id: "effort_physique", etat: "effort physique", confiance: 0.18, intervalle: [0.05, 0.31], preuves: ["frequence_cardiaque"] }
    ],
    confiance_globale: { valeur: 0.72, intervalle: [0.58, 0.81] },
    alternatives: ["effort physique", "excitation", "stress", "peur", "douleur", "simple déplacement"],
    timeline: [
      { id: "T1", label: "T1", charge: 0.42, lo: 0.28, hi: 0.55 },
      { id: "T2", label: "T2", charge: 0.55, lo: 0.4, hi: 0.68 },
      { id: "T3", label: "T3", charge: 0.68, lo: 0.52, hi: 0.79 },
      { id: "T4", label: "T4", charge: 0.72, lo: 0.54, hi: 0.84 },
      { id: "now", label: "Maintenant", charge: 0.68, lo: 0.52, hi: 0.79 }
    ],
    action_interface: {
      titre: "Proposer une aide progressive",
      detail: "Réduire la densité d'information, fractionner la tâche, laisser le choix à l'utilisateur.",
      declencheurs: [
        "charge cognitive probable en hausse",
        "trois erreurs récentes",
        "temps sur tâche allongé par rapport au début"
      ],
      proprietes: ["explicable", "réversible", "contrôle utilisateur"]
    }
  };

  const SIGNALS_META = {
    frequence_cardiaque: { label: "Fréquence cardiaque" },
    variabilite_cardiaque: { label: "Variabilité cardiaque" },
    temps_sur_tache: { label: "Temps sur tâche" },
    erreurs_recentes: { label: "Erreurs récentes" }
  };

  const etat = {
    data: null,
    avis: {},
    action: null
  };

  function pct(x) {
    return Math.round(x * 100);
  }

  function clamp(x, a, b) {
    return Math.max(a, Math.min(b, x));
  }

  function languesActives() {
    return new Set(etat.data.langages.filter(function (l) { return l.collecte; }).map(function (l) { return l.id; }));
  }

  function hypothesesCalculees() {
    const actives = languesActives();
    return etat.data.hypotheses.map(function (h) {
      const preuves = h.preuves || [];
      let total = 0;
      let on = 0;
      preuves.forEach(function (id) {
        const s = etat.data.signaux[id];
        if (!s) return;
        total += 1;
        if (actives.has(s.langue)) on += 1;
      });
      const ratio = total ? on / total : 0;
      const avis = etat.avis[h.id];
      let facteur = 0.3 + 0.7 * ratio;
      let widen = (1 - ratio) * 0.16;
      if (avis === "non") {
        facteur *= 0.28;
        widen += 0.08;
      } else if (avis === "oui") {
        facteur = clamp(facteur * 1.08, 0, 1);
      } else if (avis === "nsp") {
        widen += 0.1;
        facteur *= 0.9;
      }
      const p = clamp(h.confiance * facteur, 0.04, 0.95);
      const lo = clamp(h.intervalle[0] * facteur - widen * 0.25, 0, p);
      const hi = clamp(h.intervalle[1] * facteur + widen, p, 1);
      return {
        id: h.id,
        etat: h.etat,
        p: p,
        lo: lo,
        hi: hi,
        preuves: preuves.filter(function (id) {
          const s = etat.data.signaux[id];
          return s && actives.has(s.langue);
        }),
        ratio: ratio,
        avis: avis || null
      };
    }).sort(function (a, b) { return b.p - a.p; });
  }

  function confianceGlobale(hyps) {
    const actives = languesActives();
    const utiles = etat.data.langages.filter(function (l) { return l.necessaire; });
    const n = utiles.filter(function (l) { return actives.has(l.id); }).length;
    const couverture = utiles.length ? n / utiles.length : 0;
    const avisNon = Object.keys(etat.avis).filter(function (k) { return etat.avis[k] === "non"; }).length;
    const base = etat.data.confiance_globale.valeur * (0.45 + 0.55 * couverture);
    const p = clamp(base - avisNon * 0.08, 0.12, 0.9);
    const widen = (1 - couverture) * 0.14 + avisNon * 0.04;
    return {
      p: p,
      lo: clamp(etat.data.confiance_globale.intervalle[0] * (0.5 + 0.5 * couverture) - widen, 0, p),
      hi: clamp(etat.data.confiance_globale.intervalle[1] + widen, p, 1),
      couverture: couverture
    };
  }

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "class") node.className = attrs[k];
        else if (k === "html") node.innerHTML = attrs[k];
        else if (k.indexOf("on") === 0) node.addEventListener(k.slice(2), attrs[k]);
        else if (attrs[k] !== null && attrs[k] !== undefined) node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function piste(p, lo, hi, label) {
    const wrap = el("div", {
      class: "estime",
      role: "img",
      "aria-label": label
    });
    wrap.style.setProperty("--p", String(p));
    wrap.style.setProperty("--lo", String(lo));
    wrap.style.setProperty("--hi", String(hi));
    wrap.appendChild(el("span", { class: "estime-piste" }));
    wrap.appendChild(el("span", { class: "estime-ci" }));
    wrap.appendChild(el("span", { class: "estime-point" }));
    return wrap;
  }

  function dots(q) {
    const n = 5;
    const on = Math.round(q * n);
    const box = el("span", { class: "qualite", "aria-label": "Qualité " + pct(q) + " %" });
    for (let i = 0; i < n; i++) {
      box.appendChild(el("i", { class: i < on ? "on" : "" }));
    }
    return box;
  }

  function renderLangages() {
    const root = document.getElementById("langages");
    if (!root.dataset.ready) {
      etat.data.langages.forEach(function (l) {
        const id = "lg-" + l.id;
        const label = el("label", { class: "langue", "data-on": l.collecte ? "true" : "false", for: id });
        const input = el("input", { type: "checkbox", id: id });
        input.checked = !!l.collecte;
        input.addEventListener("change", function () {
          l.collecte = input.checked;
          render();
        });
        label.appendChild(input);
        label.appendChild(el("span", null, [
          el("strong", null, [l.label]),
          el("small", null, [l.categorie + " · " + l.justification])
        ]));
        root.appendChild(label);
      });
      root.dataset.ready = "1";
    } else {
      etat.data.langages.forEach(function (l) {
        const label = root.querySelector('label[for="lg-' + l.id + '"]');
        const input = document.getElementById("lg-" + l.id);
        if (label) label.setAttribute("data-on", l.collecte ? "true" : "false");
        if (input) input.checked = !!l.collecte;
      });
    }
    const n = etat.data.langages.filter(function (l) { return l.collecte; }).length;
    document.getElementById("langages-note").textContent =
      n + " modalité" + (n > 1 ? "s" : "") + " active" + (n > 1 ? "s" : "") +
      " · les autres restent hors collecte (minimisation).";
  }

  function fmtSignal(id, s) {
    if (id === "frequence_cardiaque") {
      return s.valeur + " bpm · +" + s.ecart_bpm + " vs repos " +
        etat.data.individu.ligne_de_base.frequence_cardiaque_repos;
    }
    if (id === "variabilite_cardiaque") return "↓ relative à la ligne de base";
    if (id === "temps_sur_tache") return s.valeur + " min";
    if (id === "erreurs_recentes") return String(s.valeur);
    return String(s.valeur);
  }

  function renderSignaux() {
    const root = document.getElementById("signaux");
    root.replaceChildren();
    const actives = languesActives();
    let n = 0;
    Object.keys(etat.data.signaux).forEach(function (id) {
      const s = etat.data.signaux[id];
      const meta = SIGNALS_META[id] || { label: id };
      const on = actives.has(s.langue);
      const row = el("div", { class: "row" });
      const left = el("span", null, [meta.label]);
      if (!on) {
        row.appendChild(left);
        row.appendChild(el("b", null, ["non collecté"]));
        root.appendChild(row);
        return;
      }
      n += 1;
      const right = el("span", { style: "display:flex;gap:10px;align-items:center;text-align:right" }, [
        dots(s.qualite),
        el("b", null, [fmtSignal(id, s)])
      ]);
      row.appendChild(left);
      row.appendChild(right);
      root.appendChild(row);
    });
    if (n === 0) {
      root.appendChild(el("p", { class: "note" }, [
        "Aucune mesure : les hypothèses ci-contre deviennent très larges. C’est le comportement attendu de la minimisation."
      ]));
    } else {
      root.appendChild(el("p", { class: "note" }, [
        "Aucun tracé brut. Qualité = fiabilité d’acquisition simulée, pas une preuve d’émotion."
      ]));
    }
  }

  function renderHypotheses() {
    const hyps = hypothesesCalculees();
    const glob = confianceGlobale(hyps);
    const root = document.getElementById("hypotheses");
    root.replaceChildren();

    const g = el("article", { class: "hypothese" });
    g.appendChild(el("header", null, [
      el("h3", null, ["Confiance globale du modèle"]),
      el("span", { class: "ci" }, [pct(glob.p) + " % · [" + pct(glob.lo) + "–" + pct(glob.hi) + "]"])
    ]));
    g.appendChild(piste(glob.p, glob.lo, glob.hi,
      "Confiance globale " + pct(glob.p) + " pour cent, intervalle " + pct(glob.lo) + " à " + pct(glob.hi)));
    g.appendChild(el("p", { class: "note" }, [
      "Confiance sur la représentation, pas une certitude intérieure. Couverture des modalités nécessaires : " +
        pct(glob.couverture) + " %."
    ]));
    root.appendChild(g);

    hyps.forEach(function (h) {
      const art = el("article", { class: "hypothese", "data-id": h.id });
      art.appendChild(el("header", null, [
        el("h3", null, [h.etat]),
        el("span", { class: "ci" }, [pct(h.p) + " % · [" + pct(h.lo) + "–" + pct(h.hi) + "]"])
      ]));
      art.appendChild(piste(h.p, h.lo, h.hi,
        h.etat + " " + pct(h.p) + " pour cent, intervalle " + pct(h.lo) + " à " + pct(h.hi)));
      const preuves = h.preuves.length
        ? "Preuves : " + h.preuves.map(function (id) { return (SIGNALS_META[id] || { label: id }).label; }).join(", ") + "."
        : "Aucune preuve active — données insuffisantes.";
      art.appendChild(el("p", { class: "note" }, [preuves]));
      const avis = el("div", { class: "avis", role: "group", "aria-label": "Corriger " + h.etat });
      [
        ["oui", "Ceci correspond"],
        ["non", "Ceci ne correspond pas"],
        ["nsp", "Je ne sais pas"]
      ].forEach(function (pair) {
        const btn = el("button", {
          type: "button",
          "aria-pressed": h.avis === pair[0] ? "true" : "false"
        }, [pair[1]]);
        btn.addEventListener("click", function () {
          if (etat.avis[h.id] === pair[0]) delete etat.avis[h.id];
          else etat.avis[h.id] = pair[0];
          render();
        });
        avis.appendChild(btn);
      });
      art.appendChild(avis);
      root.appendChild(art);
    });

    document.getElementById("alternatives").innerHTML =
      "<strong>Le même signal cardiaque peut aussi indiquer</strong>" +
      etat.data.alternatives.join(" · ") +
      ". D’où l’intervalle, pas une émotion unique.";
  }

  function extraWiden() {
    const glob = confianceGlobale(hypothesesCalculees());
    return (1 - glob.couverture) * 0.12;
  }

  function renderChart() {
    const widen = extraWiden();
    const pts = etat.data.timeline.map(function (t) {
      return {
        label: t.label,
        y: t.charge,
        lo: clamp(t.lo - widen, 0, 1),
        hi: clamp(t.hi + widen, 0, 1)
      };
    });
    const w = 640;
    const h = 176;
    const pad = { l: 36, r: 12, t: 14, b: 28 };
    const innerW = w - pad.l - pad.r;
    const innerH = h - pad.t - pad.b;
    const x = function (i) { return pad.l + (pts.length === 1 ? innerW / 2 : i * innerW / (pts.length - 1)); };
    const y = function (v) { return pad.t + (1 - v) * innerH; };

    let band = "";
    pts.forEach(function (p, i) {
      band += (i === 0 ? "M" : "L") + x(i).toFixed(1) + " " + y(p.hi).toFixed(1) + " ";
    });
    for (let i = pts.length - 1; i >= 0; i--) {
      band += "L" + x(i).toFixed(1) + " " + y(pts[i].lo).toFixed(1) + " ";
    }
    band += "Z";

    let line = "";
    pts.forEach(function (p, i) {
      line += (i === 0 ? "M" : "L") + x(i).toFixed(1) + " " + y(p.y).toFixed(1) + " ";
    });

    const grid = [0, 0.5, 1].map(function (v) {
      const yy = y(v).toFixed(1);
      return '<line x1="' + pad.l + '" x2="' + (w - pad.r) + '" y1="' + yy + '" y2="' + yy +
        '" stroke="#d7cfc0" stroke-dasharray="3 4"/>' +
        '<text x="4" y="' + (Number(yy) + 4) + '" fill="#5e584f" font-size="10" font-family="ui-monospace, monospace">' +
        Math.round(v * 100) + '</text>';
    }).join("");

    const dotsSvg = pts.map(function (p, i) {
      return '<circle cx="' + x(i).toFixed(1) + '" cy="' + y(p.y).toFixed(1) +
        '" r="4" fill="#1c1914" stroke="#fcfaf4" stroke-width="2"/>';
    }).join("");

    const svg =
      '<svg viewBox="0 0 ' + w + ' ' + h + '" role="img" aria-label="Charge cognitive estimée dans le temps, avec bande d’incertitude">' +
      '<defs><pattern id="hachure" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">' +
      '<line x1="0" y1="0" x2="0" y2="6" stroke="rgb(141 90 26 / 0.45)" stroke-width="2"/></pattern></defs>' +
      grid +
      '<path d="' + band + '" fill="url(#hachure)" opacity="0.9"/>' +
      '<path d="' + line + '" fill="none" stroke="#1f4f4a" stroke-width="2"/>' +
      dotsSvg +
      "</svg>";

    document.getElementById("chart").innerHTML = svg;

    const ticks = document.getElementById("ticks");
    ticks.replaceChildren();
    pts.forEach(function (p) {
      const d = el("div", { class: "tick" }, [
        el("b", null, [p.label]),
        el("span", null, [pct(p.y) + " % · [" + pct(p.lo) + "–" + pct(p.hi) + "]"])
      ]);
      ticks.appendChild(d);
    });
  }

  function renderAction() {
    const root = document.getElementById("action");
    root.replaceChildren();
    const hyps = hypothesesCalculees();
    const glob = confianceGlobale(hyps);
    const a = etat.data.action_interface;
    const tropPeu = glob.couverture < 0.4;

    if (tropPeu) {
      root.appendChild(el("p", null, [
        "Données insuffisantes pour proposer une adaptation. Le système n’agit pas par défaut — c’est volontaire."
      ]));
      return;
    }

    root.appendChild(el("p", null, [
      el("strong", { style: "color:var(--ink)" }, [a.titre])
    ]));
    root.appendChild(el("p", null, [a.detail]));
    const labels = {
      explicable: "explicable",
      reversible: "réversible",
      controle_utilisateur: "contrôle utilisateur"
    };
    const pills = el("div", { class: "pills" });
    a.proprietes.forEach(function (p) {
      pills.appendChild(el("span", { class: "pill" }, [labels[p] || p]));
    });
    root.appendChild(pills);
    const ul = el("ul", { class: "declencheurs" });
    a.declencheurs.forEach(function (d) { ul.appendChild(el("li", null, [d])); });
    root.appendChild(ul);

    const actions = el("div", { class: "actions" });
    [
      ["accepter", "Accepter l’aide", true],
      ["autre", "Autre suggestion", false],
      ["ignorer", "Ignorer", false]
    ].forEach(function (item) {
      const btn = el("button", {
        type: "button",
        class: item[2] ? "primary" : "",
        "aria-pressed": etat.action === item[0] ? "true" : "false"
      }, [item[1]]);
      btn.addEventListener("click", function () {
        etat.action = item[0];
        render();
      });
      actions.appendChild(btn);
    });
    root.appendChild(actions);

    if (etat.action === "accepter") {
      root.appendChild(el("p", { class: "status" }, ["Aide proposée, réversible. Rien n’a été imposé."]));
    } else if (etat.action === "autre") {
      root.appendChild(el("p", { class: "status" }, ["Alternative : fractionner uniquement la prochaine étape, sans extraire d’autre signal."]));
    } else if (etat.action === "ignorer") {
      root.appendChild(el("p", { class: "status" }, ["Adaptation ignorée. Le modèle reste une suggestion."]));
    }
  }

  function representation() {
    const actives = languesActives();
    const signaux = {};
    Object.keys(etat.data.signaux).forEach(function (id) {
      const s = etat.data.signaux[id];
      if (!actives.has(s.langue)) return;
      if (id === "frequence_cardiaque") signaux[id] = "élevée vs baseline";
      else if (id === "variabilite_cardiaque") signaux[id] = "diminuée";
      else if (id === "temps_sur_tache") signaux[id] = "long";
      else signaux[id] = s.valeur;
    });
    const hyps = hypothesesCalculees().map(function (h) {
      return {
        etat: h.etat,
        confiance: Number(h.p.toFixed(2)),
        intervalle: [Number(h.lo.toFixed(2)), Number(h.hi.toFixed(2))],
        correction_utilisateur: h.avis
      };
    });
    const action = tropPeuAction()
      ? "aucune — données insuffisantes"
      : (etat.action === "ignorer" ? "aucune (ignorée)" : etat.data.action_interface.titre);

    return {
      temps: "T3",
      contexte: etat.data.contexte.cas,
      simulation: true,
      diagnostic_medical: false,
      signaux: signaux,
      hypotheses: hyps,
      action_interface: action,
      conservation: "session",
      brut_conserve: false
    };
  }

  function tropPeuAction() {
    return confianceGlobale(hypothesesCalculees()).couverture < 0.4;
  }

  function renderStatut() {
    const n = Object.keys(etat.avis).length;
    const elStatut = document.getElementById("statut-controle");
    if (etat.action === "ignorer") {
      elStatut.textContent = "Vous avez ignoré l’adaptation. Contrôle conservé.";
    } else if (n === 0) {
      elStatut.textContent = "Aucune correction pour l’instant.";
    } else {
      elStatut.textContent = n + " interprétation" + (n > 1 ? "s" : "") + " annotée" + (n > 1 ? "s" : "") + " par vous.";
    }
  }

  function render() {
    renderLangages();
    renderSignaux();
    renderHypotheses();
    renderChart();
    renderAction();
    renderStatut();
    document.getElementById("representation").textContent =
      JSON.stringify(representation(), null, 2);
  }

  async function charger() {
    try {
      const r = await fetch("data/session-simulee.json", { cache: "no-store" });
      if (r.ok) {
        const json = await r.json();
        Object.keys(FALLBACK.signaux).forEach(function (id) {
          if (json.signaux && json.signaux[id] && !json.signaux[id].label) {
            json.signaux[id].label = FALLBACK.signaux[id].label || SIGNALS_META[id].label;
          }
        });
        return json;
      }
    } catch (e) {
      /* fichier local sans serveur : repli */
    }
    return FALLBACK;
  }

  document.addEventListener("DOMContentLoaded", async function () {
    etat.data = await charger();
    if (!etat.data.signaux.frequence_cardiaque.ecart_bpm) {
      etat.data.signaux.frequence_cardiaque.ecart_bpm = 24;
    }
    render();
  });
})();
