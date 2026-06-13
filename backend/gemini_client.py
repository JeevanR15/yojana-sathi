"""Google Gemini: profile extraction, embeddings, Hindi explanations, form questions.

Cost note: the embedding API is called only during seeding and on a real user query.
Each external call prints a line first so credit usage is always visible in the console.
"""

import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

GENERATION_MODEL = "gemini-2.5-flash"
# gemini-embedding-001 is the current embedding model (text-embedding-004 is retired).
# It defaults to 3072 dims, but we pin 768 via output_dimensionality so the MongoDB
# Atlas vector_index (numDimensions: 768) keeps working unchanged.
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMS = 768

PROFILE_SYSTEM = (
    "You are a government scheme eligibility assistant for India. Extract the user's "
    "profile from their spoken statement. Return ONLY a valid JSON object with no "
    "explanation, no markdown, no code fences. If a field is not mentioned, use null."
)

EXPLAIN_SYSTEM = (
    "You explain Indian government welfare schemes to rural non-literate people in very "
    "simple Hindi. Use short sentences. No jargon. Be warm and encouraging like a "
    "helpful relative."
)


def _safe_json(raw: str):
    """Parse JSON, defensively stripping markdown code fences Gemini sometimes adds."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except Exception as e:
        print(f"[gemini] JSON parse failed: {e}; raw={raw!r}")
        return None


def extract_profile(transcript: str) -> dict:
    """Send the transcript to Gemini and get a structured profile dict back."""
    prompt = f"""Extract profile from this statement: {transcript}
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
  "is_urban": <true|false|null>
}}"""
    print(f"[gemini] → extract_profile ({GENERATION_MODEL})")
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=PROFILE_SYSTEM,
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    data = _safe_json(response.text)
    return data if isinstance(data, dict) else {}


def profile_to_search_text(profile: dict) -> str:
    """Turn the structured profile into a natural-language sentence before embedding.

    Example: "A 60-year-old female farmer from Bihar. Belongs to a Below Poverty Line
    (BPL) family. Owns agricultural land. Is a widow who lost her husband."
    """
    if not profile:
        return ""

    desc = []
    if profile.get("age"):
        desc.append(f"{profile['age']}-year-old")
    if profile.get("gender"):
        desc.append(str(profile["gender"]))
    if profile.get("occupation"):
        desc.append(str(profile["occupation"]))

    who = ("A " + " ".join(desc)) if desc else "A person"
    if profile.get("state"):
        who += f" from {profile['state']}"
    parts = [who + "."]

    if profile.get("bpl_card") is True:
        parts.append("Belongs to a Below Poverty Line (BPL) family.")
    if profile.get("land_ownership") is True:
        parts.append("Owns agricultural land.")
    if profile.get("is_widow") is True:
        parts.append("Is a widow who lost her husband.")
    if profile.get("is_pregnant") is True:
        parts.append("Is pregnant or a new mother.")
    if profile.get("has_girl_child") is True:
        parts.append("Has a young girl child.")
    if profile.get("is_elderly") is True:
        parts.append("Is an elderly senior citizen.")
    if profile.get("is_urban") is True:
        parts.append("Lives in an urban area.")
    elif profile.get("is_urban") is False:
        parts.append("Lives in a rural village.")

    return " ".join(parts)


def embed_text(text: str, task_type: str = "retrieval_query") -> list:
    """Embed text with gemini-embedding-001, truncated to 768 dimensions.

    Use task_type="retrieval_document" when embedding the scheme texts (seeding) and
    "retrieval_query" when embedding the user's situation — they are designed to be
    compared against each other, which improves retrieval quality.

    gemini-embedding-001 only L2-normalizes its full 3072-dim output. When we request a
    smaller dimension we must normalize ourselves so cosine/dotProduct stay correct.
    """
    print(f"[gemini] → embed_text ({EMBEDDING_MODEL}, dims={EMBEDDING_DIMS}, task={task_type}, chars={len(text)})")
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMS,
        ),
    )
    values = list(result.embeddings[0].values)

    # L2-normalize the truncated vector (required for dims < 3072).
    norm = sum(v * v for v in values) ** 0.5
    if norm > 0:
        values = [v / norm for v in values]
    return values


def explain_scheme(profile_summary: str, scheme: dict) -> str:
    """Generate a simple-Hindi explanation for one matched scheme."""
    docs = ", ".join(scheme.get("required_docs", []))
    prompt = f"""The user's profile: {profile_summary}
Matched scheme: {scheme.get('name')} — {scheme.get('benefit')}
Why they qualify: {scheme.get('eligibility_text')}
Required documents: {docs}

Write a 3-4 sentence explanation in simple Hindi that:
1. Tells them which scheme they qualify for and what they will get
2. Tells them why they qualify in one simple sentence
3. Lists the documents they need to bring
Keep it under 80 words. Use simple words a village person would understand."""
    print(f"[gemini] → explain_scheme '{scheme.get('name')}' ({GENERATION_MODEL})")
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=EXPLAIN_SYSTEM,
            temperature=0.4,
        ),
    )
    return (response.text or "").strip()


def generate_form_questions(scheme_name: str, profile: dict) -> list:
    """Ask Gemini for a short list of simple Hindi questions to fill this scheme's form."""
    prompt = f"""We are helping a rural person apply for the Indian government scheme "{scheme_name}".
Their known profile (JSON): {json.dumps(profile, ensure_ascii=False)}

Generate a SHORT list (5 to 7) of simple questions IN HINDI to collect the remaining
information needed to fill the application form — for example full name, father's or
husband's name, full address, bank account number, Aadhaar number, mobile number.
Skip anything already known in the profile.
Return ONLY a JSON array of question strings. No markdown, no explanation."""
    print(f"[gemini] → generate_form_questions '{scheme_name}' ({GENERATION_MODEL})")
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=EXPLAIN_SYSTEM,
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )
    data = _safe_json(response.text)
    if isinstance(data, list) and data:
        return [str(q) for q in data]
    return []
