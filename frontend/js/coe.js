"use strict";

const $ = (sel, el = document) => el.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n) => String(Math.round(n * 2) / 2);
const pct = (x) => `${Math.round(x * 100)}%`;
const ICON = { ok: ["good", "✓"], warn: ["warn", "!"], bad: ["crit", "✕"] };
const HOT = new Set(["VELOCITY_GATE", "VELOCITY_NUDGE", "SEED_DRIFT_DETECTED", "TIER3_SHADOW_REVIEW", "SHADOW_REVIEW_ROUTED",
  "INJECTION_FLAGGED", "MARKS_REJECTED", "TAMPER_DETECTED", "DEMO_DB_EDIT"]);

const verifications = {}; // script_id -> last verify result, kept across refreshes

async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.detail?.message || data?.detail || res.statusText);
  return data;
}

function toast(msg, kind = "") {
  const t = document.createElement("div");
  t.className = `toast ${kind}`;
  t.textContent = msg;
  $("#toasts").append(t);
  setTimeout(() => t.remove(), 5000);
}

function badge(label, tone) {
  const [cls, glyph] = ICON[tone] || ICON.ok;
  return `<span class="badge"><span class="icon ${cls}">${glyph}</span>${esc(label)}</span>`;
}

function meter(value, tolerance) {
  // Drift on a 0-50% scale with a tick at the tolerance line.
  const scale = 0.5;
  const w = Math.min(value / scale, 1) * 100;
  return `<span class="meter" role="img" aria-label="drift ${pct(value)}, tolerance ${pct(tolerance)}">
    <i class="${value > tolerance ? "over" : ""}" style="width:${w}%"></i><b style="left:${(tolerance / scale) * 100}%"></b></span>`;
}

function renderKpis(k) {
  const tiles = [
    ["Scripts evaluated", k.scripts.toLocaleString("en-IN"), `${k.examiners} examiners`],
    ["Median time per script", k.median_dwell_s == null ? "–" : `${Math.round(k.median_dwell_s)} s`, "across examiners"],
    ["Speed flags", k.velocity_flags, "Tier 1–2 prompts shown"],
    ["Seed drift alerts", k.seed_alerts, "beyond ±15% of max marks"],
    ["Shadow-review queue", k.shadow_queue, "scripts awaiting second reading"],
  ];
  $("#kpis").innerHTML = tiles.map(([label, value, sub]) =>
    `<div class="card kpi"><div class="label">${label}</div><div class="value">${value}</div><div class="sub">${sub}</div></div>`).join("");
}

function renderExaminers(rows) {
  $("#examiners").innerHTML = `
    <thead><tr><th>Examiner</th><th class="n">Scripts</th><th class="n">Avg time</th><th class="n">Speed flags</th>
      <th class="n">Mark spread</th><th>Seed drift</th><th class="n">Accepts AI as-is</th><th>Status</th></tr></thead>
    <tbody>${rows.map((r) => `
      <tr class="${r.simulated ? "" : "live"}">
        <td><b class="mono">${esc(r.id)}</b> ${r.simulated ? '<span class="tag">simulated</span>' : '<span class="tag">live</span>'}</td>
        <td class="n">${r.scripts}</td>
        <td class="n">${r.avg_dwell_s == null ? "–" : `${Math.round(r.avg_dwell_s)} s`}</td>
        <td class="n">${r.violations}</td>
        <td class="n">${r.entropy_bits == null ? `<span class="muted small">${esc(r.entropy_note)}</span>` : `${r.entropy_bits.toFixed(2)} bits`}</td>
        <td class="num drift">${r.seed_drift == null ? '<span class="muted small">no seed yet</span>' : `${meter(r.seed_drift, 0.15)}${pct(r.seed_drift)}`}</td>
        <td class="n">${r.accept_rate == null ? "–" : pct(r.accept_rate)}</td>
        <td><div class="badges">${r.badges.map((b) => badge(b.label, b.tone)).join("")}</div></td>
      </tr>`).join("")}</tbody>`;
}

function renderSeeds(rows) {
  if (!rows.length) { $("#seeds").innerHTML = `<tbody><tr><td class="empty">No seed scripts marked yet.</td></tr></tbody>`; return; }
  $("#seeds").innerHTML = `
    <thead><tr><th>Examiner</th><th>Anchor script</th><th class="n">Chief Examiner</th><th class="n">Examiner</th><th>Examiner drift</th>
      <th class="n">AI suggested</th><th class="n">AI drift</th><th>Result</th></tr></thead>
    <tbody>${rows.map((s) => `
      <tr class="${s.simulated ? "" : "live"}">
        <td><span class="mono">${esc(s.examiner_id)}</span> ${s.simulated ? '<span class="tag">simulated</span>' : '<span class="tag">live</span>'}</td>
        <td class="mono">${esc(s.script_id)}</td>
        <td class="n">${fmt(s.gold_total)} / ${fmt(s.max_marks)}</td>
        <td class="n">${fmt(s.given_total)}</td>
        <td class="num drift">${meter(s.drift, s.tolerance)}${pct(s.drift)}</td>
        <td class="n">${fmt(s.ai_total)}</td>
        <td class="n">${pct(s.ai_drift)}</td>
        <td>${s.flagged ? badge("Drift: next scripts to Head Examiner", "bad") : badge("Within tolerance", "ok")}</td>
      </tr>`).join("")}</tbody>`;
}

function renderShadow(rows) {
  if (!rows.length) { $("#shadow").innerHTML = `<tbody><tr><td class="empty">Nothing routed for a second reading.</td></tr></tbody>`; return; }
  $("#shadow").innerHTML = `<thead><tr><th>Script</th><th>Examiner</th><th>Why</th></tr></thead>
    <tbody>${rows.map((r) => `<tr class="${r.simulated ? "" : "live"}"><td class="mono">${esc(r.script_id)}</td>
      <td><span class="mono">${esc(r.examiner_id)}</span> ${r.simulated ? '<span class="tag">simulated</span>' : ""}</td><td>${esc(r.reason)}</td></tr>`).join("")}</tbody>`;
}

function verifyHtml(v) {
  if (!v) return "";
  const head = v.ok
    ? `<b>${badge("Record intact", "ok")}</b> <span class="small muted">all ${v.leaves.length} hashes match · signature valid · chain intact</span>`
    : `<b>${badge("Record changed after submission", "bad")}</b>`;
  const changed = v.leaves.filter((l) => !l.ok);
  const list = changed.length ? `<ul>${changed.map((l) => `<li><span class="icon crit">✕</span><span><b>${esc(l.name.replace(/_/g, " "))}</b> changed: recorded <span class="mono">${l.stored.slice(0, 12)}…</span> now <span class="mono">${l.current.slice(0, 12)}…</span></span></li>`).join("")}</ul>` : "";
  return `<div class="verify callout ${v.ok ? "good" : "crit"}">${head}${list}</div>`;
}

function renderLedger(subs, ledger) {
  $("#ledger-meta").innerHTML = `${ledger.length} entr${ledger.length === 1 ? "y" : "ies"} · chain ${ledger.chain_ok ? "intact" : "BROKEN"} · key ${esc(ledger.public_key_fingerprint)}`;
  if (!subs.length) { $("#ledger").innerHTML = `<div class="empty">Submitted scripts appear here with their signed Merkle root.</div>`; return; }
  $("#ledger").innerHTML = subs.map((s) => `
    <div class="ledger-row" data-id="${esc(s.script_id)}">
      <div class="top"><span class="tag">#${s.ledger_index}</span><b class="mono">${esc(s.script_id)}</b>
        <span class="num">${fmt(s.total)} / ${fmt(s.max_marks)}</span><span class="mono small muted">root ${s.merkle_root.slice(0, 16)}…</span></div>
      <div class="acts">
        <a class="btn sm" href="${esc(s.dossier_url)}" target="_blank" rel="noopener">Audit dossier (PDF)</a>
        <button class="btn sm" data-act="verify" type="button">Verify integrity</button>
        <button class="btn sm ghost danger" data-act="tamper" type="button" title="Demo: change the stored marks directly, bypassing the system">Edit marks in DB (demo)</button>
      </div>
      ${verifyHtml(verifications[s.script_id])}
    </div>`).join("");
}

function describe(e) {
  const skip = new Set(["offset", "ts", "topic", "type"]);
  return Object.entries(e).filter(([k]) => !skip.has(k))
    .map(([k, v]) => `${k}=${Array.isArray(v) ? v.join("|") : v}`).join("  ");
}

function renderEvents(events) {
  if (!events.length) { $("#events").innerHTML = `<div class="empty">No events yet. Open the examiner workspace.</div>`; return; }
  $("#events").innerHTML = events.map((e) => `
    <div class="event"><span class="mono muted">#${e.offset}</span><span class="mono muted">${esc(e.ts.slice(11, 19))}</span>
      <span class="type ${HOT.has(e.type) ? "hot" : ""}">${esc(e.type)}</span>
      <span class="detail mono">${esc(describe(e))}</span></div>`).join("");
}

async function refresh() {
  try {
    const d = await api("/api/coe");
    $("#engine-chip").innerHTML = `<span class="dot ${d.engine.mode}"></span><span>${esc(d.engine.label)}</span>`;
    renderKpis(d.kpis);
    renderExaminers(d.examiners);
    renderSeeds(d.seeds);
    renderShadow(d.shadow_queue);
    renderLedger(d.submissions, d.ledger);
    renderEvents(d.events);
    $("#updated").textContent = `Updated ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    $("#updated").textContent = `Offline: ${err.message}`;
  }
}

$("#ledger").addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-act]");
  if (!btn) return;
  const id = btn.closest(".ledger-row").dataset.id;
  try {
    if (btn.dataset.act === "tamper") {
      const r = await api(`/api/demo/tamper/${encodeURIComponent(id)}`, { method: "POST" });
      toast(`Stored total for ${id} changed from ${fmt(r.before)} to ${fmt(r.after)} directly in the database. Now verify it.`);
      delete verifications[id];
    } else {
      verifications[id] = await api(`/api/scripts/${encodeURIComponent(id)}/verify`);
    }
  } catch (err) {
    toast(err.message, "error");
  }
  refresh();
});

$("#reset-btn").addEventListener("click", async () => {
  if (!confirm("Reset the demo? This clears all submissions, the ledger and events.")) return;
  await api("/api/demo/reset", { method: "POST" });
  Object.keys(verifications).forEach((k) => delete verifications[k]);
  toast("Demo reset. Reload the examiner workspace to start again.");
  refresh();
});

refresh();
setInterval(refresh, 2000);
