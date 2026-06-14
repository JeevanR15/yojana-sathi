"""Pydantic request/response models for the Yojana Sathi API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class TranscribeResponse(BaseModel):
    transcript: str
    language_detected: str


class Profile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    bpl_card: Optional[bool] = None
    land_ownership: Optional[bool] = None
    is_widow: Optional[bool] = None
    is_pregnant: Optional[bool] = None
    has_girl_child: Optional[bool] = None
    is_elderly: Optional[bool] = None
    is_urban: Optional[bool] = None


class SchemeResult(BaseModel):
    name: str
    benefit: str
    eligibility_summary: str
    required_docs: List[str]
    apply_url: str
    match_score: float
    hindi_explanation: str


class MatchResponse(BaseModel):
    transcript: str
    profile: Profile
    schemes: List[SchemeResult]
    audio_explanation_text: str
    # valid=False when the input was gibberish/irrelevant (no schemes returned).
    # tts_language is the BCP-47 code the audio_explanation_text should be spoken in.
    valid: bool = True
    tts_language: str = "hi-IN"


class TTSRequest(BaseModel):
    text: str
    language: str = "hi-IN"


# ── Conversational helpline (/converse) ──────────────────────────────────────
# One conversation can cover SEVERAL beneficiaries (the caller + their family). We
# track a list of people, each with their own merged facts, and recommend per person.
# The whole state is carried by the client between turns, so the backend stays stateless.
class Person(BaseModel):
    relation: str = "self"                # "self" | "daughter" | "son" | "spouse" | ...
    facts: Dict[str, Any] = {}            # merged facts about THIS person


class ConverseState(BaseModel):
    people: List[Person] = []             # the caller + any family members mentioned
    history: List[Dict[str, str]] = []    # [{"role": "user"|"bot", "text": "..."}]
    asked: List[str] = []                 # questions already asked (avoid repeats)
    language: str = "hi-IN"               # BCP-47 language the citizen is speaking
    turn: int = 0


class BeneficiaryGroup(BaseModel):
    label: str                            # localized, e.g. "You" / "आप" / "Your daughter"
    relation: str                         # "self" | "daughter" | ...
    schemes: List[SchemeResult] = []      # schemes THIS person qualifies for


class ConverseResponse(BaseModel):
    action: str                           # "ask" (need more info) | "recommend" (done)
    message: str                          # what the bot says, in the citizen's language
    transcript: str                       # what we heard this turn (English) — for display
    groups: List[BeneficiaryGroup] = []   # per-beneficiary recommendations (action==recommend)
    schemes: List[SchemeResult] = []      # flattened union of all groups (compatibility)
    state: ConverseState                  # updated state to send back on the next turn
    tts_language: str = "hi-IN"           # bulbul:v2 code to speak `message` in
    done: bool = False


class FormFillStartRequest(BaseModel):
    scheme_name: str
    profile: Dict[str, Any] = {}


class FormFillStartResponse(BaseModel):
    scheme_name: str
    question_index: int
    question: str
    total_questions: int
    questions: List[str]
    collected_so_far: Dict[str, Any] = {}
    done: bool = False


class FormFillAnswerRequest(BaseModel):
    scheme_name: str
    question_index: int
    answer: str
    collected_so_far: Dict[str, Any] = {}


class FormFillAnswerResponse(BaseModel):
    scheme_name: str
    done: bool
    question_index: Optional[int] = None
    question: Optional[str] = None
    collected_so_far: Dict[str, Any] = {}
    pdf_base64: Optional[str] = None
    message: Optional[str] = None
