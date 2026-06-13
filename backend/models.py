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


class TTSRequest(BaseModel):
    text: str
    language: str = "hi-IN"


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
