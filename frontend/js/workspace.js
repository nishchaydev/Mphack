"use strict";

const $ = (sel, el = document) => el.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n) => String(Math.round(n * 2) / 2);
const mmss = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
const sum = (xs) => xs.reduce((a, b) => a + b, 0);
const LANG = { hindi: "Hindi", english: "English", hinglish: "Hinglish", other: "Mixed" };
const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;

const state = {
  session: null, script: null, preread: null, criteria: [], page: 0, dwell: [], annotations: [],
  tool: "tick", ack: 0, submitted: null, busy: false, drawing: null, pendingNote: null,
};

async function api(path, opts = {}) {
  const headers = opts.body && !(opts.body instanceof FormData) ? { "Content-Type": "application/json" } : {};
  const res = await fetch(path, { ...opts, headers });
  let data = null;
  try { data = await res.json(); } catch { /* empty body */ }
  if (!res.ok) {
    const d = data?.detail;
    const msg = typeof d === "string" ? d : d?.message || (Array.isArray(d) ? d.map((e) => e.msg).join("; ") : res.statusText);
    const err = new Error(msg);
    err.status = res.status;
    err.detail = d;
    throw err;
  }
  return data;
}

function toast(msg, kind = "") {
  const t = document.createElement("div");
  t.className = `toast ${kind}`;
  t.textContent = msg;
  $("#toasts").append(t);
  setTimeout(() => t.remove(), kind === "error" ? 8000 : 4000);
}

/* ---------- Session & queue ---------- */

async function loadSession() {
  state.session = await api("/api/session");
  const e = state.session.engine;
  $("#engine-chip").innerHTML = `<span class="dot ${e.mode}"></span><span>${esc(e.label)}</span>`;
  $("#examiner-chip").textContent = `${state.session.examiner.id} · ${state.session.examiner.name}`;
  const q = state.session.queue;
  const done = q.filter((s) => s.status === "submitted").length;
  $("#queue-chip").textContent = `Queue: ${done} of ${q.length} done`;
}

async function openScript(id) {
  Object.assign(state, { script: null, preread: null, criteria: [], page: 0, annotations: [], ack: 0, submitted: null, drawing: null });
  $("#done-card").hidden = true;
  $("#submit-bar").hidden = false;
  $("#criteria").innerHTML = "";
  $("#transcript-card").hidden = true;
  $("#ai-card").innerHTML = "";
  window.scrollTo(0, 0);
  const s = await api(`/api/scripts/${encodeURIComponent(id)}`);
  state.script = s;
  state.dwell = s.pages.map(() => 0);
  s.pages.forEach((p) => { new Image().src = p.url; });
  history.replaceState(null, "", `/?script=${encodeURIComponent(id)}`);
  renderQuestion();
  showPage(0);
  $("#max").textContent = fmt(s.question.max_marks);
  renderTotal();
  if (s.status === "submitted") {
    showDone({ script_id: id, total: s.submitted.total, max_marks: s.question.max_marks, ledger_index: s.submitted.ledger_index,
      dossier_url: `/api/scripts/${id}/dossier.pdf`, next_script_id: state.session.next_script_id });
    return;
  }
  renderAI({ loading: true });
  try {
    state.preread = await api(`/api/scripts/${encodeURIComponent(id)}/preread`, { method: "POST" });
  } catch (err) {
    renderAI({ error: err.message });
    return;
  }
  state.criteria = state.preread.criteria.map((c) => ({ ...c, value: null, decision: null, verified: false }));
  renderAI();
  renderCriteria();
  renderTotal();
  $("#transcript").textContent = state.preread.transcription;
  $("#transcript-card").hidden = false;
}

/* ---------- Copilot panel ---------- */

function renderQuestion() {
  const { question: q, script_id, pages } = state.script;
  $("#question-card").innerHTML = `
    <div class="script-head">
      <div><h1>${esc(script_id)}</h1><div class="small muted">${esc(q.course)}</div></div>
      <span class="chip">${esc(q.id)} · ${fmt(q.max_marks)} marks</span>
    </div>
    <p class="qtext">${esc(q.text)}</p>
    <div class="small muted">${esc(q.text_en)}</div>
    <details style="margin-top:8px"><summary>Model answer and rubric</summary>
      <div class="small">${esc(q.model_answer)}</div>
      <ul class="small" style="padding-left:18px;margin:6px 0 0">${q.rubric.map((r) => `<li><b>${esc(r.id)} (${fmt(r.max)})</b> ${esc(r.description)}</li>`).join("")}</ul>
    </details>`;
  $("#booklet-meta").textContent = `Booklet ${script_id} · ${pages.length} page${pages.length > 1 ? "s" : ""} · candidate identity masked`;
}

function renderAI(opt = {}) {
  const el = $("#ai-card");
  if (opt.loading) {
    el.innerHTML = `<div class="ai-line"><span class="spinner"></span>AI is pre-reading ${state.script.pages.length} page(s)…</div>`;
    return;
  }
  if (opt.error) {
    el.innerHTML = `<div class="callout crit"><b><span class="icon crit">!</span>AI pre-read unavailable</b><div class="small">${esc(opt.error)}</div></div>`;
    return;
  }
  const p = state.preread;
  const tokens = p.usage ? ` · ${p.usage.input_tokens.toLocaleString("en-IN")} in / ${(p.usage.output_tokens + p.usage.thinking_tokens).toLocaleString("en-IN")} out tokens · ₹${p.usage.cost_inr.toFixed(3)}` : "";
  const time = p.engine_kind === "live" ? ` · ${(p.latency_ms / 1000).toFixed(1)} s`
    : p.engine_kind === "cache" ? ` · ${(p.latency_ms / 1000).toFixed(1)} s on first run` : "";
  const extras = [p.equation_count && plural(p.equation_count, "equation"), p.diagram_count && plural(p.diagram_count, "diagram")].filter(Boolean);
  const reasons = p.injection_suspected ? p.review_reasons.slice(1) : p.review_reasons;
  let html = `
    <div class="ai-line"><span class="dot ${p.engine_kind === "mock" ? "mock" : "live"}"></span><span><b>AI pre-read</b> · ${esc(p.engine)}${time}${tokens}</span></div>
    <div class="ai-line small" style="margin-top:2px">${LANG[p.language] || esc(p.language)} · ${p.word_count} words${extras.length ? " · " + extras.join(" · ") : ""} · confidence ${Math.round(p.confidence * 100)}%</div>`;
  if (p.injection_suspected) {
    html += `<div class="callout crit" style="margin-top:10px"><b><span class="icon crit">!</span>Instructions found inside the answer were ignored</b>
      <div class="small">“${esc(p.injection_text || p.injection_matches.join(" · "))}”</div></div>`;
  }
  if (reasons.length) {
    html += `<div class="callout warn" style="margin-top:10px"><b><span class="icon warn">!</span>Check before accepting</b><ul class="small">${reasons.map((r) => `<li>${esc(r)}</li>`).join("")}</ul></div>`;
  } else if (!p.injection_suspected) {
    html += `<div class="callout good" style="margin-top:10px"><b><span class="icon good">✓</span>Every suggested mark is backed by a quote found in the answer</b></div>`;
  }
  html += `<p class="ai-summary">${esc(p.summary)}</p>
    <div class="controls"><span class="small muted">AI suggests <b>${fmt(p.suggested_total)} / ${fmt(p.max_marks)}</b>. You decide every mark.</span>
    <button class="btn sm" id="accept-all" type="button">Accept all</button></div>`;
  el.innerHTML = html;
  $("#accept-all").addEventListener("click", () => {
    state.criteria.forEach((c) => { c.value = c.suggested; c.decision = "accepted"; });
    renderCriteria();
    renderTotal();
  });
}

function decisionText(c) {
  if (c.value === null) return c.decision === "overridden" ? "Override: type your own mark" : "Not marked yet";
  const over = c.value > c.max ? ` · above the ${fmt(c.max)}-mark maximum` : "";
  const label = { accepted: "Accepted AI suggestion", modified: `Modified (AI suggested ${fmt(c.suggested)})`,
    overridden: `Overridden (AI suggested ${fmt(c.suggested)})` }[c.decision || "modified"];
  return label + over;
}

function evidenceHtml(c) {
  if (!c.evidence.length) return `<p class="reason">No supporting text found in the answer.</p>`;
  return c.evidence.map((e) => {
    const cls = e.kind === "diagram" ? "diagram" : e.grounded ? "" : "ungrounded";
    const pre = e.kind === "diagram" ? `<span class="tag">Diagram</span> ` : "";
    const post = e.grounded ? "" : ` <span class="tag">not in transcription</span>`;
    return `<div class="quote ${cls}">${pre}${esc(e.text.replace(/^\[diagram\]\s*/i, ""))}${post}</div>`;
  }).join("");
}

function renderCriteria() {
  $("#criteria").innerHTML = state.criteria.map((c, i) => `
    <div class="card crit-card" data-i="${i}" style="margin-bottom:12px">
      <div class="crit-top"><h3>${esc(c.criterion_id)} · ${esc(c.name)}</h3><span class="ai-pill">AI ${fmt(c.suggested)} / ${fmt(c.max)}</span></div>
      ${evidenceHtml(c)}
      ${c.reasoning ? `<p class="reason">${esc(c.reasoning)}</p>` : ""}
      ${c.missing ? `<p class="reason"><b>Missing:</b> ${esc(c.missing)}</p>` : ""}
      ${c.flags.map((f) => `<p class="flag-line"><span class="icon warn">!</span><span>${esc(f)}</span></p>`).join("")}
      <div class="controls">
        <button class="btn sm" data-act="accept" type="button">Accept ${fmt(c.suggested)}</button>
        <span class="stepper">
          <button data-act="dec" type="button" aria-label="Half a mark less">−</button>
          <input data-act="input" inputmode="decimal" placeholder="–" aria-label="Marks for ${esc(c.criterion_id)}">
          <button data-act="inc" type="button" aria-label="Half a mark more">+</button>
        </span>
        <button class="btn sm ghost" data-act="override" type="button">Override</button>
        <button class="check-chip" data-act="verify" type="button" aria-pressed="false">☐ Checked on script</button>
      </div>
      <div class="decision"></div>
    </div>`).join("");
  document.querySelectorAll(".crit-card").forEach((card) => refreshCard(card, state.criteria[+card.dataset.i]));
}

function refreshCard(card, c) {
  const input = card.querySelector("input");
  if (document.activeElement !== input) input.value = c.value === null ? "" : fmt(c.value);
  input.classList.toggle("over", c.value !== null && c.value > c.max);
  const chip = card.querySelector('[data-act="verify"]');
  chip.setAttribute("aria-pressed", String(c.verified));
  chip.textContent = `${c.verified ? "☑" : "☐"} Checked on script`;
  card.querySelector(".decision").textContent = decisionText(c);
}

$("#criteria").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-act]");
  if (!btn || state.submitted) return;
  const card = btn.closest(".crit-card");
  const c = state.criteria[+card.dataset.i];
  const settle = () => { if (c.decision !== "overridden") c.decision = c.value === c.suggested ? "accepted" : "modified"; };
  switch (btn.dataset.act) {
    case "accept": c.value = c.suggested; c.decision = "accepted"; break;
    case "dec": c.value = Math.max(0, (c.value ?? c.suggested) - 0.5); settle(); break;
    case "inc": c.value = Math.min(c.max, (c.value ?? c.suggested) + 0.5); settle(); break;
    case "override": c.value = null; c.decision = "overridden"; break;
    case "verify": c.verified = !c.verified; break;
    default: return;
  }
  refreshCard(card, c);
  if (btn.dataset.act === "override") card.querySelector("input").focus();
  renderTotal();
});

$("#criteria").addEventListener("input", (e) => {
  if (e.target.dataset.act !== "input") return;
  const card = e.target.closest(".crit-card");
  const c = state.criteria[+card.dataset.i];
  const v = parseFloat(e.target.value.replace(",", "."));
  c.value = Number.isFinite(v) && v >= 0 ? v : null;
  if (c.decision !== "overridden") c.decision = c.value === c.suggested ? "accepted" : "modified";
  refreshCard(card, c);
  renderTotal();
});

function touched() {
  return state.criteria.some((c) => c.verified) || state.annotations.length > 0;
}

function renderTotal() {
  const ready = state.criteria.length > 0 && state.criteria.every((c) => c.value !== null);
  const total = sum(state.criteria.map((c) => c.value ?? 0));
  $("#total").textContent = state.criteria.length ? fmt(total) : "–";
  const gated = state.ack === 2 && !touched();
  $("#submit-btn").disabled = !ready || state.busy || !!state.submitted || gated;
  const note = $("#gate-note");
  note.hidden = state.ack !== 2;
  note.innerHTML = gated
    ? `<b><span class="icon warn">!</span>Check one criterion on the script to unlock</b>Tap “☐ Checked on script” on any criterion, or mark the page.`
    : `<b><span class="icon good">✓</span>Check recorded. You can submit.</b>`;
}

/* ---------- Submit & velocity sentinel ---------- */

function showVelocity(v) {
  state.ack = Math.max(state.ack, v.tier);
  const p = state.preread;
  const parts = [plural(p.word_count, "word"), p.equation_count && plural(p.equation_count, "equation"),
    p.diagram_count && plural(p.diagram_count, "diagram")].filter(Boolean).join(", ");
  let html = v.tier === 2
    ? `<h2><span class="icon crit">!</span>Check needed before submitting</h2>
       <p>This answer was submitted after <b>${v.dwell_s} s</b>. A careful first read of it (${parts}) takes about <b>${Math.round(v.floor_s)} s</b>.</p>
       <p>To continue, check at least one criterion against the script: tap <b>☐ Checked on script</b> on a criterion card, or mark the page with a tick.</p>`
    : `<h2><span class="icon warn">!</span>Quick check before submitting</h2>
       <p>You have been on this script for <b>${v.dwell_s} s</b>. A careful first read of it (${parts}) takes about <b>${Math.round(v.floor_s)} s</b>.</p>`;
  if (v.unviewed_pages.length) html += `<p><b>Not opened yet:</b> page ${v.unviewed_pages.join(", ")}.</p>`;
  html += `<p class="small muted">This is a prompt, not a lock.</p>`;
  $("#velocity-body").innerHTML = html;
  const go = $("#velocity-go");
  const ok = v.tier < 2 || touched();
  go.textContent = v.tier === 2 ? (ok ? "Submit" : "Check a criterion first") : "Submit anyway";
  go.disabled = !ok;
  $("#velocity-dialog").showModal();
  renderTotal();
}

$("#velocity-back").addEventListener("click", () => $("#velocity-dialog").close());
$("#velocity-go").addEventListener("click", () => { $("#velocity-dialog").close(); submit(); });
$("#submit-btn").addEventListener("click", () => submit());

async function submit() {
  if (state.busy || !state.script) return;
  state.busy = true;
  renderTotal();
  const body = {
    marks: state.criteria.map((c) => ({ criterion_id: c.criterion_id, marks: c.value, decision: c.decision || "modified", verified: c.verified })),
    annotations: state.annotations,
    telemetry: { page_dwell_s: state.dwell.map((x) => Math.round(x * 10) / 10), active_s: Math.round(sum(state.dwell) * 10) / 10 },
    acknowledged_tier: state.ack,
  };
  try {
    const r = await api(`/api/scripts/${encodeURIComponent(state.script.script_id)}/submit`, { method: "POST", body: JSON.stringify(body) });
    state.submitted = r;
    showDone(r);
    await loadSession();
  } catch (err) {
    if (err.status === 409 && err.detail?.velocity) showVelocity(err.detail.velocity);
    else toast(`Server rejected the submission: ${err.message}`, "error");
  } finally {
    state.busy = false;
    renderTotal();
  }
}

function showDone(r) {
  $("#submit-bar").hidden = true;
  const card = $("#done-card");
  card.hidden = false;
  card.innerHTML = `
    <div class="callout good"><b><span class="icon good">✓</span>Submitted ${fmt(r.total)} / ${fmt(r.max_marks)}</b>
      <div class="small">Hashed, signed and written to ledger entry #${r.ledger_index}.</div></div>
    ${r.merkle_root ? `<div><div class="small muted">Merkle root</div><div class="mono root">${esc(r.merkle_root)}</div></div>` : ""}
    <div class="controls">
      <a class="btn" href="${esc(r.dossier_url)}" target="_blank" rel="noopener">Audit dossier (PDF)</a>
      ${r.next_script_id ? `<button class="btn primary" id="next-btn" type="button">Next script →</button>`
        : `<a class="btn primary" href="/coe" target="_blank" rel="noopener">Queue finished · open CoE</a>`}
    </div>`;
  $("#next-btn")?.addEventListener("click", () => openScript(r.next_script_id));
}

/* ---------- Page viewer & annotation canvas ---------- */

const img = $("#page-img");
const canvas = $("#ink");
const ctx = canvas.getContext("2d");

function showPage(i) {
  state.page = i;
  img.src = state.script.pages[i].url;
  renderPageTabs();
  drawInk();
}

function renderPageTabs() {
  $("#page-tabs").innerHTML = state.script.pages.map((p, i) => `
    <button class="page-tab" role="tab" type="button" data-page="${i}" aria-selected="${i === state.page}">
      <span class="seen ${state.dwell[i] >= 1 ? "on" : ""}"></span>Page ${i + 1}</button>`).join("");
}

$("#page-tabs").addEventListener("click", (e) => {
  const tab = e.target.closest("[data-page]");
  if (tab) showPage(+tab.dataset.page);
});

function sizeCanvas() {
  const r = img.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(r.width * dpr));
  canvas.height = Math.max(1, Math.round(r.height * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  drawInk();
}
img.addEventListener("load", sizeCanvas);
new ResizeObserver(sizeCanvas).observe(img);

function drawAnnotation(a, w, h) {
  const unit = w / 1240;
  const s = 22 * unit;
  const [x, y] = [a.points[0][0] * w, a.points[0][1] * h];
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  if (a.tool === "tick") {
    ctx.strokeStyle = "#168c3c";
    ctx.lineWidth = Math.max(2, 5 * unit);
    ctx.moveTo(x - s, y); ctx.lineTo(x - s * 0.3, y + s * 0.8); ctx.lineTo(x + s * 1.2, y - s);
    ctx.stroke();
  } else if (a.tool === "cross") {
    ctx.strokeStyle = "#d21e1e";
    ctx.lineWidth = Math.max(2, 5 * unit);
    ctx.moveTo(x - s, y - s); ctx.lineTo(x + s, y + s); ctx.moveTo(x - s, y + s); ctx.lineTo(x + s, y - s);
    ctx.stroke();
  } else if (a.tool === "pen") {
    ctx.strokeStyle = "#d21e1e";
    for (let i = 1; i < a.points.length; i++) {
      ctx.beginPath();
      ctx.lineWidth = Math.max(1.5, (2 + 4 * (a.pressure[i] ?? 0.5)) * unit);
      ctx.moveTo(a.points[i - 1][0] * w, a.points[i - 1][1] * h);
      ctx.lineTo(a.points[i][0] * w, a.points[i][1] * h);
      ctx.stroke();
    }
  } else if (a.tool === "note") {
    ctx.fillStyle = "#d21e1e";
    ctx.textBaseline = "top";
    ctx.font = `${Math.round(34 * unit)}px Kalam, cursive`;
    ctx.fillText(a.text, x, y - 20 * unit);
  }
}

function drawInk() {
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.width / dpr;
  const h = canvas.height / dpr;
  ctx.clearRect(0, 0, w, h);
  state.annotations.filter((a) => a.page === state.page).forEach((a) => drawAnnotation(a, w, h));
  if (state.drawing) drawAnnotation(state.drawing, w, h);
}

function normPoint(e) {
  const r = canvas.getBoundingClientRect();
  return [+((e.clientX - r.left) / r.width).toFixed(4), +((e.clientY - r.top) / r.height).toFixed(4)];
}

function addAnnotation(a) {
  state.annotations.push(a);
  drawInk();
  renderTotal();
}

canvas.addEventListener("pointerdown", (e) => {
  if (!state.script || state.submitted) return;
  const p = normPoint(e);
  if (state.tool === "pen") {
    canvas.setPointerCapture(e.pointerId);
    state.drawing = { page: state.page, tool: "pen", points: [p], pressure: [+(e.pressure || 0.5).toFixed(2)], text: "" };
  } else if (state.tool === "note") {
    state.pendingNote = p;
    $("#note-text").value = "";
    $("#note-dialog").showModal();
  } else {
    addAnnotation({ page: state.page, tool: state.tool, points: [p], pressure: [], text: "" });
  }
});
canvas.addEventListener("pointermove", (e) => {
  if (!state.drawing) return;
  const p = normPoint(e);
  const last = state.drawing.points[state.drawing.points.length - 1];
  if (Math.hypot(p[0] - last[0], p[1] - last[1]) < 0.002) return;
  state.drawing.points.push(p);
  state.drawing.pressure.push(+(e.pressure || 0.5).toFixed(2));
  drawInk();
});
const endStroke = () => {
  if (!state.drawing) return;
  const d = state.drawing;
  state.drawing = null;
  if (d.points.length > 1) addAnnotation(d); else drawInk();
};
canvas.addEventListener("pointerup", endStroke);
canvas.addEventListener("pointercancel", endStroke);

$("#note-dialog").addEventListener("close", () => {
  const text = $("#note-text").value.trim();
  if ($("#note-dialog").returnValue === "ok" && text && state.pendingNote) {
    addAnnotation({ page: state.page, tool: "note", points: [state.pendingNote], pressure: [], text });
  }
  state.pendingNote = null;
});

function setTool(tool) {
  state.tool = tool;
  document.querySelectorAll(".tool[data-tool]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.tool === tool)));
  canvas.classList.toggle("pen", tool === "pen");
}
document.querySelectorAll(".tool[data-tool]").forEach((b) => b.addEventListener("click", () => setTool(b.dataset.tool)));

function undo() {
  if (state.submitted) return;
  for (let i = state.annotations.length - 1; i >= 0; i--) {
    if (state.annotations[i].page === state.page) { state.annotations.splice(i, 1); break; }
  }
  drawInk();
  renderTotal();
}
$("#undo-btn").addEventListener("click", undo);

document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea, select") || document.querySelector("dialog[open]")) return;
  if ((e.ctrlKey || e.metaKey) && e.key === "z") { e.preventDefault(); undo(); return; }
  const tools = { t: "tick", x: "cross", p: "pen", n: "note" };
  if (tools[e.key]) setTool(tools[e.key]);
  if (state.script && e.key === "ArrowRight" && state.page < state.script.pages.length - 1) showPage(state.page + 1);
  if (state.script && e.key === "ArrowLeft" && state.page > 0) showPage(state.page - 1);
});

/* ---------- Dwell telemetry: seconds each page is actually on screen ---------- */

let lastTick = performance.now();
setInterval(() => {
  const now = performance.now();
  const dt = (now - lastTick) / 1000;
  lastTick = now;
  if (!state.script || state.submitted || document.hidden || state.script.status === "submitted") return;
  state.dwell[state.page] += dt;
  $("#timer").textContent = mmss(sum(state.dwell));
  document.querySelectorAll(".page-tab .seen").forEach((el, i) => el.classList.toggle("on", state.dwell[i] >= 1));
}, 250);

/* ---------- Upload ---------- */

$("#upload-btn").addEventListener("click", () => {
  const live = state.session?.engine.mode === "live";
  $("#upload-question").innerHTML = state.session.questions.map((q) => `<option value="${esc(q.id)}">${esc(q.id)} · ${esc(q.course)}</option>`).join("");
  $("#upload-hint").textContent = live
    ? "Photograph or scan the answer pages in order. The AI pre-reads them live."
    : "Uploads need live AI. Add GEMINI_API_KEY to the .env file and restart the server.";
  $("#upload-go").disabled = !live;
  $("#upload-form").reset();
  $("#upload-dialog").showModal();
});

$("#upload-dialog").addEventListener("close", async () => {
  if ($("#upload-dialog").returnValue !== "upload") return;
  const fd = new FormData();
  fd.append("question_id", $("#upload-question").value);
  for (const f of $("#upload-files").files) fd.append("files", f);
  try {
    const r = await api("/api/upload", { method: "POST", body: fd });
    await loadSession();
    openScript(r.script_id);
  } catch (err) {
    toast(`Upload failed: ${err.message}`, "error");
  }
});

/* ---------- Start ---------- */

(async () => {
  try {
    await loadSession();
  } catch (err) {
    toast(`Cannot reach the server: ${err.message}`, "error");
    return;
  }
  const want = new URLSearchParams(location.search).get("script");
  const id = want && state.session.queue.some((s) => s.script_id === want) ? want : state.session.next_script_id;
  if (id) {
    openScript(id);
  } else {
    $("#submit-bar").hidden = true;
    $("#done-card").hidden = false;
    $("#done-card").innerHTML = `<div class="callout good"><b><span class="icon good">✓</span>Your queue is finished</b>
      <div class="small">Open the CoE command centre to see the ledger, or reset the demo there.</div></div>
      <div class="controls"><a class="btn primary" href="/coe">Open CoE command centre</a></div>`;
  }
})();
