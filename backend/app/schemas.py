from typing import Literal, Optional

from pydantic import BaseModel, Field


class RubricCriterion(BaseModel):
    id: str
    name: str
    max: float
    description: str


class Question(BaseModel):
    id: str
    course: str
    text: str
    text_en: str
    max_marks: float
    model_answer: str
    rubric: list[RubricCriterion]


class ScriptRecord(BaseModel):
    script_id: str
    question_id: str
    pages: list[str]
    is_seed: bool = False
    gold: Optional[dict[str, float]] = None
    gold_note: str = ""
    uploaded: bool = False


# Raw output from the vision model. Deliberately lenient: guards.py clamps and checks it.
class AICriterion(BaseModel):
    criterion_id: str
    awarded: float = 0
    evidence: list[str] = []
    reasoning: str = ""
    missing: str = ""


class AIEvaluation(BaseModel):
    language: str = "other"
    transcription: str = ""
    word_count: int = 0
    equation_count: int = 0
    diagram_count: int = 0
    legibility: str = "clear"
    injection_suspected: bool = False
    injection_text: str = ""
    criteria: list[AICriterion] = []
    confidence: float = 0.5
    summary: str = ""


# What the examiner sees after the guards have run.
class EvidenceQuote(BaseModel):
    text: str
    kind: Literal["text", "diagram"]
    grounded: bool


class CriterionSuggestion(BaseModel):
    criterion_id: str
    name: str
    max: float
    description: str
    suggested: float
    evidence: list[EvidenceQuote]
    reasoning: str
    missing: str
    flags: list[str]


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    cost_inr: float


class PreRead(BaseModel):
    script_id: str
    question_id: str
    engine: str
    engine_kind: Literal["live", "cache", "mock"]
    latency_ms: int
    usage: Optional[Usage] = None
    language: str
    transcription: str
    word_count: int
    equation_count: int
    diagram_count: int
    legibility: str
    confidence: float
    criteria: list[CriterionSuggestion]
    suggested_total: float
    max_marks: float
    needs_human_review: bool
    review_reasons: list[str]
    injection_suspected: bool
    injection_text: str
    injection_matches: list[str]
    summary: str
    reading_floor_s: float


# Examiner submission.
class CriterionMark(BaseModel):
    criterion_id: str
    marks: float = Field(ge=0)
    decision: Literal["accepted", "modified", "overridden"]
    verified: bool = False


class Annotation(BaseModel):
    page: int = Field(ge=0)
    tool: Literal["tick", "cross", "pen", "note"]
    points: list[tuple[float, float]]  # normalised 0..1 page coordinates
    pressure: list[float] = []
    text: str = ""


class Telemetry(BaseModel):
    page_dwell_s: list[float]  # seconds each page was on screen, index 0 = page 1
    active_s: float = Field(ge=0)


class Submission(BaseModel):
    marks: list[CriterionMark]
    annotations: list[Annotation] = []
    telemetry: Telemetry
    acknowledged_tier: int = Field(0, ge=0, le=2)
