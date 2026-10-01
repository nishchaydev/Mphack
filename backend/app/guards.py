"""Server-side checks on AI output. The model only suggests; nothing it returns is trusted as-is."""
import re
import unicodedata
from difflib import SequenceMatcher

from .config import settings
from .schemas import AIEvaluation, CriterionSuggestion, EvidenceQuote, Question

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(the\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"(award|give|assign)\s+(me\s+)?(full|maximum|max|all|\d+\s*/\s*\d+)\s+marks",
    r"full\s+marks",
    r"system\s+prompt",
    r"you\s+are\s+(now\s+)?(an?\s+)?(ai|assistant|language\s+model|evaluator)",
    r"पिछले\s+(सभी\s+)?निर्देश",
    r"निर्देशों?\s+को\s+(अनदेखा|नज़रअंदाज़|नजरअंदाज)",
    r"पूरे\s+(\d+\s*/\s*\d+\s+)?अंक",
    r"पूर्ण\s+अंक",
    r"(परीक्षक|AI|एआई)\s+(के\s+लिए|हेतु)\s+निर्देश",
]
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
_BRACKETED = re.compile(r"\[[^\]]*\]")


def scan_injection(text: str) -> list[str]:
    """Return the phrases in the transcription that look like instructions to the grader."""
    hits = []
    for rx in _INJECTION_RE:
        for m in rx.finditer(text):
            hits.append(m.group(0))
    return list(dict.fromkeys(hits))


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    return "".join(ch for ch in text if not (ch.isspace() or unicodedata.category(ch).startswith("P") or ch in "।॥"))


def is_grounded(quote: str, transcription: str, threshold: float = 0.85) -> bool:
    """True if the quote appears (near-)verbatim in the transcription."""
    q, t = _normalise(quote), _normalise(transcription)
    if not q:
        return False
    if q in t:
        return True
    match = SequenceMatcher(None, q, t, autojunk=False).find_longest_match(0, len(q), 0, len(t))
    return match.size / len(q) >= threshold


def count_words(transcription: str) -> int:
    return len(_BRACKETED.sub(" ", transcription).split())


def _half_step(value: float) -> float:
    return round(value * 2) / 2


def apply_guards(raw: AIEvaluation, question: Question) -> dict:
    """Clamp marks to the rubric, check every quote against the transcription, flag injections."""
    by_id = {c.criterion_id: c for c in raw.criteria}
    reasons: list[str] = []
    criteria: list[CriterionSuggestion] = []

    unknown = sorted(set(by_id) - {r.id for r in question.rubric})
    if unknown:
        reasons.append(f"Model returned unknown criteria {', '.join(unknown)}; ignored.")

    for rub in question.rubric:
        flags: list[str] = []
        c = by_id.get(rub.id)
        if c is None:
            flags.append("Model gave no mark for this criterion; set to 0.")
            awarded, evidence_in, reasoning, missing = 0.0, [], "", ""
        else:
            awarded, evidence_in, reasoning, missing = c.awarded, c.evidence, c.reasoning, c.missing

        suggested = _half_step(min(max(awarded, 0.0), rub.max))
        if suggested != awarded:
            flags.append(f"AI suggested {awarded:g}; clamped to {suggested:g} (max {rub.max:g}).")

        evidence = []
        for quote in evidence_in:
            quote = quote.strip()
            if not quote:
                continue
            if quote.lower().startswith("[diagram"):
                evidence.append(EvidenceQuote(text=quote, kind="diagram", grounded=True))
            else:
                evidence.append(EvidenceQuote(text=quote, kind="text", grounded=is_grounded(quote, raw.transcription)))
        if any(not e.grounded for e in evidence):
            flags.append("A quoted line was not found in the transcription. Check it on the script.")
        if suggested > 0 and not any(e.grounded for e in evidence):
            flags.append("Marks suggested without supporting evidence.")

        criteria.append(CriterionSuggestion(
            criterion_id=rub.id, name=rub.name, max=rub.max, description=rub.description,
            suggested=suggested, evidence=evidence, reasoning=reasoning, missing=missing, flags=flags,
        ))
        if flags:
            reasons.append(f"{rub.id}: {flags[0]}")

    matches = scan_injection(raw.transcription)
    injection = raw.injection_suspected or bool(matches)
    if injection:
        reasons.insert(0, "The answer contains text addressed to the examiner or the AI. It was ignored for marking.")

    confidence = min(max(raw.confidence, 0.0), 1.0)
    if confidence < settings.low_confidence:
        reasons.append(f"Low AI confidence ({confidence:.2f}).")
    if raw.legibility != "clear":
        reasons.append(f"Handwriting marked '{raw.legibility.replace('_', ' ')}'.")

    total = sum(c.suggested for c in criteria)
    assert total <= question.max_marks + 1e-9

    return {
        "criteria": criteria,
        "suggested_total": total,
        "confidence": confidence,
        "word_count": count_words(raw.transcription),
        "injection_suspected": injection,
        "injection_matches": matches,
        "needs_human_review": bool(reasons),
        "review_reasons": reasons,
    }
