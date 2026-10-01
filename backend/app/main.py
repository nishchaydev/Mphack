"""PARIKSHAK-AI proof of concept: FastAPI backend that also serves the examiner and CoE pages.

Run from the repo root:  .venv/bin/uvicorn app.main:app --app-dir backend --port 8000
"""
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from . import coe, workflow
from .config import FONTS_DIR, FRONTEND_DIR, ROOT_DIR
from .dossier import build_dossier
from .schemas import PreRead, Submission
from .store import store

app = FastAPI(title="PARIKSHAK-AI POC", version="0.1.0")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/fonts", StaticFiles(directory=FONTS_DIR), name="fonts")


@app.get("/", include_in_schema=False)
def examiner_page():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/coe", include_in_schema=False)
def coe_page():
    return FileResponse(FRONTEND_DIR / "coe.html")


@app.get("/api/health")
def health():
    return {"ok": True, "engine": coe.engine_info()}


@app.get("/api/session")
def session():
    return {
        "examiner": {"id": store.examiner.id, "name": store.examiner.name},
        "engine": coe.engine_info(),
        "queue": workflow.queue_view(),
        "next_script_id": workflow.next_pending(),
        "questions": [{"id": q.id, "course": q.course, "text_en": q.text_en} for q in store.questions.values()],
    }


@app.get("/api/scripts/{script_id}")
def open_script(script_id: str):
    return workflow.open_script(script_id)


@app.get("/api/scripts/{script_id}/pages/{n}", include_in_schema=False)
def page_image(script_id: str, n: int):
    script = workflow.get_script(script_id)
    if not 1 <= n <= len(script.pages):
        return Response(status_code=404)
    return FileResponse(ROOT_DIR / script.pages[n - 1], headers={"Cache-Control": "no-store"})


@app.post("/api/scripts/{script_id}/preread", response_model=PreRead)
def preread(script_id: str):
    return workflow.get_preread(script_id)


@app.post("/api/scripts/{script_id}/submit")
def submit(script_id: str, submission: Submission):
    return workflow.submit(script_id, submission)


@app.get("/api/scripts/{script_id}/verify")
def verify(script_id: str):
    return workflow.verify(script_id)


@app.get("/api/scripts/{script_id}/dossier.pdf")
def dossier(script_id: str):
    script = workflow.get_script(script_id)
    verification = workflow.verify(script_id, emit=False)
    record = store.submissions[script_id]
    pdf = build_dossier(script, store.questions[script.question_id], record, store.page_bytes(script),
                        verification, store.ledger.find(script_id), store.signer.fingerprint)
    store.emit("DOSSIER_GENERATED", script_id=script_id, integrity_ok=verification["ok"])
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="dossier_{script_id}.pdf"'})


@app.post("/api/upload")
async def upload(question_id: str = Form(...), files: list[UploadFile] = File(...)):
    pages = [(f.filename or "page", await f.read()) for f in files]
    return workflow.add_upload(question_id, pages)


@app.get("/api/coe")
def coe_dashboard():
    return coe.dashboard()


@app.post("/api/demo/tamper/{script_id}")
def demo_tamper(script_id: str):
    return workflow.tamper(script_id)


@app.post("/api/demo/reset")
def demo_reset():
    store.reset()
    return {"ok": True}
