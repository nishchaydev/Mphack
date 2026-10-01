"""Examiner workflow: open a script, AI pre-read, submit, verify. Routes in main.py stay thin."""
import io
import secrets
import time

from fastapi import HTTPException
from PIL import Image

from .config import ROOT_DIR, RUNTIME_DIR, settings
from .grading import AIUnavailable, _mime
from .grading import preread as run_preread
from .integrity import evidence_leaves, merkle_root
from .schemas import PreRead, ScriptRecord, Submission
from .sentinel import assess_velocity, check_seed
from .store import now_iso, store

MAX_UPLOAD_BYTES = 12 * 1024 * 1024


def get_script(script_id: str) -> ScriptRecord:
    script = store.scripts.get(script_id)
    if script is None:
        raise HTTPException(404, f"Unknown script {script_id}")
    return script


def queue_view() -> list[dict]:
    # Never expose is_seed or gold: seed scripts must look like any other script.
    return [
        {
            "script_id": s.script_id,
            "question_id": s.question_id,
            "pages": len(s.pages),
            "status": "submitted" if s.script_id in store.submissions else "pending",
            "uploaded": s.uploaded,
        }
        for s in store.scripts.values()
    ]


def next_pending() -> str | None:
    return next((s.script_id for s in store.scripts.values() if s.script_id not in store.submissions), None)


def open_script(script_id: str) -> dict:
    script = get_script(script_id)
    question = store.questions[script.question_id]
    if script_id not in store.opened_at:
        store.opened_at[script_id] = time.monotonic()
        store.emit("SCRIPT_OPENED", script_id=script_id, examiner_id=store.examiner.id)
    record = store.submissions.get(script_id)
    return {
        "script_id": script_id,
        "question": question.model_dump(),
        "pages": [{"n": i, "url": f"/api/scripts/{script_id}/pages/{i}"} for i in range(1, len(script.pages) + 1)],
        "status": "submitted" if record else "pending",
        "submitted": {"total": record["total"], "ledger_index": record["ledger_index"]} if record else None,
    }


def get_preread(script_id: str) -> PreRead:
    if script_id in store.prereads:
        return store.prereads[script_id]
    script = get_script(script_id)
    question = store.questions[script.question_id]
    try:
        result = run_preread(script_id, question, store.page_bytes(script))
    except AIUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    store.prereads[script_id] = result
    store.emit("AI_PREREAD_COMPLETED", script_id=script_id, engine=result.engine_kind,
               suggested_total=result.suggested_total, needs_review=result.needs_human_review)
    if result.injection_suspected:
        store.emit("INJECTION_FLAGGED", script_id=script_id, matches=result.injection_matches[:3])
    return result


def _reject(status: int, code: str, message: str, **extra) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message, **extra})


def submit(script_id: str, sub: Submission) -> dict:
    script = get_script(script_id)
    if script_id in store.submissions:
        raise _reject(409, "ALREADY_SUBMITTED", "This script has already been submitted.")
    question = store.questions[script.question_id]
    pr = get_preread(script_id)
    ex = store.examiner

    # 1. Bounds at the API boundary: no criterion can exceed its maximum (the "1604 / 1600" guard).
    rubric = {r.id: r for r in question.rubric}
    if sorted(m.criterion_id for m in sub.marks) != sorted(rubric):
        raise _reject(422, "RUBRIC_MISMATCH", "Marks must cover each rubric criterion exactly once.")
    for m in sub.marks:
        top = rubric[m.criterion_id].max
        if m.marks > top:
            store.emit("MARKS_REJECTED", script_id=script_id, criterion_id=m.criterion_id, marks=m.marks, max=top)
            raise _reject(422, "MARKS_OUT_OF_BOUNDS",
                          f"{m.criterion_id}: {m.marks:g} is more than the maximum of {top:g}. "
                          "Rejected before it can reach the tabulation register.")
        if m.marks * 2 != int(m.marks * 2):
            raise _reject(422, "MARKS_STEP", f"{m.criterion_id}: marks must be in steps of 0.5.")
    if len(sub.telemetry.page_dwell_s) != len(script.pages):
        raise _reject(422, "TELEMETRY_MISMATCH", "Page telemetry does not match the number of pages.")

    # 2. Velocity sentinel. Dwell is capped by the server's own clock, so a client cannot inflate it.
    server_elapsed = time.monotonic() - store.opened_at.get(script_id, time.monotonic())
    dwell = min(sub.telemetry.active_s, server_elapsed)
    touchpoint = any(m.verified for m in sub.marks) or bool(sub.annotations)
    velocity = assess_velocity(dwell, pr.reading_floor_s, sub.telemetry.page_dwell_s, touchpoint)
    tier = velocity["tier"]
    if (tier == 2 and not touchpoint) or tier > sub.acknowledged_tier:
        code = "VELOCITY_GATE" if tier == 2 else "VELOCITY_NUDGE"
        store.emit(code, script_id=script_id, examiner_id=ex.id, dwell_s=velocity["dwell_s"], floor_s=velocity["floor_s"])
        raise _reject(409, code, "Submitted faster than the reading floor.", velocity=velocity)

    # 3. Record the evaluation.
    total = sum(m.marks for m in sub.marks)
    ai_marks = {c.criterion_id: c.suggested for c in pr.criteria}
    for m in sub.marks:
        ex.decisions[m.decision] += 1
    record = {
        "script_id": script_id,
        "question_id": question.id,
        "examiner_id": ex.id,
        "marks": [m.model_dump() for m in sub.marks],
        "total": total,
        "max_marks": question.max_marks,
        "annotations": [a.model_dump() for a in sub.annotations],
        "telemetry": {**sub.telemetry.model_dump(), "server_elapsed_s": round(server_elapsed, 1)},
        "velocity": {**velocity, "acknowledged_tier": sub.acknowledged_tier},
        "preread": pr.model_dump(),
        "submitted_at": now_iso(),
    }

    # 4. Silent quality controls: shadow routing, Tier 3, blind seed check. Nothing here is shown to the examiner.
    reasons = []
    if ex.shadow_remaining > 0:
        reasons.append("Routed after a seed-script drift")
        ex.shadow_remaining -= 1
    if ex.shadow_mode:
        reasons.append("Examiner under Tier 3 shadow review")
    violation = tier >= 1
    ex.recent_violations.append(violation)
    ex.violations += int(violation)
    if not ex.shadow_mode and sum(ex.recent_violations) >= settings.tier3_violations:
        ex.shadow_mode = True
        reasons.append("Tier 3: repeated rapid submissions")
        store.emit("TIER3_SHADOW_REVIEW", examiner_id=ex.id)
    if script.is_seed and script.gold:
        seed = check_seed(script, {m.criterion_id: m.marks for m in sub.marks}, ai_marks, question.max_marks)
        seed.update(examiner_id=ex.id, ts=now_iso(), simulated=False)
        store.seed_results.append(seed)
        if seed["flagged"]:
            ex.shadow_remaining += settings.shadow_route_count
            store.emit("SEED_DRIFT_DETECTED", examiner_id=ex.id, script_id=script_id, drift=seed["drift"])
    record["shadow_review"] = "; ".join(reasons) or None
    if reasons:
        store.shadow_queue.append({"script_id": script_id, "examiner_id": ex.id, "reason": record["shadow_review"],
                                   "ts": now_iso(), "simulated": False})
        store.emit("SHADOW_REVIEW_ROUTED", script_id=script_id, examiner_id=ex.id)

    # 5. Tamper evidence: hash every artefact, sign the Merkle root, append to the ledger.
    leaves = evidence_leaves(store.page_bytes(script), record)
    root = merkle_root([h for _, h in leaves])
    signature = store.signer.sign(root)
    entry = store.ledger.append(script_id, root, signature, leaves)
    record.update(ledger_index=entry["index"], merkle_root=root, signature=signature)
    store.submissions[script_id] = record
    ex.totals.append(total)
    ex.dwell_s.append(dwell)

    store.emit("SCRIPT_SUBMITTED", script_id=script_id, examiner_id=ex.id, total=total,
               max_marks=question.max_marks, dwell_s=round(dwell, 1), velocity_tier=tier)
    store.emit("LEDGER_APPENDED", script_id=script_id, index=entry["index"], merkle_root=root[:16])

    return {
        "script_id": script_id,
        "total": total,
        "max_marks": question.max_marks,
        "ledger_index": entry["index"],
        "merkle_root": root,
        "dossier_url": f"/api/scripts/{script_id}/dossier.pdf",
        "next_script_id": next_pending(),
    }


def verify(script_id: str, emit: bool = True) -> dict:
    record = store.submissions.get(script_id)
    entry = store.ledger.find(script_id)
    if record is None or entry is None:
        raise HTTPException(404, "Script has not been submitted yet.")
    current = evidence_leaves(store.page_bytes(get_script(script_id)), record)
    stored = dict(entry["leaves"])
    leaves = [{"name": n, "stored": stored.get(n), "current": h, "ok": stored.get(n) == h} for n, h in current]
    current_root = merkle_root([h for _, h in current])
    result = {
        "script_id": script_id,
        "ledger_index": entry["index"],
        "merkle_root": entry["merkle_root"],
        "current_root": current_root,
        "root_ok": current_root == entry["merkle_root"],
        "signature_ok": store.signer.verify(entry["merkle_root"], entry["signature"]),
        "chain_ok": store.ledger.chain_ok(),
        "leaves": leaves,
        "checked_at": now_iso(),
    }
    result["ok"] = result["root_ok"] and result["signature_ok"] and result["chain_ok"] and all(l["ok"] for l in leaves)
    if emit:
        store.emit("INTEGRITY_VERIFIED" if result["ok"] else "TAMPER_DETECTED", script_id=script_id)
    return result


def tamper(script_id: str) -> dict:
    """Demo only: edit stored marks behind the system's back, like an insider editing the database."""
    record = store.submissions.get(script_id)
    if record is None:
        raise HTTPException(404, "Script has not been submitted yet.")
    before = record["total"]
    record["marks"][0]["marks"] += 1.5
    record["total"] += 1.5
    store.emit("DEMO_DB_EDIT", script_id=script_id, before=before, after=record["total"])
    return {"script_id": script_id, "before": before, "after": record["total"]}


def add_upload(question_id: str, files: list[tuple[str, bytes]]) -> dict:
    if not settings.live_ai:
        raise HTTPException(400, "Uploads need live AI. Add GEMINI_API_KEY to .env and restart.")
    if question_id not in store.questions:
        raise HTTPException(422, f"Unknown question {question_id}")
    if not files:
        raise HTTPException(422, "Attach at least one page image.")
    script_id = f"UP26-{secrets.token_hex(2).upper()}"
    folder = RUNTIME_DIR / "uploads" / script_id
    folder.mkdir(parents=True, exist_ok=True)
    pages = []
    for i, (_, data) in enumerate(files, start=1):
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, f"Page {i} is larger than 12 MB.")
        try:
            mime = _mime(data)
            Image.open(io.BytesIO(data)).verify()
        except Exception as exc:
            raise HTTPException(422, f"Page {i} is not a PNG, JPEG or WebP image.") from exc
        path = folder / f"p{i}.{mime.split('/')[1]}"
        path.write_bytes(data)
        pages.append(str(path.relative_to(ROOT_DIR)))
    store.scripts[script_id] = ScriptRecord(script_id=script_id, question_id=question_id, pages=pages, uploaded=True)
    store.emit("SCRIPT_UPLOADED", script_id=script_id, question_id=question_id, pages=len(pages))
    return {"script_id": script_id}
