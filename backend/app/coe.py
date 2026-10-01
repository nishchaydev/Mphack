"""Controller of Examinations (CoE) dashboard data: the live examiner plus a labelled simulated cohort."""
import random
from functools import lru_cache
from statistics import mean

from .config import settings
from .sentinel import shannon_entropy
from .store import store

# (id, profile, scripts, mean dwell s, violations, seed gold, seed given, AI-accept rate)
_PROFILES = [
    ("EX-0211", "steady", 34, 96, 1, 12, 13, 0.58),
    ("EX-0388", "rubber_stamp", 40, 41, 3, 9, 14, 0.12),
    ("EX-0502", "speed", 58, 11, 31, 12, 12, 0.97),
    ("EX-0613", "lenient", 29, 88, 0, 9, 15, 0.44),
    ("EX-0745", "steady", 31, 104, 2, 12, 11.5, 0.66),
]


@lru_cache(maxsize=1)
def simulated_cohort() -> tuple[dict, ...]:
    rng = random.Random(2026)
    rows = []
    for ex_id, profile, n, dwell, violations, gold, given, accept in _PROFILES:
        if profile == "rubber_stamp":
            marks = [14.0 if rng.random() < 0.85 else rng.choice([13.0, 15.0]) for _ in range(n)]
        elif profile == "lenient":
            marks = [min(20.0, round(rng.gauss(15.5, 2.2) * 2) / 2) for _ in range(n)]
        else:
            marks = [max(0.0, min(20.0, round(rng.gauss(11.5, 3.4) * 2) / 2)) for _ in range(n)]
        rows.append({
            "id": ex_id, "profile": profile, "scripts": n, "marks": marks, "avg_dwell_s": dwell,
            "violations": violations, "shadow_mode": violations >= 10,
            "seed": {"gold_total": gold, "given_total": given, "max_marks": 20,
                     "drift": round(abs(given - gold) / 20, 3), "ai_total": gold - 0.5,
                     "ai_drift": 0.025},
            "accept_rate": accept, "decisions": n * 4,
        })
    return tuple(rows)


def _badges(entropy, drift_flag, shadow_mode, accept_rate, decisions, avg_dwell):
    out = []
    if shadow_mode:
        out.append({"label": "Tier 3 shadow review", "tone": "warn"})
    if drift_flag:
        out.append({"label": "Seed drift", "tone": "bad"})
    if entropy is not None and entropy < settings.entropy_flag_bits:
        out.append({"label": "Rubber-stamp pattern", "tone": "bad"})
    if accept_rate is not None and decisions >= 20 and accept_rate > 0.9 and avg_dwell is not None and avg_dwell < 30:
        out.append({"label": "Accepts AI without reading", "tone": "warn"})
    return out or [{"label": "OK", "tone": "ok"}]


def _examiner_rows() -> list[dict]:
    rows = []
    ex = store.examiner
    decisions = sum(ex.decisions.values())
    accept_rate = ex.decisions["accepted"] / decisions if decisions else None
    live_seed = next((s for s in reversed(store.seed_results) if s["examiner_id"] == ex.id), None)
    window = ex.totals[-settings.entropy_window:]
    entropy = shannon_entropy(window) if len(window) >= settings.entropy_min_samples else None
    avg_dwell = round(mean(ex.dwell_s), 1) if ex.dwell_s else None
    rows.append({
        "id": ex.id, "simulated": False, "scripts": len(ex.totals), "avg_dwell_s": avg_dwell,
        "violations": ex.violations, "entropy_bits": None if entropy is None else round(entropy, 2),
        "entropy_note": f"needs {settings.entropy_min_samples}+ scripts" if entropy is None else "",
        "seed_drift": live_seed["drift"] if live_seed else None,
        "accept_rate": None if accept_rate is None else round(accept_rate, 2),
        "badges": _badges(entropy, bool(live_seed and live_seed["flagged"]), ex.shadow_mode, accept_rate, decisions, avg_dwell),
    })
    for sim in simulated_cohort():
        window = sim["marks"][-settings.entropy_window:]
        entropy = shannon_entropy(window)
        drift_flag = sim["seed"]["drift"] > settings.seed_tolerance
        rows.append({
            "id": sim["id"], "simulated": True, "scripts": sim["scripts"], "avg_dwell_s": sim["avg_dwell_s"],
            "violations": sim["violations"], "entropy_bits": round(entropy, 2), "entropy_note": "",
            "seed_drift": sim["seed"]["drift"], "accept_rate": sim["accept_rate"],
            "badges": _badges(entropy, drift_flag, sim["shadow_mode"], sim["accept_rate"], sim["decisions"], sim["avg_dwell_s"]),
        })
    return rows


def _seed_rows() -> list[dict]:
    rows = [{**s, "simulated": False} for s in reversed(store.seed_results)]
    for sim in simulated_cohort():
        seed = sim["seed"]
        rows.append({
            "examiner_id": sim["id"], "script_id": "ANCHOR-B2", "simulated": True, **seed,
            "tolerance": settings.seed_tolerance, "flagged": seed["drift"] > settings.seed_tolerance,
            "ai_flagged": seed["ai_drift"] > settings.seed_tolerance,
        })
    return rows


def dashboard() -> dict:
    examiners = _examiner_rows()
    sim_shadow = [
        {"script_id": f"{sim['id'][-3:]}-{i:03d}", "examiner_id": sim["id"], "simulated": True,
         "reason": "Examiner under Tier 3 shadow review" if sim["shadow_mode"] else "Routed after a seed-script drift"}
        for sim in simulated_cohort()
        if sim["shadow_mode"] or sim["seed"]["drift"] > settings.seed_tolerance
        for i in (1, 2)
    ]
    submissions = [
        {"script_id": r["script_id"], "total": r["total"], "max_marks": r["max_marks"],
         "submitted_at": r["submitted_at"], "ledger_index": r["ledger_index"], "merkle_root": r["merkle_root"],
         "dossier_url": f"/api/scripts/{r['script_id']}/dossier.pdf"}
        for r in sorted(store.submissions.values(), key=lambda r: r["ledger_index"], reverse=True)
    ]
    seeds = _seed_rows()
    all_dwell = [e["avg_dwell_s"] for e in examiners if e["avg_dwell_s"] is not None]
    return {
        "kpis": {
            "scripts": sum(e["scripts"] for e in examiners),
            "examiners": len(examiners),
            "median_dwell_s": sorted(all_dwell)[len(all_dwell) // 2] if all_dwell else None,
            "velocity_flags": sum(e["violations"] for e in examiners),
            "seed_alerts": sum(1 for s in seeds if s["flagged"]),
            "shadow_queue": len(store.shadow_queue) + len(sim_shadow),
        },
        "examiners": examiners,
        "seeds": seeds,
        "shadow_queue": list(reversed(store.shadow_queue)) + sim_shadow,
        "submissions": submissions,
        "events": list(reversed(store.events))[:60],
        "ledger": {
            "length": len(store.ledger.entries),
            "head": store.ledger.head,
            "chain_ok": store.ledger.chain_ok(),
            "public_key_fingerprint": store.signer.fingerprint,
        },
        "engine": engine_info(),
    }


def engine_info() -> dict:
    return {
        "mode": "live" if settings.live_ai else "mock",
        "model": settings.gemini_model if settings.live_ai else None,
        "label": f"Gemini · {settings.gemini_model}" if settings.live_ai else "Demo responses (no API key)",
    }
