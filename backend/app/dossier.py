"""One-click evaluation audit dossier (PDF) for RTI replies and court challenges."""
import io
from datetime import datetime, timezone

from fpdf import FPDF, FontFace
from fpdf.enums import XPos, YPos
from PIL import Image, ImageDraw, ImageFont

from .config import FONTS_DIR
from .schemas import Question, ScriptRecord

INK = (31, 41, 55)
MUTED = (107, 114, 128)
ACCENT = (30, 58, 138)
GOOD = (21, 128, 61)
BAD = (185, 28, 28)
RULE = (209, 213, 219)
HEAD = FontFace(emphasis="BOLD", color=ACCENT, fill_color=(243, 244, 246))
DECISION = {"accepted": "Accepted AI", "modified": "Modified", "overridden": "Overridden"}


def render_page(image_bytes: bytes, annotations: list[dict]) -> bytes:
    """Burn the examiner's ticks, crosses, pen strokes and notes onto the scanned page."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    d = ImageDraw.Draw(img)
    unit = w / 1240
    note_font = ImageFont.truetype(str(FONTS_DIR / "Kalam-Regular.ttf"), int(34 * unit),
                                   layout_engine=ImageFont.Layout.RAQM)
    green, red = (22, 140, 60), (210, 30, 30)
    for a in annotations:
        pts = [(min(max(x, 0), 1) * w, min(max(y, 0), 1) * h) for x, y in a["points"]]
        if not pts:
            continue
        x, y = pts[0]
        s = 22 * unit
        if a["tool"] == "tick":
            d.line([(x - s, y), (x - s * 0.3, y + s * 0.8), (x + s * 1.2, y - s)], fill=green, width=int(5 * unit), joint="curve")
        elif a["tool"] == "cross":
            d.line([(x - s, y - s), (x + s, y + s)], fill=red, width=int(5 * unit))
            d.line([(x - s, y + s), (x + s, y - s)], fill=red, width=int(5 * unit))
        elif a["tool"] == "pen" and len(pts) > 1:
            p = a.get("pressure") or [0.5]
            d.line(pts, fill=red, width=max(2, int((2 + 4 * sum(p) / len(p)) * unit)), joint="curve")
        elif a["tool"] == "note" and a.get("text"):
            d.text((x, y - 20 * unit), a["text"], font=note_font, fill=red)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=82)
    return out.getvalue()


class _PDF(FPDF):
    script_id = ""

    def header(self):
        self.set_font("Mukta", size=8)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f"PARIKSHAK-AI · Evaluation audit dossier · {self.script_id}", new_x=XPos.LMARGIN, new_y=YPos.TOP)
        self.cell(0, 5, f"Page {self.page_no()}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Mukta", size=7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, "Proof-of-concept build. Synthetic demo data. Not an official university record.", align="C")


def _heading(pdf: FPDF, text: str) -> None:
    pdf.ln(3)
    pdf.set_font("Mukta", "B", 12)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*RULE)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    pdf.set_text_color(*INK)


def _para(pdf: FPDF, text: str, size: float = 9.5, color=INK, style: str = "") -> None:
    pdf.set_font("Mukta", style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, size * 0.55, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _kv_table(pdf: FPDF, rows: list[tuple[str, str]]) -> None:
    pdf.set_font("Mukta", size=9)
    pdf.set_draw_color(*RULE)
    with pdf.table(col_widths=(45, 135), first_row_as_headings=False, line_height=5.2,
                   borders_layout="HORIZONTAL_LINES") as table:
        for k, v in rows:
            row = table.row()
            row.cell(k)
            row.cell(v)


def _mono(pdf: FPDF, text: str, size: float = 7.5) -> None:
    pdf.set_font("Courier", size=size)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, size * 0.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_dossier(script: ScriptRecord, question: Question, record: dict, pages: list[bytes],
                  verification: dict, ledger_entry: dict, fingerprint: str) -> bytes:
    pr = record["preread"]
    pdf = _PDF(format="A4")
    pdf.script_id = script.script_id
    pdf.set_margins(15, 12, 15)
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_font("Mukta", fname=str(FONTS_DIR / "Mukta-Regular.ttf"))
    pdf.add_font("Mukta", "B", fname=str(FONTS_DIR / "Mukta-Bold.ttf"))
    pdf.set_text_shaping(use_shaping_engine=True, script="deva", language="hin")
    pdf.add_page()

    pdf.set_font("Mukta", "B", 18)
    pdf.set_text_color(*INK)
    pdf.cell(0, 9, "Evaluation Audit Dossier · मूल्यांकन ऑडिट अभिलेख", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    _para(pdf, "Electronic record prepared to support a certificate under Section 63, Bharatiya Sakshya Adhiniyam 2023.",
          9, MUTED)
    pdf.ln(2)

    ok = verification["ok"]
    pdf.set_fill_color(*(GOOD if ok else BAD))
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Mukta", "B", 10)
    leaves_ok = sum(1 for l in verification["leaves"] if l["ok"])
    status = (f"INTEGRITY CHECK PASSED: all {leaves_ok} hashes match ledger entry #{verification['ledger_index']}, "
              "signature valid, ledger chain intact." if ok else
              f"INTEGRITY CHECK FAILED: {len(verification['leaves']) - leaves_ok} of {len(verification['leaves'])} hashes "
              f"no longer match ledger entry #{verification['ledger_index']}. The stored record was changed after submission.")
    pdf.multi_cell(0, 6, status, fill=True, padding=2, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(*INK)
    pdf.ln(2)

    _kv_table(pdf, [
        ("Booklet (fictitious code)", script.script_id),
        ("Course", question.course),
        ("Examiner (pseudonym)", record["examiner_id"]),
        ("AI pre-read engine", pr["engine"]),
        ("Submitted at (UTC)", record["submitted_at"]),
        ("Final marks", f"{record['total']:g} / {record['max_marks']:g}   (AI suggested {pr['suggested_total']:g})"),
    ])

    _heading(pdf, "Question")
    _para(pdf, question.text, 10)
    _para(pdf, question.text_en, 9, MUTED)

    _heading(pdf, "Marks by rubric criterion")
    marks = {m["criterion_id"]: m for m in record["marks"]}
    pdf.set_font("Mukta", size=9)
    with pdf.table(col_widths=(62, 16, 24, 18, 32, 28), text_align=("LEFT", "CENTER", "CENTER", "CENTER", "LEFT", "CENTER"),
                   line_height=5.4, borders_layout="HORIZONTAL_LINES", headings_style=HEAD) as table:
        head = table.row()
        for h in ("Criterion", "Max", "AI suggested", "Final", "Decision", "Checked on script"):
            head.cell(h)
        for c in pr["criteria"]:
            m = marks[c["criterion_id"]]
            row = table.row()
            row.cell(f"{c['criterion_id']} · {c['name']}")
            row.cell(f"{c['max']:g}")
            row.cell(f"{c['suggested']:g}")
            row.cell(f"{m['marks']:g}")
            row.cell(DECISION[m["decision"]])
            row.cell("Yes" if m["verified"] else "")

    _heading(pdf, "Evidence the marks rest on (quoted from the script)")
    for c in pr["criteria"]:
        _para(pdf, f"{c['criterion_id']} · {c['name']}", 9.5, ACCENT, "B")
        for e in c["evidence"]:
            mark = "" if e["grounded"] else "  [not found in transcription]"
            _para(pdf, f"“{e['text']}”{mark}", 9.5)
        if not c["evidence"]:
            _para(pdf, "No supporting text found.", 9, MUTED)
        if c["reasoning"]:
            _para(pdf, f"AI reasoning: {c['reasoning']}", 8.5, MUTED)
        if c["missing"]:
            _para(pdf, f"Missing for full marks: {c['missing']}", 8.5, MUTED)
        pdf.ln(1)

    if pr["review_reasons"]:
        _heading(pdf, "Flags raised for the examiner")
        for r in pr["review_reasons"]:
            _para(pdf, f"•  {r}", 9)

    _heading(pdf, "Reading time")
    v, t = record["velocity"], record["telemetry"]
    per_page = ", ".join(f"page {i} {s:.0f}s" for i, s in enumerate(t["page_dwell_s"], start=1))
    tier_text = {0: "none", 1: "Tier 1 nudge shown", 2: "Tier 2 verification gate shown"}[v["tier"]]
    _kv_table(pdf, [
        ("Answer length", f"{pr['word_count']} words, {pr['equation_count']} equations, {pr['diagram_count']} diagrams"),
        ("Reading floor", f"{v['floor_s']:g} s (nudge below {v['nudge_at_s']:g} s, gate below {v['gate_at_s']:g} s)"),
        ("Time on script", f"{v['dwell_s']:g} s ({per_page}); server clock {t['server_elapsed_s']:g} s"),
        ("Speed check", tier_text + (", acknowledged by examiner" if v["acknowledged_tier"] else "")),
    ])

    for i, (page, img) in enumerate(zip(script.pages, pages), start=1):
        pdf.add_page()
        _heading(pdf, f"Scanned page {i} with examiner annotations")
        page_annots = [a for a in record["annotations"] if a["page"] == i - 1]
        jpeg = render_page(img, page_annots)
        width = 150
        pdf.image(io.BytesIO(jpeg), x=(pdf.w - width) / 2, w=width)
        leaf = next(l for l in verification["leaves"] if l["name"] == f"page_{i}_image")
        _para(pdf, f"SHA-256 of original scan: {leaf['stored']}", 7.5, MUTED)

    pdf.add_page()
    _heading(pdf, "Integrity proof")
    _para(pdf, "Each artefact below was hashed with SHA-256 when the examiner submitted. The hashes form a Merkle tree "
               "whose root was signed and appended to a hash-chained ledger. Re-hashing the stored record today must "
               "give the same values.", 9)
    pdf.ln(1)
    pdf.set_font("Mukta", size=8.5)
    with pdf.table(col_widths=(32, 132, 16), text_align=("LEFT", "LEFT", "CENTER"), line_height=5,
                   borders_layout="HORIZONTAL_LINES", headings_style=HEAD) as table:
        head = table.row()
        for h in ("Artefact", "SHA-256 recorded at submission", "Now"):
            head.cell(h)
        for l in verification["leaves"]:
            row = table.row()
            row.cell(l["name"].replace("_", " "))
            row.cell(l["stored"] or "missing")
            row.cell("match" if l["ok"] else "CHANGED")
    pdf.ln(3)
    _para(pdf, "Merkle root (recorded)", 9, ACCENT, "B")
    _mono(pdf, ledger_entry["merkle_root"])
    if not verification["root_ok"]:
        _para(pdf, "Merkle root recomputed now", 9, BAD, "B")
        _mono(pdf, verification["current_root"])
    _para(pdf, "Ed25519 signature over the root", 9, ACCENT, "B")
    _mono(pdf, ledger_entry["signature"])
    _para(pdf, f"Signing key fingerprint: {fingerprint}   ·   Signature valid: {'yes' if verification['signature_ok'] else 'NO'}", 8.5)
    _para(pdf, "Ledger entry", 9, ACCENT, "B")
    _mono(pdf, f"index {ledger_entry['index']}  at {ledger_entry['ts']}\nentry {ledger_entry['entry_hash']}\nprev  {ledger_entry['prev_hash']}")

    _heading(pdf, "Section 63 certificate: what this system supplies")
    _para(pdf, "Section 63(4) of the Bharatiya Sakshya Adhiniyam 2023 requires a certificate in the form in its Schedule, "
               "signed by the person in charge of the computer resource (Part A) and by an expert (Part B). This dossier "
               "is not that certificate. It pre-fills the technical particulars they attest to:", 9)
    _kv_table(pdf, [
        ("Hash algorithm", "SHA-256 (Merkle tree), signature Ed25519"),
        ("Hash value of the record", ledger_entry["merkle_root"]),
        ("System", "PARIKSHAK-AI proof of concept, examiner workspace and evaluation ledger"),
        ("Generated (UTC)", datetime.now(timezone.utc).isoformat(timespec="seconds")),
    ])
    return bytes(pdf.output())
