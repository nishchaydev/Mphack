"""Examiner integrity checks: reading-speed floor, blind seed scripts, rubber-stamp entropy."""
import math
from collections import Counter

from .config import settings
from .schemas import ScriptRecord


def reading_floor(word_count: int, equation_count: int = 0, diagram_count: int = 0) -> float:
    """Seconds a careful first read of this answer needs (the team's T_min formula)."""
    s = settings
    return round(
        word_count / s.reading_wpm * 60
        + equation_count * s.seconds_per_equation
        + diagram_count * s.seconds_per_diagram
        + s.base_seconds,
        1,
    )


def assess_velocity(dwell_s: float, floor_s: float, page_dwell_s: list[float], touchpoint: bool) -> dict:
    """Tier 0 = fine, 1 = soft nudge, 2 = touchpoint gate. Tier 3 is decided across scripts."""
    nudge_at = floor_s * settings.nudge_fraction
    gate_at = floor_s * settings.gate_fraction
    unviewed = [i + 1 for i, t in enumerate(page_dwell_s) if t < 1.0]
    tier = 2 if dwell_s < gate_at else 1 if dwell_s < nudge_at else 0
    if unviewed and tier == 0:
        tier = 1
    return {
        "tier": tier,
        "dwell_s": round(dwell_s, 1),
        "floor_s": floor_s,
        "nudge_at_s": round(nudge_at, 1),
        "gate_at_s": round(gate_at, 1),
        "unviewed_pages": unviewed,
        "touchpoint": touchpoint,
    }


def check_seed(script: ScriptRecord, final: dict[str, float], ai: dict[str, float], max_marks: float) -> dict:
    """Compare the examiner (and the AI) against the Chief Examiner's marks on an anchor script."""
    gold = script.gold or {}
    gold_total, given_total, ai_total = sum(gold.values()), sum(final.values()), sum(ai.values())
    drift = abs(given_total - gold_total) / max_marks
    ai_drift = abs(ai_total - gold_total) / max_marks
    return {
        "script_id": script.script_id,
        "gold_total": gold_total,
        "given_total": given_total,
        "ai_total": ai_total,
        "max_marks": max_marks,
        "drift": round(drift, 3),
        "ai_drift": round(ai_drift, 3),
        "tolerance": settings.seed_tolerance,
        "flagged": drift > settings.seed_tolerance,
        "ai_flagged": ai_drift > settings.seed_tolerance,
        "criteria": [
            {"criterion_id": cid, "gold": g, "given": final.get(cid, 0.0), "ai": ai.get(cid, 0.0)}
            for cid, g in gold.items()
        ],
    }


def shannon_entropy(values: list[float]) -> float:
    """Bits of spread in an examiner's marks. Everyone getting 14/20 gives 0."""
    if not values:
        return 0.0
    n = len(values)
    return abs(-sum(c / n * math.log2(c / n) for c in Counter(values).values()))
