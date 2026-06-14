"""Yojana Sathi — FastAPI backend. All endpoints live here.

Pipeline (POST /match):
  audio ─Sarvam STT─► transcript ─Sarvam LLM─► profile ─Gemini embed─► vector ─Atlas─► top 3
        ─Sarvam LLM─► simple-Hindi explanations ─► JSON response (TTS'd on the client)

Provider split: Sarvam does all the language work (STT, profile JSON, Hindi
explanations, TTS); Gemini is used ONLY for the vector-search embeddings, since
Sarvam has no embedding API.
"""

import json
import re
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
from fastapi.responses import JSONResponse, Response

import form_filler
import gemini_client
import mongo_client
import sarvam_client
from models import (
    BeneficiaryGroup,
    ConverseResponse,
    ConverseState,
    Person,
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
    # far better.
    try:
        query_embedding = gemini_client.embed_text(transcript, task_type="retrieval_query")
    except Exception as e:  # noqa: BLE001
        print(f"[/match] embedding error: {e}")
        raise HTTPException(status_code=502, detail="Could not process your request. Please try again.")

    # ── Step 4: Atlas Vector Search (+ deterministic age gate) ──────────
    # /match is the legacy single-shot path (the UI uses /converse). We still apply the
    # age gate so it can never surface an age-contradicting scheme either.
    try:
        matches = mongo_client.vector_search(query_embedding, limit=8)
        age = profile_dict.get("age")
        matches = [m for m in matches if age_eligibility_ok(age, m.get("eligibility_text", ""))][:3]
    except Exception as e:  # noqa: BLE001
        print(f"[/match] vector search error: {e}")
        raise HTTPException(status_code=502, detail="Could not search schemes right now.")

    # ── Step 5: STRICT eligibility audit + Hindi explanations ───────────
    # Reuse the same auditor as /converse so a card here can never contradict the profile
    # either (e.g. Widow Pension for a male, or an 18-40 scheme for an older person).
    profile = Profile(**{k: profile_dict.get(k) for k in Profile.model_fields})
    schemes = []
    try:
        verdict = sarvam_client.verify_group(
            [{"relation": "self", "facts": profile_dict, "candidates": matches}], "hi-IN"
        )
    except Exception as e:  # noqa: BLE001
        print(f"[/match] verify error: {e}")
        verdict = {}

    if isinstance(verdict, dict) and verdict.get("groups"):
        for k in (verdict["groups"][0].get("kept") or [])[:3]:
            idx = k.get("index")
            if isinstance(idx, int) and 0 <= idx < len(matches):
                m = matches[idx]
                schemes.append(
                    SchemeResult(
                        name=m.get("name", ""),
                        benefit=m.get("benefit", ""),
                        eligibility_summary=m.get("eligibility_text", ""),
                        required_docs=m.get("required_docs", []),
                        apply_url=m.get("apply_url", ""),
                        match_score=float(m.get("score", 0.0)),
                        hindi_explanation=str(k.get("explanation", "")),
                    )
                )

    # ── Step 6: return ──────────────────────────────────────────────────
    if not schemes:
        audio_text = (verdict.get("message") if isinstance(verdict, dict) else "") or (
            "हम पक्की तौर पर कोई योजना नहीं बता पाए। कृपया अपने नज़दीकी CSC केंद्र पर जाएँ।"
        )
        return MatchResponse(
            transcript=transcript, profile=profile, schemes=[],
            audio_explanation_text=audio_text, valid=True, tts_language="hi-IN",
        )

    return MatchResponse(
        transcript=transcript,
        profile=profile,
        schemes=schemes,
        audio_explanation_text=schemes[0].hindi_explanation,
        valid=True,
        tts_language="hi-IN",
    )


# Conversational helpline tuning.
# Over-fetch generously PER PERSON: the strict eligibility audit (verify_group) drops the
# bad matches, so if the pool is too small a person can end up with NOTHING after auditing.
# A wider pool keeps recall up while the audit keeps precision.
PERSON_CANDIDATES = 10
MAX_TURNS = 12          # safety cap (a bit higher: a family covers more ground than one person)


def age_eligibility_ok(age, eligibility_text: str) -> bool:
    """Deterministic age gate (no LLM): return False when a KNOWN age clearly violates an
    age range stated in the scheme's eligibility text.

    LLMs are unreliable at numeric age reasoning (they catch '18-40' but miss '60 or
    above'), so this runs as a hard backstop. It only reads ELIGIBILITY age phrases
    ('aged 18 to 40 years', 'age 60 or above', 'below 6 years') — NOT benefit ages like
    'pension after age 60', which is the exact distinction the model kept getting wrong.
    Conservative by design: if no clear age phrase is found, it passes (True).
    """
    if not isinstance(age, (int, float)) or isinstance(age, bool):
        return True
    t = (eligibility_text or "").lower()
    # explicit ranges: "aged 18 to 40 years", "18 to 40 years", "between 40 and 79 years"
    for lo, hi in re.findall(r"(\d{1,2})\s+to\s+(\d{1,2})\s+years", t):
        if not (int(lo) <= age <= int(hi)):
            return False
    for lo, hi in re.findall(r"between\s+(\d{1,2})\s+and\s+(\d{1,2})\s+year", t):
        if not (int(lo) <= age <= int(hi)):
            return False
    # lower bound: "aged 60 years or above", "60 years and above", "age 60 or above"
    for lo in re.findall(r"(\d{1,2})\s+years?\s+(?:or|and)\s+above", t):
        if age < int(lo):
            return False
    for lo in re.findall(r"aged?\s+(\d{1,2})\s+(?:or|and)\s+above", t):
        if age < int(lo):
            return False
    # upper bound for child schemes: "below 6 years", "under 18 years" (NOT "up to" — that
    # is often a duration, e.g. "shelter up to 3 years", not an age limit)
    for hi in re.findall(r"(?:below|under)\s+(\d{1,2})\s+years", t):
        if age >= int(hi):
            return False
    return True


def _person_query(relation: str, facts: dict) -> str:
    """Build a natural-language retrieval query for ONE person from their facts."""
    bits = []
    if facts.get("age"):
        bits.append(f"{facts['age']} years old")
    if facts.get("gender"):
        bits.append(str(facts["gender"]))
    if facts.get("occupation"):
        bits.append(str(facts["occupation"]))
    if facts.get("is_student") is True:
        bits.append("student")
    base = "A person who is " + ", ".join(bits) if bits else f"A person ({relation})"

    # WHAT the person needs / WHO they are — the topical retrieval signal. We deliberately
    # EXCLUDE purely-economic facts (below_poverty_line, has_ration_card): those are
    # eligibility GATES the LLM checks later, and as query terms they wrongly pull food/PDS
    # schemes that drown out the real need (e.g. a pregnant woman → maternity, not ration).
    flags = {
        "is_pregnant": "pregnant, needs maternity help",
        "is_disabled": "has a disability",
        "is_widow": "widow",
        "land_ownership": "owns farm land, is a farmer",
        "has_girl_child": "has a girl child",
    }
    extras = [phrase for key, phrase in flags.items() if facts.get(key) is True]
    for key in ("category", "education_level", "disability_detail", "needs", "state"):
        v = facts.get(key)
        if isinstance(v, str) and v.strip():
            extras.append(f"{key.replace('_', ' ')}: {v}")
    return base + ("; " + "; ".join(extras) if extras else "")


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
            # Respond in the language of THIS turn (re-detect every turn), so switching
            # from English to Telugu mid-conversation gets a Telugu reply.
            if stt.get("language_detected"):
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

    # ── Step 2: update the list of PEOPLE this call is about ────────────
    # One conversation can cover the caller AND their family members.
    st.history.append({"role": "user", "text": user_text})
    prior_people = [p.model_dump() for p in st.people]
    try:
        people = sarvam_client.extract_people(prior_people, user_text)
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] extract_people error (continuing): {e}")
        people = prior_people or [{"relation": "self", "facts": {}}]
    st.people = [Person(**p) for p in people]
    st.turn += 1

    # ── Step 3: retrieve candidate schemes PER PERSON ───────────────────
    # Deterministic AGE gate is applied here, BEFORE the LLM sees the candidates, so an
    # age-violating scheme can never be recommended OR mentioned in the spoken summary.
    try:
        people_with_candidates = []
        for p in st.people:
            emb = gemini_client.embed_text(_person_query(p.relation, p.facts), task_type="retrieval_query")
            cands = mongo_client.vector_search(emb, limit=PERSON_CANDIDATES)
            age = p.facts.get("age")
            kept = [c for c in cands if age_eligibility_ok(age, c.get("eligibility_text", ""))]
            dropped = len(cands) - len(kept)
            if dropped:
                print(f"[/converse] age gate dropped {dropped} scheme(s) for {p.relation} (age={age})")
            people_with_candidates.append({"relation": p.relation, "facts": p.facts, "candidates": kept})
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] retrieval error: {e}")
        raise HTTPException(status_code=502, detail="Could not search schemes right now.")

    # ── Step 4: the brain decides — ask one more question, or recommend ─
    history_text = "\n".join(
        f"{'Citizen' if h['role'] == 'user' else 'You'}: {h['text']}" for h in st.history
    )
    force = st.turn >= MAX_TURNS
    try:
        decision = sarvam_client.decide_group(
            people_with_candidates, st.asked, history_text, st.language, force_recommend=force
        )
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] decide_group error: {e}")
        decision = {}

    action = decision.get("action")
    message = (decision.get("message") or "").strip()
    group_specs = decision.get("groups") or []

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

    # ── Branch B: recommend — ONLY after a STRICT eligibility audit ─────
    # decide_group proposed recommending. verify_group now independently audits EVERY
    # candidate per person and keeps only the ones whose hard eligibility rules the known
    # facts satisfy (catching e.g. an 18–40 pension recommended to a 55-year-old). The
    # spoken message AND the per-scheme explanations come from the AUDITED survivors, so a
    # card can never contradict the stated facts. We deliberately DO NOT fall back to
    # showing unverified candidates — an honest "couldn't confirm" beats a false positive.
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

    def _build_groups(specs: list, kept_key: str) -> list:
        out = []
        for g in specs:
            pi = g.get("person")
            if not isinstance(pi, int) or not (0 <= pi < len(people_with_candidates)):
                continue
            cands = people_with_candidates[pi]["candidates"]
            relation = people_with_candidates[pi]["relation"]
            picks = []
            for item in (g.get(kept_key) or [])[:3]:
                idx = item.get("index")
                if isinstance(idx, int) and 0 <= idx < len(cands):
                    picks.append(_scheme(cands[idx], str(item.get("explanation", ""))))
            if picks:
                out.append(BeneficiaryGroup(label=str(g.get("label") or relation), relation=relation, schemes=picks))
        return out

    try:
        verdict = sarvam_client.verify_group(people_with_candidates, st.language)
    except Exception as e:  # noqa: BLE001
        print(f"[/converse] verify_group error: {e}")
        verdict = {}

    if isinstance(verdict, dict) and isinstance(verdict.get("groups"), list):
        groups = _build_groups(verdict["groups"], "kept")
        message = (verdict.get("message") or "").strip() or message
    else:
        # Audit transiently unavailable → fall back to the proposer's picks (best effort).
        print("[/converse] verify_group unavailable — using proposer's picks")
        groups = _build_groups(group_specs, "qualified")

    flattened = [s for g in groups for s in g.schemes]
    if not message:
        message = (
            "Here are the schemes I could confirm for your family."
            if groups
            else "I could not confirm a specific scheme from what I know. Please visit a "
            "local Common Service Centre (CSC) so someone can check the details with you."
        )
    st.history.append({"role": "bot", "text": message})
    print(f"[/converse] turn {st.turn}: RECOMMEND {len(groups)} group(s), {len(flattened)} scheme(s) [audited]")
    return ConverseResponse(
        action="recommend",
        message=message,
        transcript=user_text,
        groups=groups,
        schemes=flattened,
        state=st,
        tts_language=sarvam_client.tts_language(st.language),
        done=True,
    )


@app.post("/tts")
def tts(req: TTSRequest):
    """Text → speech via Sarvam bulbul:v2. Returns {audio: base64-wav}."""
    try:
        audio_b64 = sarvam_client.text_to_speech(req.text, language_code=req.language)
        return JSONResponse({"audio": audio_b64})
    except Exception as e:  # noqa: BLE001
        print(f"[/tts] error: {e}")
        # TTS is non-fatal — return empty so the client just shows the text.
        return JSONResponse({"audio": ""})


@app.post("/scheme-pdf")
def scheme_pdf(scheme: SchemeResult):
    """Generate a downloadable PDF summary of a matched scheme (Indic-script aware)."""
    try:
        pdf = form_filler.generate_scheme_pdf(scheme.model_dump())
    except Exception as e:  # noqa: BLE001
        print(f"[/scheme-pdf] error: {e}")
        raise HTTPException(status_code=500, detail="Could not generate the PDF.")
    safe = re.sub(r"[^A-Za-z0-9]+", "_", scheme.name).strip("_")[:60] or "scheme"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe}_yojana-saathi.pdf"'},
    )


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
