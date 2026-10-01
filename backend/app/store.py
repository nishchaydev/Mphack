"""In-memory demo state. A real deployment keeps this in PostgreSQL and MPOnline's tabulation register."""
import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .config import DEMO_DATA_DIR, ROOT_DIR, RUNTIME_DIR, settings
from .integrity import Ledger, Signer
from .schemas import PreRead, Question, ScriptRecord

TOPIC = "exam.evaluation.events"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_questions() -> dict[str, Question]:
    raw = json.loads((DEMO_DATA_DIR / "questions.json").read_text(encoding="utf-8"))
    return {qid: Question.model_validate(q) for qid, q in raw.items()}


def load_demo_scripts() -> list[ScriptRecord]:
    raw = json.loads((DEMO_DATA_DIR / "scripts.json").read_text(encoding="utf-8"))
    return [ScriptRecord.model_validate(s) for s in raw]


@dataclass
class ExaminerState:
    id: str = "EX-0417"
    name: str = "Demo Examiner"
    totals: list[float] = field(default_factory=list)
    dwell_s: list[float] = field(default_factory=list)
    recent_violations: deque = field(default_factory=lambda: deque(maxlen=settings.tier3_window))
    violations: int = 0
    shadow_mode: bool = False  # Tier 3: chronic speed-checking
    shadow_remaining: int = 0  # scripts still to route after a seed drift
    decisions: dict = field(default_factory=lambda: {"accepted": 0, "modified": 0, "overridden": 0})


class Store:
    def __init__(self):
        self.questions = load_questions()
        self.signer = Signer(RUNTIME_DIR / "keys" / "ed25519_private.pem")
        self.ledger = Ledger(RUNTIME_DIR / "ledger.jsonl")
        self.reset()

    def reset(self) -> None:
        self.scripts: dict[str, ScriptRecord] = {s.script_id: s for s in load_demo_scripts()}
        self.prereads: dict[str, PreRead] = {}
        self.opened_at: dict[str, float] = {}
        self.submissions: dict[str, dict] = {}
        self.events: deque = deque(maxlen=300)
        self.offset = 0
        self.examiner = ExaminerState()
        self.shadow_queue: list[dict] = []
        self.seed_results: list[dict] = []
        self.ledger.reset()

    def emit(self, event_type: str, **data) -> None:
        self.events.append({"offset": self.offset, "ts": now_iso(), "topic": TOPIC, "type": event_type, **data})
        self.offset += 1

    def page_bytes(self, script: ScriptRecord) -> list[bytes]:
        return [(ROOT_DIR / p).read_bytes() for p in script.pages]


store = Store()
