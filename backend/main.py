"""Yojana Sathi — FastAPI backend. All endpoints live here.

Pipeline (POST /match):
  audio ─Sarvam STT─► transcript ─Gemini─► profile ─embed─► vector ─Atlas─► top 3
        ─Gemini─► simple-Hindi explanations ─► JSON response (TTS'd on the client)
"""

import sys
from datetime import datetime, timezone
from typing import Optional

# Windows consoles default to cp1252, which crashes on the →/✅ chars our modules log.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import form_filler
import gemini_client
import mongo_client
import sarvam_client
from models import (
    FormFillAnswerRequest,
    FormFillAnswerResponse,
    FormFillStartRequest,
    FormFillStartResponse,
    HealthResponse,
    MatchResponse,
    Profile,
    SchemeResult,
    TranscribeResponse,
    TTSRequest,
)

app = FastAPI(title="Yojana Sathi API", version="1.0.0")

# CORS so the Next.js frontend (3000/3001) can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc).isoformat())


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    language_code: str = Form("hi-IN"),
) -> TranscribeResponse:
    """Audio → text via Sarvam saarika:v2."""
    try:
        audio_bytes = await file.read()
        result = sarvam_client.transcribe(
            audio_bytes, filename=file.filename or "audio.webm", language_code=language_code
        )
        return TranscribeResponse(
            transcript=result["transcript"], language_detected=result["language_detected"]
        )
    except Exception as e:  # noqa: BLE001
        print(f"[/transcribe] error: {e}")
        raise HTTPException(status_code=502, detail="Voice recognition failed. Please try again.")


@app.post("/match", response_model=MatchResponse)
async def match(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language_code: str = Form("hi-IN"),
) -> MatchResponse:
    """Full pipeline. Accepts audio (preferred) OR a `text` field (mic-denied fallback)."""

    # ── Step 1: transcript ──────────────────────────────────────────────
    try:
        if text and text.strip():
            transcript = text.strip()
        elif file is not None:
            audio_bytes = await file.read()
            stt = sarvam_client.transcribe(
                audio_bytes, filename=file.filename or "audio.webm", language_code=language_code
            )
            transcript = stt.get("transcript", "")
        else:
            raise HTTPException(status_code=400, detail="Provide either an audio file or text.")
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"[/match] STT error: {e}")
        raise HTTPException(status_code=502, detail="Voice recognition failed. Please try again.")

    if not transcript.strip():
        raise HTTPException(status_code=422, detail="We could not hear anything. Please try again.")

    # ── Step 2: structured profile ──────────────────────────────────────
    try:
        profile_dict = gemini_client.extract_profile(transcript)
    except Exception as e:  # noqa: BLE001
        print(f"[/match] profile extraction error: {e}")
        raise HTTPException(status_code=502, detail="Could not process your request. Please try again.")

    # ── Step 3: profile → search text → embedding ───────────────────────
    profile_summary = gemini_client.profile_to_search_text(profile_dict) or transcript
    try:
        query_embedding = gemini_client.embed_text(profile_summary, task_type="retrieval_query")
    except Exception as e:  # noqa: BLE001
        print(f"[/match] embedding error: {e}")
        raise HTTPException(status_code=502, detail="Could not process your request. Please try again.")

    # ── Step 4: Atlas Vector Search ─────────────────────────────────────
    try:
        matches = mongo_client.vector_search(query_embedding, limit=3)
    except Exception as e:  # noqa: BLE001
        print(f"[/match] vector search error: {e}")
        raise HTTPException(status_code=502, detail="Could not search schemes right now.")

    # ── Step 5: simple-Hindi explanation per matched scheme ─────────────
    schemes = []
    for m in matches:
        try:
            hindi = gemini_client.explain_scheme(profile_summary, m)
        except Exception as e:  # noqa: BLE001
            print(f"[/match] explanation error for {m.get('name')}: {e}")
            hindi = ""
        schemes.append(
            SchemeResult(
                name=m.get("name", ""),
                benefit=m.get("benefit", ""),
                eligibility_summary=m.get("eligibility_text", ""),
                required_docs=m.get("required_docs", []),
                apply_url=m.get("apply_url", ""),
                match_score=float(m.get("score", 0.0)),
                hindi_explanation=hindi,
            )
        )

    audio_text = schemes[0].hindi_explanation if schemes else ""

    # ── Step 6: return everything ───────────────────────────────────────
    profile = Profile(**{k: profile_dict.get(k) for k in Profile.model_fields})
    return MatchResponse(
        transcript=transcript,
        profile=profile,
        schemes=schemes,
        audio_explanation_text=audio_text,
    )


@app.post("/tts")
def tts(req: TTSRequest):
    """Text → speech via Sarvam bulbul:v1. Returns {audio: base64-wav}."""
    try:
        audio_b64 = sarvam_client.text_to_speech(req.text, language_code=req.language)
        return JSONResponse({"audio": audio_b64})
    except Exception as e:  # noqa: BLE001
        print(f"[/tts] error: {e}")
        # TTS is non-fatal — return empty so the client just shows the text.
        return JSONResponse({"audio": ""})


@app.post("/form-fill/start", response_model=FormFillStartResponse)
def form_fill_start(req: FormFillStartRequest) -> FormFillStartResponse:
    """Return the first question. Uses Gemini for contextual Hindi questions,
    falling back to a deterministic question bank if Gemini is unavailable."""
    questions = []
    try:
        questions = gemini_client.generate_form_questions(req.scheme_name, req.profile)
    except Exception as e:  # noqa: BLE001
        print(f"[/form-fill/start] Gemini question gen failed, using fallback: {e}")
    if not questions:
        questions = form_filler.build_questions(req.scheme_name, req.profile)

    # Carry the question list forward so /answer stays stateless and cost-free.
    return FormFillStartResponse(
        scheme_name=req.scheme_name,
        question_index=0,
        question=questions[0],
        total_questions=len(questions),
        questions=questions,
        collected_so_far={"__questions__": questions},
        done=False,
    )


@app.post("/form-fill/answer", response_model=FormFillAnswerResponse)
def form_fill_answer(req: FormFillAnswerRequest) -> FormFillAnswerResponse:
    """Store the answer; return the next question, or generate the PDF when done."""
    collected = dict(req.collected_so_far or {})
    questions = collected.get("__questions__")
    if not isinstance(questions, list) or not questions:
        questions = form_filler.build_questions(req.scheme_name)
        collected["__questions__"] = questions

    # Save the answer keyed by the question we just asked.
    if 0 <= req.question_index < len(questions):
        collected[questions[req.question_index]] = req.answer

    next_index = req.question_index + 1
    if next_index < len(questions):
        return FormFillAnswerResponse(
            scheme_name=req.scheme_name,
            done=False,
            question_index=next_index,
            question=questions[next_index],
            collected_so_far=collected,
        )

    # All answered → generate the filled PDF draft.
    pdf_b64 = form_filler.generate_pdf(req.scheme_name, questions, collected)
    return FormFillAnswerResponse(
        scheme_name=req.scheme_name,
        done=True,
        collected_so_far=collected,
        pdf_base64=pdf_b64,
        message="Your application draft PDF is ready.",
    )
