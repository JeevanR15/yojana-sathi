"""Yojana Sathi — FastAPI backend. All endpoints live here.

Pipeline (POST /match):
  audio ─Sarvam STT─► transcript ─Sarvam LLM─► profile ─Gemini embed─► vector ─Atlas─► top 3
        ─Sarvam LLM─► simple-Hindi explanations ─► JSON response (TTS'd on the client)

Provider split: Sarvam does all the language work (STT, profile JSON, Hindi
explanations, TTS); Gemini is used ONLY for the vector-search embeddings, since
Sarvam has no embedding API.
"""

import json
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
    ConverseResponse,
    ConverseState,
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


# Spoken fallback (Hindi) if Gemini didn't supply a native-language re-prompt.
DEFAULT_REPROMPT = (
    "माफ़ कीजिए, हम समझ नहीं पाए। कृपया अपनी उम्र, अपना राज्य, "
    "अपना काम और अपने पास कौन से कार्ड हैं, यह साफ़-साफ़ बताइए।"
)

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc).isoformat())


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    language_code: str = Form("hi-IN"),
) -> TranscribeResponse:
    """Audio → English text via Sarvam saaras:v3 (translate mode)."""
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
    detected_lang = "hi-IN"  # what language the user actually spoke (for native re-prompts)
    try:
        if text and text.strip():
            transcript = text.strip()
        elif file is not None:
            audio_bytes = await file.read()
            stt = sarvam_client.transcribe(
                audio_bytes, filename=file.filename or "audio.webm", language_code=language_code
            )
            transcript = stt.get("transcript", "")
            detected_lang = stt.get("language_detected") or "hi-IN"
        else:
            raise HTTPException(status_code=400, detail="Provide either an audio file or text.")
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"[/match] STT error: {e}")
        raise HTTPException(status_code=502, detail="Voice recognition failed. Please try again.")

    if not transcript.strip():
        raise HTTPException(status_code=422, detail="We could not hear anything. Please try again.")

    # ── Step 2: structured profile (+ relevance gate) ───────────────────
    try:
        profile_dict = sarvam_client.extract_profile(transcript, language_hint=detected_lang)
    except Exception as e:  # noqa: BLE001
        print(f"[/match] profile extraction error: {e}")
        raise HTTPException(status_code=502, detail="Could not process your request. Please try again.")

    # Relevance gate: vector search ALWAYS returns some scheme, even for gibberish, so we
    # skip RAG entirely when the LLM judged the input to be a non-request (a bare greeting,
    # a name with no detail, or gibberish). We trust the LLM's is_valid flag here: across
    # 150 diverse schemes the old "must contain a rural field" check wrongly rejected valid
    # requests (students, persons with disabilities, jobseekers). Skipping also saves the
    # embedding/search/explanation quota.
    iv = profile_dict.get("is_valid", True)
    is_invalid = (iv is False) or (isinstance(iv, str) and iv.strip().lower() in ("false", "no", "0"))
    if is_invalid:
        reprompt = (profile_dict.get("reprompt_message") or "").strip() or DEFAULT_REPROMPT
        print(f"[/match] input rejected (is_valid={iv!r}) — re-prompt lang={detected_lang}, skipping RAG")
        return MatchResponse(
            transcript=transcript,
            profile=Profile(),
            schemes=[],
            audio_explanation_text=reprompt,
            valid=False,
            tts_language=detected_lang,
        )

    # ── Step 3: embedding ───────────────────────────────────────────────
    # Embed the user's OWN words (the transcript), NOT the structured summary. With 150
    # diverse schemes (scholarships, caste-based, disability, jobs, housing…) the narrow
    # rural profile schema drops critical signal — e.g. a student collapses to "A other."
    # and matches nothing. The clean English transcript keeps every detail and retrieves
    # far better. profile_summary is still used below as readable context for explanations.
    profile_summary = gemini_client.profile_to_search_text(profile_dict) or transcript
    try:
        query_embedding = gemini_client.embed_text(transcript, task_type="retrieval_query")
    except Exception as e:  # noqa: BLE001
        print(f"[/match] embedding error: {e}")
        raise HTTPException(status_code=502, detail="Could not process your request. Please try again.")

    # ── Step 4: Atlas Vector Search ─────────────────────────────────────
    try:
        matches = mongo_client.vector_search(query_embedding, limit=3)
    except Exception as e:  # noqa: BLE001
        print(f"[/match] vector search error: {e}")
        raise HTTPException(status_code=502, detail="Could not search schemes right now.")

    # ── Step 5: simple-Hindi explanations for ALL schemes in ONE call ───
    # Batched (not one call per scheme) to conserve the LLM quota.
    try:
        explanations = sarvam_client.explain_schemes(profile_summary, matches)
    except Exception as e:  # noqa: BLE001
        print(f"[/match] explanation error: {e}")
        explanations = [""] * len(matches)

    schemes = []
    for i, m in enumerate(matches):
        schemes.append(
            SchemeResult(
                name=m.get("name", ""),
                benefit=m.get("benefit", ""),
                eligibility_summary=m.get("eligibility_text", ""),
                required_docs=m.get("required_docs", []),
                apply_url=m.get("apply_url", ""),
                match_score=float(m.get("score", 0.0)),
                hindi_explanation=explanations[i] if i < len(explanations) else "",
            )
        )

    audio_text = schemes[0].hindi_explanation if schemes else ""

    # ── Step 6: return everything ───────────────────────────────────────
    # Explanations are generated in Hindi, so the spoken answer is hi-IN here
    # (the native-language path is only used for the invalid re-prompt above).
    profile = Profile(**{k: profile_dict.get(k) for k in Profile.model_fields})
    return MatchResponse(
        transcript=transcript,
        profile=profile,
        schemes=schemes,
        audio_explanation_text=audio_text,
        valid=True,
        tts_language="hi-IN",
    )


# Conversational helpline tuning.
CANDIDATE_POOL = 8   # over-fetch this many so the eligibility filter has real choices
MAX_TURNS = 10       # safety cap: after this many questions, force a recommendation


@app.post("/converse", response_model=ConverseResponse)
async def converse(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    language_code: str = Form("hi-IN"),
) -> ConverseResponse:
    """Multi-turn helpline: gather facts, ask follow-ups, then recommend ONLY schemes the
    citizen genuinely qualifies for — all in the citizen's own language.

    The frontend carries `state` (JSON) between turns; the backend stays stateless.
    """
    # ── Load prior conversation state ───────────────────────────────────
    try:
        st = ConverseState(**json.loads(state)) if state else ConverseState()
    except Exception:  # noqa: BLE001
        st = ConverseState()

    # ── Step 1: this turn's user text (English) + detect language on turn 0 ─
    try:
        if text and text.strip():
            user_text = text.strip()
        elif file is not None:
            audio_bytes = await file.read()
            stt = sarvam_client.transcribe(
                audio_bytes, filename=file.filename or "audio.webm", language_code=language_code
            )
            user_text = stt.get("transcript", "")
            if st.turn == 0 and stt.get("language_detected"):
                st.language = stt["language_detected"]
        else:
            raise HTTPException(status_code=400, detail="Provide either an audio file or text.")
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] STT error: {e}")
        raise HTTPException(status_code=502, detail="Voice recognition failed. Please try again.")

    if not user_text.strip():
        # Couldn't hear — ask them to repeat, spoken in their language if we know it.
        return ConverseResponse(
            action="ask",
            message=DEFAULT_REPROMPT,
            transcript="",
            state=st,
            tts_language=sarvam_client.tts_language(st.language),
        )

    # ── Step 2: merge whatever new facts the citizen just gave us ───────
    st.history.append({"role": "user", "text": user_text})
    try:
        st.facts = sarvam_client.extract_facts(st.facts, user_text)
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] extract_facts error (continuing with prior facts): {e}")
    st.turn += 1

    # ── Step 3: retrieve candidate schemes from the WHOLE conversation ──
    query_text = " ".join(h["text"] for h in st.history if h["role"] == "user") or user_text
    try:
        emb = gemini_client.embed_text(query_text, task_type="retrieval_query")
        candidates = mongo_client.vector_search(emb, limit=CANDIDATE_POOL)
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] retrieval error: {e}")
        raise HTTPException(status_code=502, detail="Could not search schemes right now.")

    # ── Step 4: the brain decides — ask one more question, or recommend ─
    history_text = "\n".join(
        f"{'Citizen' if h['role'] == 'user' else 'You'}: {h['text']}" for h in st.history
    )
    force = st.turn >= MAX_TURNS
    try:
        decision = sarvam_client.decide_next(
            st.facts, candidates, st.asked, history_text, st.language, force_recommend=force
        )
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] decide_next error: {e}")
        decision = {}

    action = decision.get("action")
    message = (decision.get("message") or "").strip()
    qualified = decision.get("qualified") or []

    # ── Branch A: ask one more clarifying question ──────────────────────
    if action != "recommend" and not force:
        if not message:
            message = DEFAULT_REPROMPT
        st.asked.append(message)
        st.history.append({"role": "bot", "text": message})
        print(f"[/converse] turn {st.turn}: ASK — {message[:60]}")
        return ConverseResponse(
            action="ask",
            message=message,
            transcript=user_text,
            state=st,
            tts_language=sarvam_client.tts_language(st.language),
            done=False,
        )

    # ── Branch B: recommend only the schemes the citizen qualifies for ──
    def _scheme(m: dict, explanation: str) -> SchemeResult:
        return SchemeResult(
            name=m.get("name", ""),
            benefit=m.get("benefit", ""),
            eligibility_summary=m.get("eligibility_text", ""),
            required_docs=m.get("required_docs", []),
            apply_url=m.get("apply_url", ""),
            match_score=float(m.get("score", 0.0)),
            hindi_explanation=explanation,
        )

    schemes = []
    for q in qualified[:3]:
        idx = q.get("index")
        if isinstance(idx, int) and 0 <= idx < len(candidates):
            schemes.append(_scheme(candidates[idx], str(q.get("explanation", ""))))
    # Fallback: if the model named nothing usable, surface the top candidates so the
    # user is never left with an empty screen.
    if not schemes:
        schemes = [_scheme(m, "") for m in candidates[:3]]

    if not message:
        message = "Here are the schemes that fit you."
    st.history.append({"role": "bot", "text": message})
    print(f"[/converse] turn {st.turn}: RECOMMEND {len(schemes)} scheme(s)")
    return ConverseResponse(
        action="recommend",
        message=message,
        transcript=user_text,
        schemes=schemes,
        state=st,
        tts_language=sarvam_client.tts_language(st.language),
        done=True,
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
        questions = sarvam_client.generate_form_questions(req.scheme_name, req.profile)
    except Exception as e:  # noqa: BLE001
        print(f"[/form-fill/start] Sarvam question gen failed, using fallback: {e}")
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
