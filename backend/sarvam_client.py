"""Sarvam AI wrapper — built for Indian languages, code-mixing, accents and dialects.

Sarvam now powers ALL the language work in the pipeline:
  - speech-to-text-translate : saaras:v3 (mode=translate → English out)
  - fact extraction (per turn): sarvam-30b  (cheap, fast)
  - conversation + eligibility reasoning + explanations: sarvam-105b  (the smart brain)
  - text-to-speech           : bulbul:v2  (in the user's own language)

The only thing Sarvam does NOT offer is a text-embedding API, so the vector-search
embeddings stay on Gemini (see gemini_client.py). Everything else is one provider.

Includes a simple retry on HTTP 429 (free-tier rate limit), per the spec.
"""

import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
STT_URL = "https://api.sarvam.ai/speech-to-text"
TTS_URL = "https://api.sarvam.ai/text-to-speech"
CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"

# sarvam-m is deprecated. We use a HYBRID: cheap 30b for per-turn fact extraction,
# bigger 105b for the conversational brain (deciding what to ask + eligibility filtering).
LLM_MODEL = "sarvam-30b"
LLM_MODEL_BIG = "sarvam-105b"

_MAX_RETRIES = 2
_RETRY_WAIT_S = 2

# BCP-47 → (English language name for the LLM prompt, TTS code bulbul:v2 supports).
# bulbul:v2 supports these Indian languages; anything else falls back to English audio
# (the on-screen text is still written in the user's language).
LANG_INFO = {
    "en-IN": ("English", "en-IN"),
    "hi-IN": ("Hindi", "hi-IN"),
    "bn-IN": ("Bengali", "bn-IN"),
    "gu-IN": ("Gujarati", "gu-IN"),
    "kn-IN": ("Kannada", "kn-IN"),
    "ml-IN": ("Malayalam", "ml-IN"),
    "mr-IN": ("Marathi", "mr-IN"),
    "od-IN": ("Odia", "od-IN"),
    "pa-IN": ("Punjabi", "pa-IN"),
    "ta-IN": ("Tamil", "ta-IN"),
    "te-IN": ("Telugu", "te-IN"),
}


def language_name(code: str) -> str:
    """English name of a BCP-47 code, for instructing the LLM which language to write in."""
    return LANG_INFO.get(code, LANG_INFO.get((code or "")[:2] + "-IN", ("Hindi", "hi-IN")))[0]


def tts_language(code: str) -> str:
    """Map a detected language to a code bulbul:v2 can speak; fall back to Hindi audio."""
    return LANG_INFO.get(code, LANG_INFO.get((code or "")[:2] + "-IN", ("Hindi", "hi-IN")))[1]

PROFILE_SYSTEM = (
    "You are a government scheme eligibility assistant for India. Extract the user's "
    "profile from their spoken statement. Return ONLY a valid JSON object with no "
    "explanation, no markdown, no code fences. If a field is not mentioned, use null."
)

EXPLAIN_SYSTEM = (
    "You explain Indian government welfare schemes to rural non-literate people in very "
    "simple Hindi. Use short sentences. No jargon. Be warm and encouraging like a "
    "helpful relative. ALWAYS write in Hindi using Devanagari script (देवनागरी) — never "
    "in Roman/English letters."
)


def _headers(json_content: bool = False) -> dict:
    h = {"api-subscription-key": SARVAM_API_KEY or ""}
    if json_content:
        h["Content-Type"] = "application/json"
    return h


def _safe_json(raw: str):
    """Parse JSON from an LLM reply, tolerating the junk models sometimes add.

    Handles ```json … ``` fences, leading prose, and trailing characters (e.g. a stray
    `]}]` after a valid array — which otherwise silently drops a whole turn's data).
    """
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # Decode the FIRST complete JSON value and ignore anything trailing/leading.
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                obj, _ = json.JSONDecoder().raw_decode(text[i:])
                return obj
            except Exception:
                continue
    print(f"[sarvam] JSON parse failed; raw={raw!r}")
    return None


def transcribe(audio_bytes: bytes, filename: str = "audio.webm", language_code: str = "hi-IN") -> dict:
    """Speech-to-text-TRANSLATE via Saaras v3 (mode=translate).

    Whatever Indian language OR English the user speaks, Saaras v3 in translate mode
    returns clean ENGLISH text. We deliberately omit `language_code` so Saaras
    auto-detects the spoken language — this is why English speech no longer comes back
    as Hindi-script phonetics. The LLM then gets plain English and can focus on matching
    schemes (RAG) instead of translating.

    Returns {transcript (English), language_detected (auto-detected input language)}.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in backend/.env")

    files = {"file": (filename, audio_bytes, "audio/webm")}
    # No language_code => Saaras auto-detects the spoken language. mode=translate => English out.
    data = {"model": "saaras:v3", "mode": "translate"}

    print(f"[sarvam] → STT-translate (saaras:v3, mode=translate, file={filename}, bytes={len(audio_bytes)})")
    resp = None
    for attempt in range(_MAX_RETRIES + 1):
        resp = requests.post(STT_URL, headers=_headers(), files=files, data=data, timeout=60)
        if resp.status_code == 429 and attempt < _MAX_RETRIES:
            print(f"[sarvam] STT rate-limited (429) — retrying in {_RETRY_WAIT_S}s…")
            time.sleep(_RETRY_WAIT_S)
            continue
        break

    # Surface Sarvam's actual error body — it explains WHY a 400/422 happened.
    if not resp.ok:
        print(f"[sarvam] STT {resp.status_code} body: {resp.text}")
    resp.raise_for_status()
    body = resp.json()
    return {
        "transcript": body.get("transcript", ""),
        "language_detected": body.get("language_code") or language_code,
    }


def _chat(system: str, user: str, temperature: float = 0.2, model: str = LLM_MODEL) -> str:
    """Call a Sarvam chat LLM (sarvam-30b or sarvam-105b) and return the assistant's text.

    Two non-obvious settings, both verified empirically against the live API:

    * enable_thinking=False — the sarvam chat models are REASONING models. Left on, they
      spend the whole token budget on hidden `reasoning_content` and return EMPTY
      `content` on long prompts (this was the "profile extraction returns {}" bug).
      Turning thinking off makes them answer directly: ~140 tokens & ~1s.
    * we do NOT set response_format=json_object — that suppresses the output and returns
      "{}". Instead we ask for JSON in the prompt and strip code fences via _safe_json.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in backend/.env")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        # Disable the model's chain-of-thought so it emits the answer directly. See above.
        "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
    }
    resp = None
    for attempt in range(_MAX_RETRIES + 1):
        resp = requests.post(CHAT_URL, headers=_headers(json_content=True), json=payload, timeout=90)
        if resp.status_code == 429 and attempt < _MAX_RETRIES:
            print(f"[sarvam] chat rate-limited (429) — retrying in {_RETRY_WAIT_S}s…")
            time.sleep(_RETRY_WAIT_S)
            continue
        break

    if not resp.ok:
        print(f"[sarvam] chat {resp.status_code} body: {resp.text}")
    resp.raise_for_status()
    return (resp.json()["choices"][0]["message"]["content"] or "").strip()


def extract_profile(transcript: str, language_hint: str = "hi-IN") -> dict:
    """Send the transcript to the LLM and get a structured profile dict back.

    Also acts as a RELEVANCE GATE: vector search always returns *some* scheme, even
    for nonsense, so we ask the LLM (same call, no extra quota) to flag whether the
    input is a genuine description of a person's situation, and — if not — to write a
    short re-prompt in the user's own language (BCP-47 `language_hint`).
    """
    prompt = f"""The user spoke in language code: {language_hint}.
Extract profile from this statement: {transcript}
Return JSON with exactly these fields:
{{
  "age": <integer or null>,
  "gender": <"male"|"female"|"other"|null>,
  "state": <Indian state name in English or null>,
  "occupation": <"farmer"|"laborer"|"vendor"|"artisan"|"unemployed"|"other"|null>,
  "bpl_card": <true|false|null>,
  "land_ownership": <true|false|null>,
  "is_widow": <true|false|null>,
  "is_pregnant": <true|false|null>,
  "has_girl_child": <true|false|null>,
  "is_elderly": <true if age >= 60, else false>,
  "is_urban": <true|false|null>,
  "is_valid": <true if the statement expresses ANY concrete personal situation or need that a government scheme could address — for example age, state/location, type of work or unemployment, income or poverty status, family situation (widow, pregnant, has children), disability, caste/category (SC/ST/OBC), being a student or needing a scholarship, needing a loan/business/job/housing/pension/health care, or a document/card held. Be GENEROUS: only a bare greeting, or only a name with no other detail (e.g. "hello, my name is Suresh"), or gibberish, MUST be false.>,
  "reprompt_message": <ALWAYS fill this in: a short, warm ONE-sentence message written IN THE USER'S LANGUAGE (code {language_hint}) that asks them to clearly say their age, their state, the work they do, and any cards they have such as a BPL or Aadhaar card>
}}"""
    print(f"[sarvam] → extract_profile ({LLM_MODEL}, lang={language_hint})")
    raw = _chat(PROFILE_SYSTEM, prompt, temperature=0.1)
    data = _safe_json(raw)
    return data if isinstance(data, dict) else {}


# ─────────────────────────────────────────────────────────────────────────────
# Conversational helpline agent (the redesign): gather facts over multiple turns,
# then recommend ONLY schemes the citizen actually qualifies for.
# ─────────────────────────────────────────────────────────────────────────────

FACTS_SYSTEM = (
    "You maintain a citizen's profile for Indian government welfare eligibility. You MERGE "
    "new information into the existing facts. NEVER invent facts the person did not state. "
    "Return ONLY a JSON object, no markdown, no code fences."
)

AGENT_SYSTEM = (
    "You are a warm, patient telephone helpline agent for Indian government welfare schemes, "
    "helping rural, often non-literate citizens. You speak simply and kindly, like a helpful "
    "relative. CRITICAL RULES: (1) NEVER assume or invent facts the citizen has not stated — "
    "do not guess their caste, widow/marital status, income, religion or anything else. "
    "(2) Every scheme has hard eligibility rules (age ranges, widow/marital status, caste, "
    "income/BPL, occupation). Recommend a scheme ONLY when the KNOWN facts clearly satisfy "
    "its rules. (3) If a decisive eligibility fact is unknown, ASK about it instead of "
    "guessing. Return ONLY JSON, no markdown."
)


def extract_facts(prior_facts: dict, user_text: str) -> dict:
    """Merge anything new the citizen just said into the running facts dict (sarvam-30b)."""
    prompt = f"""Existing known facts (JSON): {json.dumps(prior_facts or {}, ensure_ascii=False)}

The citizen just said (translated to English): "{user_text}"

Update the facts by MERGING in ONLY what the citizen actually stated. Keep all existing
facts unless they corrected one. Only include a field when it is genuinely known.
Use these keys when relevant (you may add others):
  name, age, gender, state, area ("urban"|"rural"),
  occupation, employment_status, annual_income, below_poverty_line (true/false),
  has_ration_card (true/false), category ("general"|"SC"|"ST"|"OBC"|"minority"),
  marital_status ("single"|"married"|"widowed"|"divorced"),
  is_disabled (true/false), disability_detail,
  is_student (true/false), education_level,
  is_pregnant (true/false), has_children (true/false), has_girl_child (true/false),
  land_ownership (true/false), has_bank_account (true/false),
  needs ("what help they are asking for, in a few words").

Return ONLY the merged JSON object."""
    print(f"[sarvam] → extract_facts ({LLM_MODEL})")
    raw = _chat(FACTS_SYSTEM, prompt, temperature=0.1, model=LLM_MODEL)
    data = _safe_json(raw)
    merged = dict(prior_facts or {})
    if isinstance(data, dict):
        # Keep prior facts; overlay only the non-null values the model returned.
        merged.update({k: v for k, v in data.items() if v is not None and v != ""})
    return merged


def decide_next(facts: dict, candidates: list, asked_topics: list,
                history_text: str, language_code: str, force_recommend: bool = False) -> dict:
    """The brain (sarvam-105b): given facts + candidate schemes, either ask ONE more
    question or recommend only the schemes the citizen genuinely qualifies for.

    Returns {"action": "ask"|"recommend", "message": str, "qualified": [{"index", "explanation"}]}.
    Everything addressed to the citizen is written in their own language. When
    force_recommend is True (we have asked enough), the model must recommend now.
    """
    lang = language_name(language_code)
    blocks = []
    for i, s in enumerate(candidates):
        docs = ", ".join(s.get("required_docs", []))
        blocks.append(
            f"{i}. {s.get('name')} — benefit: {s.get('benefit')}\n"
            f"   eligibility: {s.get('eligibility_text')}\n"
            f"   documents: {docs}"
        )
    joined = "\n".join(blocks)

    prompt = f"""Conversation so far (for context):
{history_text or '(this is the very first thing they said)'}

Known facts about the citizen (JSON):
{json.dumps(facts or {}, ensure_ascii=False)}

Topics you have ALREADY asked about (do not repeat any of these): {asked_topics or 'none'}

Candidate schemes retrieved by similarity (they may or may NOT actually fit — check each):
{joined}

Choose ONE action:
- "ask": if you still need a decisive fact to know which of these schemes the citizen truly
  qualifies for (e.g. age, caste/category, marital/widow status, income or BPL status,
  occupation, disability, rural/urban). Ask ONE short, simple question about the single most
  useful MISSING fact. Never re-ask something already known or already asked.
- "recommend": ONLY when the known facts clearly satisfy the eligibility rules of at least
  one scheme. Pick up to 3 schemes the citizen GENUINELY qualifies for (best first). Exclude
  any scheme whose required eligibility fact is unknown or not met.

Write everything addressed to the citizen (the "message" and every "explanation") in {lang},
in very simple, warm words.
{'IMPORTANT: You have gathered enough — you MUST choose "recommend" now. Pick the schemes that best fit the known facts (do not ask another question).' if force_recommend else ''}

Return ONLY this JSON:
{{
  "action": "ask" | "recommend",
  "message": "<in {lang}: your ONE question, OR a one-sentence intro before the matches>",
  "qualified": [ {{"index": <candidate number from the list above>, "explanation": "<in {lang}: 2-3 simple sentences — what they get, why they qualify, which documents to bring>"}} ]
}}
If action is "ask", "qualified" MUST be an empty array."""
    print(f"[sarvam] → decide_next ({LLM_MODEL_BIG}, candidates={len(candidates)}, lang={language_code})")
    raw = _chat(AGENT_SYSTEM, prompt, temperature=0.3, model=LLM_MODEL_BIG)
    data = _safe_json(raw)
    return data if isinstance(data, dict) else {}


# ─────────────────────────────────────────────────────────────────────────────
# Multi-beneficiary conversation: one chat can cover the caller AND their family.
# extract_people maintains a list of people; decide_group recommends per person.
# ─────────────────────────────────────────────────────────────────────────────

PEOPLE_SYSTEM = (
    "You track the people a caller wants Indian government welfare help for — the caller "
    "(relation 'self') and any family members they mention. You MERGE new information into "
    "the right person and ADD a new person when a new family member is introduced. NEVER "
    "invent facts the caller did not state. Return ONLY a JSON array, no markdown."
)

GROUP_AGENT_SYSTEM = (
    "You are a warm, patient telephone helpline agent for Indian government welfare schemes, "
    "helping rural, often non-literate families. One call can be about several people (the "
    "caller and their relatives). You speak simply and kindly. CRITICAL RULES: (1) NEVER "
    "assume or invent facts about ANY person that were not stated — do not guess caste, "
    "widow/marital status, income, etc. (2) Recommend a scheme for a person ONLY when THAT "
    "person's known facts clearly satisfy its eligibility rules. (3) If a decisive fact is "
    "missing for someone, ASK about it instead of guessing. Return ONLY JSON, no markdown."
)


def extract_people(prior_people: list, user_text: str) -> list:
    """Update the list of people the conversation is about (sarvam-30b).

    The model extracts facts from THIS utterance only (grouped by person); we MERGE them
    into the prior people server-side by relation. This makes fact-preservation
    deterministic — the model can't accidentally drop or move a previously-known fact, it
    only has to assign the new sentence's facts to the right person.

    Returns a list of {"relation": str, "facts": dict}.
    """
    known = [{"relation": p.get("relation"), "facts": p.get("facts", {})} for p in (prior_people or [])]
    prompt = f"""People already in this conversation (with the facts known so far):
{json.dumps(known, ensure_ascii=False) if known else '(none yet — this is the first thing they said)'}

The caller just said (translated to English): "{user_text}"

From THIS statement ONLY, extract the NEW or UPDATED facts, grouped by WHICH person each
fact is about. Rules:
- The caller themself is relation "self". Relatives use "daughter", "son", "spouse",
  "husband", "wife", "mother", "father", "brother", "sister".
- Use the known people above to resolve references like "she", "he", "my daughter".
- Assign each fact to the CORRECT person. Do not mix up the son's and daughter's details.
- Include ONLY facts actually stated in this statement (do not repeat old facts, do not
  invent). Use keys like: age, gender, state, area, occupation, employment_status,
  annual_income, below_poverty_line, has_ration_card, category, marital_status,
  is_disabled, disability_detail, is_student, education_level, is_pregnant, has_children,
  has_girl_child, land_ownership, has_bank_account, needs.
- ALWAYS capture "category" when a caste/community is mentioned, normalizing to one of:
  "SC" (scheduled caste / dalit), "ST" (scheduled tribe / adivasi), "OBC" (other backward
  class / backward), "minority", or "general" (forward / upper caste).
- List ONLY the people mentioned in THIS statement.

Return ONLY a JSON array: [{{"relation": "...", "facts": {{...}}}}, ...]"""
    print(f"[sarvam] → extract_people ({LLM_MODEL})")
    # Fact extraction needs no creativity — temperature 0 for the most consistent capture.
    raw = _chat(PEOPLE_SYSTEM, prompt, temperature=0.0, model=LLM_MODEL)
    data = _safe_json(raw)

    # Server-side merge: start from prior facts (never lost), overlay this turn's new facts.
    merged: dict = {p.get("relation") or "self": dict(p.get("facts") or {}) for p in (prior_people or [])}
    order = [p.get("relation") or "self" for p in (prior_people or [])]
    if isinstance(data, list):
        for p in data:
            if not isinstance(p, dict):
                continue
            rel = str(p.get("relation") or "self")
            facts = p.get("facts") if isinstance(p.get("facts"), dict) else {}
            clean = {k: v for k, v in facts.items() if v is not None and v != ""}
            if rel not in merged:
                merged[rel] = {}
                order.append(rel)
            merged[rel].update(clean)
    if not merged:
        merged, order = {"self": {}}, ["self"]
    return [{"relation": r, "facts": merged[r]} for r in order]


def decide_group(people_with_candidates: list, asked_topics: list,
                 history_text: str, language_code: str, force_recommend: bool = False) -> dict:
    """The brain (sarvam-105b) over MULTIPLE people: ask one more question, or recommend
    schemes per person.

    `people_with_candidates`: list of {"relation", "facts", "candidates": [scheme dicts]}.
    Returns {"action", "message", "groups": [{"person": idx, "label", "qualified": [{"index", "explanation"}]}]}.
    """
    lang = language_name(language_code)
    blocks = []
    for pi, p in enumerate(people_with_candidates):
        lines = []
        for ci, s in enumerate(p.get("candidates", [])):
            docs = ", ".join(s.get("required_docs", []))
            lines.append(
                f"    {ci}. {s.get('name')} — benefit: {s.get('benefit')} — "
                f"eligibility: {s.get('eligibility_text')} — documents: {docs}"
            )
        blocks.append(
            f"PERSON {pi} — relation: {p.get('relation')} — "
            f"facts: {json.dumps(p.get('facts', {}), ensure_ascii=False)}\n"
            f"  candidate schemes:\n" + "\n".join(lines)
        )
    joined = "\n\n".join(blocks)

    prompt = f"""Conversation so far (for context):
{history_text or '(this is the very first thing they said)'}

The people this call is about, each with their own candidate schemes (candidates may or
may NOT actually fit — check each person's eligibility):

{joined}

Topics you have ALREADY asked about (do not repeat any): {asked_topics or 'none'}

Choose ONE action:
- "ask": if ANY person still needs a decisive fact to determine eligibility (e.g. age,
  caste/category, marital/widow status, income or BPL, occupation, disability, rural/urban).
  Ask ONE short, simple question about the single most useful MISSING fact. If it is about a
  specific family member, name them (e.g. "your daughter"). Never re-ask a known/asked thing.
- "recommend": ONLY when you can confidently match schemes for the people. For EACH person,
  list the schemes (by that person's candidate index) whose eligibility their facts clearly
  satisfy. Exclude any scheme whose required fact is unknown or not met. A person may have
  zero qualifying schemes — that is fine.

Write everything addressed to the caller (the "message" and every "explanation") in {lang},
in very simple, warm words. The "message" on recommend should be a short spoken summary that
covers each person, e.g. "For you: ...; for your daughter: ...".
{'IMPORTANT: You have gathered enough — you MUST choose "recommend" now (do not ask another question).' if force_recommend else ''}

Return ONLY this JSON:
{{
  "action": "ask" | "recommend",
  "message": "<in {lang}>",
  "groups": [
    {{"person": <PERSON number>, "label": "<in {lang}: who this is, e.g. You / Your daughter>",
      "qualified": [ {{"index": <that person's candidate number>, "explanation": "<in {lang}: 2-3 simple sentences — what they get, why they qualify, which documents to bring>"}} ] }}
  ]
}}
If action is "ask", "groups" MUST be an empty array."""
    print(f"[sarvam] → decide_group ({LLM_MODEL_BIG}, people={len(people_with_candidates)}, lang={language_code})")
    raw = _chat(GROUP_AGENT_SYSTEM, prompt, temperature=0.3, model=LLM_MODEL_BIG)
    data = _safe_json(raw)
    return data if isinstance(data, dict) else {}


VERIFY_SYSTEM = (
    "You are a STRICT eligibility auditor for Indian government welfare schemes. Your ONLY "
    "job is to protect citizens from being told they qualify when they do not. For each "
    "scheme you check EVERY eligibility requirement against the person's KNOWN facts and you "
    "REJECT the scheme if the person clearly fails ANY requirement, OR if a decisive "
    "requirement cannot be confirmed from the known facts. Be skeptical, not generous. Never "
    "assume a fact that was not stated. Return ONLY JSON."
)


def verify_group(people_with_candidates: list, language_code: str) -> dict:
    """STRICT audit (sarvam-105b): keep ONLY the candidate schemes each person genuinely
    qualifies for, and write the grounded explanation + spoken summary FROM the survivors
    (so the card can never contradict the stated facts).

    `people_with_candidates`: list of {"relation", "facts", "candidates": [scheme dicts]}.
    Returns {"message", "groups": [{"person": idx, "label", "kept": [{"index", "explanation"}]}]}.
    """
    lang = language_name(language_code)
    blocks = []
    for pi, p in enumerate(people_with_candidates):
        lines = []
        for ci, s in enumerate(p.get("candidates", [])):
            lines.append(f"    {ci}. {s.get('name')} — eligibility: {s.get('eligibility_text')}")
        blocks.append(
            f"PERSON {pi} — relation: {p.get('relation')} — "
            f"facts: {json.dumps(p.get('facts', {}), ensure_ascii=False)}\n"
            f"  candidate schemes:\n" + "\n".join(lines)
        )
    joined = "\n\n".join(blocks)

    prompt = f"""Audit the candidate schemes for each person. Use ONLY the listed facts — do
NOT assume anything not stated.

{joined}

For EACH candidate, KEEP it only if the person's known facts clearly satisfy EVERY
requirement in its eligibility text. REJECT it if the person fails any requirement (wrong
AGE range, wrong gender, wrong caste/category, not a widow / not the required marital status,
owns more land than allowed, income too high, wrong occupation, etc.) OR if a decisive
requirement is NOT known from the facts (do not guess).

AGE — be very careful and DO THE ARITHMETIC with the person's stated age:
- "aged 18 to 40 years at time of enrolment" means the person must be 18-40 NOW. A 55-year-old
  FAILS this even though the pension is paid "after age 60". Enrolment age ≠ benefit age.
- "age 60 years or above" means the person must currently be at least 60.
- "below 6 years", "aged 18 to 50", etc. — check the person's actual age against the range.

Keep at most the 3 best-fitting schemes per person.

Return ONLY this JSON:
{{
  "message": "<in {lang}: short, warm spoken summary. For each person, say which schemes they can get. If a person has NO scheme that fits, gently say you could not confirm one for them and they can ask at a local Common Service Centre (CSC). Keep it natural and brief.>",
  "groups": [
    {{"person": <number>, "label": "<in {lang}: who this is, e.g. You / Your daughter>",
      "kept": [ {{"index": <that person's candidate number>, "explanation": "<in {lang}: 2-3 simple sentences — what they get, the SPECIFIC reason their facts qualify them, and which documents to bring>"}} ] }}
  ]
}}
Include a group entry for EVERY person; use an empty "kept" array for anyone with no fitting scheme."""
    print(f"[sarvam] → verify_group ({LLM_MODEL_BIG}, people={len(people_with_candidates)}, lang={language_code})")
    raw = _chat(VERIFY_SYSTEM, prompt, temperature=0.1, model=LLM_MODEL_BIG)
    data = _safe_json(raw)
    return data if isinstance(data, dict) else {}


def explain_schemes(profile_summary: str, schemes: list) -> list:
    """Explain ALL matched schemes in ONE LLM call (quota-friendly).

    Instead of one API call per scheme (3 calls), we ask for all explanations at once
    and get back a JSON array — keeping each /match query to 2 LLM calls total. Returns
    simple-Hindi strings in the SAME ORDER as `schemes`.
    """
    if not schemes:
        return []

    blocks = []
    for i, s in enumerate(schemes):
        docs = ", ".join(s.get("required_docs", []))
        blocks.append(
            f"{i}. Scheme: {s.get('name')} — {s.get('benefit')}\n"
            f"   Why they qualify: {s.get('eligibility_text')}\n"
            f"   Required documents: {docs}"
        )
    joined = "\n".join(blocks)

    prompt = f"""The user's profile: {profile_summary}

Here are {len(schemes)} matched government schemes (numbered):
{joined}

For EACH scheme, write a 3-4 sentence explanation in simple Hindi that:
1. Tells them which scheme they qualify for and what they will get
2. Tells them why they qualify in one simple sentence
3. Lists the documents they need to bring
Keep each under 80 words. Use simple words a village person would understand.

CRITICAL: Write ONLY in Hindi using Devanagari script. Do NOT use Roman/English letters.
For example write "आपको हर महीने ₹300 मिलेंगे।", NOT "Aapko har mahine 300 rupaye milenge."

Return ONLY a JSON array of {len(schemes)} strings, in the SAME ORDER as the schemes
above (index 0 first). No markdown, no keys — just the array of strings."""
    print(f"[sarvam] → explain_schemes (batch of {len(schemes)}, {LLM_MODEL})")
    raw = _chat(EXPLAIN_SYSTEM, prompt, temperature=0.4)
    data = _safe_json(raw)
    if isinstance(data, list):
        out = [str(x) for x in data]
    elif isinstance(data, dict):
        # Tolerate a wrapper like {"explanations": [...]}.
        arr = next((v for v in data.values() if isinstance(v, list)), [])
        out = [str(x) for x in arr]
    else:
        out = []

    # Always return exactly one entry per scheme (pad/truncate defensively).
    return (out + [""] * len(schemes))[: len(schemes)]


def generate_form_questions(scheme_name: str, profile: dict) -> list:
    """Ask the LLM for a short list of simple Hindi questions to fill this scheme's form."""
    prompt = f"""We are helping a rural person apply for the Indian government scheme "{scheme_name}".
Their known profile (JSON): {json.dumps(profile, ensure_ascii=False)}

Generate a SHORT list (5 to 7) of simple questions IN HINDI to collect the remaining
information needed to fill the application form — for example full name, father's or
husband's name, full address, bank account number, Aadhaar number, mobile number.
Skip anything already known in the profile.
Return ONLY a JSON array of question strings. No markdown, no explanation."""
    print(f"[sarvam] → generate_form_questions '{scheme_name}' ({LLM_MODEL})")
    raw = _chat(EXPLAIN_SYSTEM, prompt, temperature=0.3)
    data = _safe_json(raw)
    if isinstance(data, list) and data:
        return [str(q) for q in data]
    return []


def text_to_speech(text: str, language_code: str = "hi-IN", speaker: str = "anushka") -> str:
    """Text-to-speech via bulbul:v2. Returns a base64-encoded WAV string (the first audio).

    bulbul:v1 and its old speakers (meera, pavithra, …) are deprecated. v2 speakers
    include: anushka, manisha, vidya, arya (female), karun, hitesh, abhilash (male), …
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in backend/.env")

    payload = {
        "inputs": [text[:500]],  # bulbul caps a single input around 500 chars
        "target_language_code": language_code,
        "speaker": speaker,
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": "bulbul:v2",
    }

    print(f"[sarvam] → TTS (bulbul:v2, lang={language_code}, speaker={speaker}, chars={len(text)})")
    resp = None
    for attempt in range(_MAX_RETRIES + 1):
        resp = requests.post(TTS_URL, headers=_headers(json_content=True), json=payload, timeout=60)
        if resp.status_code == 429 and attempt < _MAX_RETRIES:
            print(f"[sarvam] TTS rate-limited (429) — retrying in {_RETRY_WAIT_S}s…")
            time.sleep(_RETRY_WAIT_S)
            continue
        break

    if not resp.ok:
        print(f"[sarvam] TTS {resp.status_code} body: {resp.text}")
    resp.raise_for_status()
    audios = resp.json().get("audios", [])
    return audios[0] if audios else ""
