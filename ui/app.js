/* Language Decoder — UI (no dependencies, offline-aware).
 * Renders the DecodedHuman contract produced by the engine and allows
 * re-decoding arbitrary text through the /api/decode endpoint when served.
 */
(function () {
  "use strict";

  const DOMAIN_META = {
    physical: { label: "Physique", icon: "🫀" },
    mental: { label: "Mental", icon: "🧠" },
    action: { label: "Capacité d'action", icon: "⚙️" },
    dynamics: { label: "Fonctionnement", icon: "⏱" },
  };

  let PROFILE = null;
  let currentTab = "overview";

  const $ = (sel) => document.querySelector(sel);
  const content = $("#content");

  function esc(s) {
    if (s == null) return "";
    return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function levelBadge(level) {
    const names = { 1: "Fait documenté", 2: "Compétence inférée", 3: "Capacité candidate", 4: "Hypothèse cognitive", 5: "Conclusion psychologique" };
    const lvl = Math.min(5, Math.max(1, level));
    return `<span class="badge badge-lvl${lvl}">L${lvl} · ${esc(names[lvl])}</span>`;
  }

  function strengthBar(value) {
    const v = Math.round((value || 0) * 100);
    return `<div class="bar"><div class="bar-fill" style="width:${v}%"></div></div>`;
  }

  function renderOverview(data) {
    const d = data.domains;
    const counts = {};
    Object.keys(DOMAIN_META).forEach((k) => {
      counts[k] = (d[k] && d[k].estimates ? d[k].estimates.length : 0) + (k === "dynamics" ? (data.dynamics.retentions || []).length : 0);
    });
    let cards = "";
    Object.keys(DOMAIN_META).forEach((k) => {
      const block = d[k];
      if (!block) return;
      const n = block.estimates.length;
      const refusals = block.refusals.length;
      const obs = block.observations.length;
      const avg = n ? (block.estimates.reduce((s, e) => s + (e.value || 0), 0) / n) : 0;
      cards += `
        <div class="ov-card" data-goto="${k}">
          <h3>${DOMAIN_META[k].icon} ${DOMAIN_META[k].label}</h3>
          <p>${esc(block.describe)}</p>
          <div class="ov-num">
            <div>${n}<small>estimations</small></div>
            <div>${obs}<small>observations</small></div>
            <div>${refusals}<small>refus</small></div>
            <div>${Math.round(avg * 100)}<small>moyenne</small></div>
          </div>
        </div>`;
    });
    const funcs = (data.functioning || []).length;
    const dyns = (data.dynamics.retentions || []).length;
    const epi = data.epistemic_summary || {};
    return `
      <div class="section-title"><h2>Vue d'ensemble</h2><span class="sub">${esc(data.id)} · ${esc(data.source_title)}</span></div>
      <div class="ov-grid">${cards}
        <div class="ov-card" data-goto="dynamics">
          <h3>↔ Fonctionnement & ICF</h3>
          <p>Projections ICF (hypothèses) et dynamique dans le temps.</p>
          <div class="ov-num"><div>${funcs}<small>projections</small></div><div>${dyns}<small>rétentions</small></div></div>
        </div>
      </div>
      <div style="margin-top:20px" class="note">
        <b>Garde-fou épistémique :</b> niveau max produit = L${epi.max_level || 0} (${epi.level5_present ? "⚠️" : ""}).
        L${epi.max_level || 0} — ${esc(epi.note || "")}
      </div>`;
  }

  function estimateCard(e, includeAlts) {
    const alts = (includeAlts && e.alternatives && e.alternatives.length)
      ? `<div class="alts"><div class="ttl">Alternatives d'explication</div>` +
        e.alternatives.map((a) => `<span class="alt-chip">${esc(a.label)} · ${(a.plausibility * 100).toFixed(0)}%</span>`).join("") +
        `</div>` : "";
    return `
      <div class="est-card">
        <div class="est-head">
          <span class="label">${esc(e.construct_label)}</span>
          ${levelBadge(e.epistemic_level)}
        </div>
        ${strengthBar(e.value)}
        <div class="est-meta">
          <span class="strength">${esc(e.strength_label)} · ${Math.round(e.value * 100)}</span>
          <span class="unc">σ=${e.uncertainty.total.toFixed(2)}</span>
        </div>
        ${alts}
      </div>`;
  }

  function renderDomain(domain, data) {
    const block = data.domains[domain];
    if (!block) return `<div class="note">Domaine indisponible.</div>`;
    let html = `<div class="section-title"><h2>${DOMAIN_META[domain].icon} ${block.title}</h2><span class="sub">${block.domain}</span></div>`;
    html += `<div class="domain-desc">${esc(block.describe)}</div>`;
    if (block.refusals && block.refusals.length) {
      html += block.refusals.map((r) => `<div class="refusal"><span class="code">Refus · ${esc(r.code)}</span><div class="msg">${esc(r.message)}</div></div>`).join("");
    }
    if (block.estimates && block.estimates.length) {
      html += `<div class="est-grid">${block.estimates.map((e) => estimateCard(e, domain !== "dynamics")).join("")}</div>`;
    } else {
      html += `<div class="note">Aucune estimation pour ce domaine dans ce décodage.</div>`;
    }
    return html;
  }

  function renderDynamics(data) {
    const dyn = data.dynamics || {};
    const rets = dyn.retentions || [];
    let html = `<div class="section-title"><h2>⏱ Fonctionnement</h2><span class="sub">modèle : ${esc(dyn.model || "—")}</span></div>`;
    html += `<div class="domain-desc">Dynamique dans le temps — oubli (courbe d'Ebbinghaus), réactivation (loi de puissance), transfert.</div>`;
    if (!rets.length) html += `<div class="note">Aucune rétention calculée.</div>`;
    rets.forEach((r) => {
      const tr = r.transferability || {};
      html += `
        <div class="dyn-card">
          <div class="rl">${esc(r.construct_id)}</div>
          ${strengthBar(r.vitality)}
          <div class="meta">
            <span>Vitalité ${(r.vitality * 100).toFixed(0)}</span>
            <span>${esc(r.availability_label)}</span>
            <span>base ${(r.base_level * 100).toFixed(0)}</span>
            <span>inactif ${r.years_inactive} an(s)</span>
            <span>demi-vie ${r.half_life_years} an(s)</span>
            <span>transfert ${Math.round((tr.score || 0) * 100)}%</span>
          </div>
        </div>`;
    });

    if (data.functioning && data.functioning.length) {
      html += `<div class="section-title" style="margin-top:26px"><h2>Projections ICF</h2><span class="sub">hypothèses, jamais déductions</span></div>`;
      html += `<div class="func-list">` + data.functioning.map((f) => `
        <div class="func-card">
          <div class="icf">ICF ${esc(f.target_code)}</div>
          <div class="k">${esc(f.construct_id)}</div>
          <div class="k">${esc(f.kind.replace(/_/g, " "))}</div>
          <div class="st">${f.status}</div>
        </div>`).join("") + `</div>`;
    }
    return html;
  }

  function renderTrace(data) {
    let html = `<div class="section-title"><h2>Traçabilité</h2><span class="sub">${data.observations.length} observation(s) · provenance</span></div>`;
    html += `<div class="note" style="margin-bottom:14px">Une observation n'est jamais un construit. ` +
      `L'alignement indique le lien <i>mesure → construit</i> ; un alignement <code>none</code> peut être stocké mais ne fonde pas une estimation.</div>`;
    html += `<table class="trace-table"><thead><tr><th>Observation</th><th>Construit(s)</th><th>Canal</th><th>Align.</th><th>Valeur</th><th>Epi.</th><th>Provenance</th></tr></thead><tbody>`;
    html += data.observations.map((o) => `
      <tr>
        <td>${esc(o.content || "(valeur)")}</td>
        <td class="cid">${o.construct_ids.map(esc).join(", ")}</td>
        <td>${esc(o.channel)}</td>
        <td class="align align-${esc(o.alignment)}">${esc(o.alignment)}</td>
        <td>${o.normalized_value != null ? (o.normalized_value * 100).toFixed(0) : (o.missingness ? esc(o.missingness) : "—")}</td>
        <td>L${o.epistemic_level}</td>
        <td>${o.provenance ? esc(o.provenance.source_document || o.provenance.agent) : "—"}</td>
      </tr>`).join("");
    html += `</tbody></table>`;
    if (data.notes && data.notes.length) html += `<div style="margin-top:14px">${data.notes.map((n) => `<div class="note" style="margin-bottom:6px">${esc(n)}</div>`).join("")}</div>`;
    return html;
  }

  function renderEmpty(data) {
    const notes = (data.notes || []).map((n) => `<div class="note" style="margin-bottom:6px">${esc(n)}</div>`).join("");
    return `<div class="section-title"><h2>Décodage</h2></div>${notes || `<div class="note">Aucune donnée. Collez un texte ci-dessous puis « Décoder ».</div>`}`;
  }

  function render() {
    const data = PROFILE;
    document.getElementById("source-title").textContent = (data && data.source_title) || "—";
    document.getElementById("meta").textContent = data
      ? `${data.version || ""} · ${data.id || ""} · observations ${(data.observations || []).length}`
      : "";

    let html;
    if (!data) { html = renderEmpty(null); }
    else if (currentTab === "overview") html = renderOverview(data);
    else if (currentTab === "physical") html = renderDomain("physical", data);
    else if (currentTab === "mental") html = renderDomain("mental", data);
    else if (currentTab === "action") html = renderDomain("action", data);
    else if (currentTab === "dynamics") html = renderDynamics(data);
    else if (currentTab === "trace") html = renderTrace(data);
    content.innerHTML = html;

    // wire navigation from overview cards
    if (currentTab === "overview") {
      content.querySelectorAll("[data-goto]").forEach((el) => {
        el.addEventListener("click", () => {
          const go = el.getAttribute("data-goto");
          if (go === "dynamics") setTab("dynamics");
          else if (DOMAIN_META[go]) setTab(go);
        });
      });
    }
  }

  function setTab(tab) {
    currentTab = tab;
    document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === tab));
    render();
  }

  async function load() {
    try {
      const res = await fetch("data/profile.json", { cache: "no-store" });
      if (res.ok) PROFILE = await res.json();
    } catch (e) { PROFILE = null; }
    render();
  }

  async function decodeNow() {
    const text = $("#decode-input").value;
    if (!text.trim()) { $("#decode-status").textContent = "Texte vide."; return; }
    const btn = $("#decode-btn");
    btn.disabled = true;
    $("#decode-status").textContent = "Décodage en cours…";
    try {
      const res = await fetch("api/decode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          title: $("#decode-title").value || "Décodage humain",
          person: $("#decode-person").value || "h-001",
          year: 2026,
        }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      PROFILE = await res.json();
      $("#decode-status").textContent = "✔ Décodé — " + PROFILE.id + " · " + PROFILE.epistemic_summary.total_estimates + " estimations, " + PROFILE.epistemic_summary.total_refusals + " refus.";
      setTab("overview");
    } catch (e) {
      $("#decode-status").textContent = "✖ Échec (le serveur est-il lancé ? `python -m language_decoder serve`). " + e.message;
    } finally {
      btn.disabled = false;
    }
  }

  // init
  document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => setTab(t.dataset.view)));
  document.getElementById("decode-btn").addEventListener("click", decodeNow);
  load();
})();
