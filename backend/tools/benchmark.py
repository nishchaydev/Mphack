"""Measure the AI pre-read against a teacher's marks on your own handwritten scripts.

Needs GEMINI_API_KEY. Make a CSV with one row per answer:

    script_id,question_id,teacher_total,pages
    T01,Q1,7.5,photos/t01_p1.jpg|photos/t01_p2.jpg
    T02,Q2,4,photos/t02_p1.jpg

Page paths are relative to the CSV file. Then run from the repo root:

    .venv/bin/python backend/tools/benchmark.py benchmark/scripts.csv

Reports agreement with the teacher (exact, within 1 mark, mean absolute error, quadratic weighted
kappa on whole marks), latency and measured cost per answer. Quote these numbers, not invented ones.
"""
import csv
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import grading  # noqa: E402
from app.config import settings  # noqa: E402
from app.store import load_questions  # noqa: E402


def quadratic_weighted_kappa(a: list[int], b: list[int], top: int) -> float:
    n = top + 1
    observed = [[0] * n for _ in range(n)]
    for x, y in zip(a, b):
        observed[x][y] += 1
    hist_a = [sum(row) for row in observed]
    hist_b = [sum(observed[i][j] for i in range(n)) for j in range(n)]
    total = len(a)
    num = den = 0.0
    for i in range(n):
        for j in range(n):
            w = (i - j) ** 2 / (n - 1) ** 2
            num += w * observed[i][j]
            den += w * hist_a[i] * hist_b[j] / total
    return 1.0 - num / den if den else 1.0


def main(csv_path: str) -> None:
    if not settings.live_ai:
        sys.exit("Set GEMINI_API_KEY in .env first. The benchmark only makes sense against the live model.")
    questions = load_questions()
    base = Path(csv_path).resolve().parent
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    results = []
    for row in rows:
        q = questions[row["question_id"]]
        pages = [(base / p.strip()).read_bytes() for p in row["pages"].split("|")]
        start = time.perf_counter()
        pr = grading.preread(f"BENCH-{row['script_id']}", q, pages)
        wall = time.perf_counter() - start
        teacher = float(row["teacher_total"])
        results.append({
            "script_id": row["script_id"], "question_id": q.id, "max": q.max_marks, "teacher": teacher,
            "ai": pr.suggested_total, "abs_err": abs(pr.suggested_total - teacher),
            "latency_s": pr.latency_ms / 1000 if pr.engine_kind == "live" else wall,
            "engine": pr.engine_kind, "review": pr.needs_human_review,
            "cost_inr": pr.usage.cost_inr if pr.usage else 0.0,
            "tokens_in": pr.usage.input_tokens if pr.usage else 0,
            "tokens_out": (pr.usage.output_tokens + pr.usage.thinking_tokens) if pr.usage else 0,
        })
        print(f"{row['script_id']:>8}  teacher {teacher:>4g}  AI {pr.suggested_total:>4g}  "
              f"({pr.engine_kind}, {results[-1]['latency_s']:.1f}s, ₹{results[-1]['cost_inr']:.3f})")

    n = len(results)
    errs = [r["abs_err"] for r in results]
    lat = sorted(r["latency_s"] for r in results)
    top = int(max(r["max"] for r in results))
    qwk = quadratic_weighted_kappa([round(r["teacher"]) for r in results], [round(r["ai"]) for r in results], top)
    print(f"\nAnswers: {n}  (model {settings.gemini_model})")
    print(f"Exact agreement:      {sum(e == 0 for e in errs) / n:.0%}")
    print(f"Within 1 mark:        {sum(e <= 1 for e in errs) / n:.0%}")
    print(f"Mean absolute error:  {statistics.mean(errs):.2f} marks")
    print(f"QWK (whole marks):    {qwk:.2f}   (small samples give unstable kappa; report n alongside it)")
    print(f"Flagged for review:   {sum(r['review'] for r in results) / n:.0%}")
    print(f"Latency p50 / p95:    {lat[n // 2]:.1f}s / {lat[min(n - 1, int(n * 0.95))]:.1f}s")
    print(f"Mean tokens in / out: {statistics.mean(r['tokens_in'] for r in results):.0f} / "
          f"{statistics.mean(r['tokens_out'] for r in results):.0f}")
    print(f"Mean cost per answer: ₹{statistics.mean(r['cost_inr'] for r in results):.3f}")

    out = Path(csv_path).with_name(f"results_{time.strftime('%Y%m%d_%H%M%S')}.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)
    print(f"Per-answer results: {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
