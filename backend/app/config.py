"""Runtime settings, read from environment variables or a .env file at the repo root."""
import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
DEMO_DATA_DIR = BACKEND_DIR / "demo_data"
FONTS_DIR = BACKEND_DIR / "fonts"
FRONTEND_DIR = ROOT_DIR / "frontend"
RUNTIME_DIR = BACKEND_DIR / "runtime"


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT_DIR / ".env")


def _f(name: str, default: float) -> float:
    return float(os.getenv(name, default))


@dataclass
class Settings:
    # AI engine. "auto" uses Gemini when a key is set, otherwise the canned demo responses.
    ai_mode: str = os.getenv("AI_MODE", "auto")  # auto | live | mock
    gemini_api_key: str = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    thinking_level: str = os.getenv("GEMINI_THINKING_LEVEL", "low")  # blank to send no thinking config

    # Pricing used to report cost per call. Check https://ai.google.dev/gemini-api/docs/pricing
    price_input_usd_per_m: float = _f("PRICE_INPUT_USD_PER_M", 1.50)
    price_output_usd_per_m: float = _f("PRICE_OUTPUT_USD_PER_M", 9.00)
    usd_inr: float = _f("USD_INR", 88.0)

    # Velocity sentinel: reading floor = words/wpm + per-equation + per-diagram + base (seconds).
    reading_wpm: float = _f("READING_WPM", 200)
    seconds_per_equation: float = _f("SECONDS_PER_EQUATION", 30)
    seconds_per_diagram: float = _f("SECONDS_PER_DIAGRAM", 45)
    base_seconds: float = _f("BASE_SECONDS", 10)
    nudge_fraction: float = _f("NUDGE_FRACTION", 0.40)  # Tier 1 below this share of the floor
    gate_fraction: float = _f("GATE_FRACTION", 0.25)  # Tier 2 below this share of the floor
    tier3_window: int = int(_f("TIER3_WINDOW", 5))
    tier3_violations: int = int(_f("TIER3_VIOLATIONS", 2))

    # Blind seed-script calibration.
    seed_tolerance: float = _f("SEED_TOLERANCE", 0.15)  # share of max marks
    shadow_route_count: int = int(_f("SHADOW_ROUTE_COUNT", 3))

    # Rubber-stamp detector and review thresholds.
    entropy_flag_bits: float = _f("ENTROPY_FLAG_BITS", 1.5)
    entropy_min_samples: int = int(_f("ENTROPY_MIN_SAMPLES", 10))
    entropy_window: int = int(_f("ENTROPY_WINDOW", 30))
    low_confidence: float = _f("LOW_CONFIDENCE", 0.6)

    @property
    def live_ai(self) -> bool:
        return self.ai_mode != "mock" and bool(self.gemini_api_key)


settings = Settings()
