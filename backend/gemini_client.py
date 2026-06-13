"""Google Gemini — EMBEDDINGS ONLY.

Sarvam has no text-embedding API, so the vector-search embeddings live here on Gemini's
gemini-embedding-001. This is the only Gemini dependency left in the pipeline; all the
language work (STT, profile extraction, Hindi explanations, TTS) is now Sarvam.

Cost note: the embedding API is called only during seeding and on a real user query.
Each call prints a line first so credit usage is always visible in the console.
"""

import os
import re
import time

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# gemini-embedding-001 is the current embedding model (text-embedding-004 is retired).
# It defaults to 3072 dims, but we pin 768 via output_dimensionality so the MongoDB
# Atlas vector_index (numDimensions: 768) keeps working unchanged.
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMS = 768

# Free tier allows 100 embedding REQUESTS per minute. Batching many texts into one
# request keeps seeding well under that (150 schemes → 3 requests instead of 150).
EMBED_BATCH_SIZE = 50
_EMBED_MAX_RETRIES = 5
_EMBED_FALLBACK_WAIT_S = 40  # used if the 429 body doesn't tell us how long to wait


def _l2_normalize(vec: list) -> list:
    """gemini-embedding-001 only L2-normalizes its full 3072-dim output; for dims < 3072
    we must normalize ourselves so cosine/dotProduct similarity stays correct."""
    norm = sum(v * v for v in vec) ** 0.5
    return [v / norm for v in vec] if norm > 0 else vec


def _retry_on_429(fn):
    """Run fn(); on a 429 rate-limit, wait the time Gemini asks for and retry.

    This makes both seeding and live queries self-heal through the 100-requests/minute
    free-tier embedding limit instead of crashing.
    """
    for attempt in range(_EMBED_MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            is_429 = "429" in msg or "RESOURCE_EXHAUSTED" in msg
            if not is_429 or attempt == _EMBED_MAX_RETRIES:
                raise
            # Gemini tells us how long to wait ("retry in 43.0s" / 'retryDelay': '43s').
            m = re.search(r"retry(?:Delay)?['\":\s]*in?\s*['\":\s]*([\d.]+)\s*s", msg)
            wait = (float(m.group(1)) + 2) if m else _EMBED_FALLBACK_WAIT_S
            print(f"[gemini] embedding rate-limited (429) — waiting {wait:.0f}s then retrying…")
            time.sleep(wait)


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
    """Embed ONE text with gemini-embedding-001, truncated to 768 dims (live queries).

    Use task_type="retrieval_document" when embedding the scheme texts (seeding) and
    "retrieval_query" when embedding the user's situation — they are designed to be
    compared against each other, which improves retrieval quality.
    """
    print(f"[gemini] → embed_text ({EMBEDDING_MODEL}, dims={EMBEDDING_DIMS}, task={task_type}, chars={len(text)})")

    def _call():
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIMS,
            ),
        )
        return list(result.embeddings[0].values)

    return _l2_normalize(_retry_on_429(_call))


def embed_texts(texts: list, task_type: str = "retrieval_document") -> list:
    """Embed MANY texts, batching into few requests to respect the 100/min free-tier
    limit (used by seeding). Returns L2-normalized 768-dim vectors in input order.
    """
    out = []
    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        chunk = texts[start:start + EMBED_BATCH_SIZE]
        n_batch = start // EMBED_BATCH_SIZE + 1
        total_batches = (len(texts) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE
        print(
            f"[gemini] → embed_texts batch {n_batch}/{total_batches} "
            f"({len(chunk)} texts, {EMBEDDING_MODEL}, dims={EMBEDDING_DIMS}, task={task_type})"
        )

        def _call():
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=chunk,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=EMBEDDING_DIMS,
                ),
            )
            return [list(e.values) for e in result.embeddings]

        out.extend(_l2_normalize(v) for v in _retry_on_429(_call))
    return out
