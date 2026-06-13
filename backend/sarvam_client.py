"""Sarvam AI wrapper — built for Indian languages, code-mixing, accents and dialects.

  - speech-to-text-translate : saaras:v3 (mode=translate → English out)
  - text-to-speech           : bulbul:v1

Includes a simple retry on HTTP 429 (free-tier rate limit), per the spec.
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
STT_URL = "https://api.sarvam.ai/speech-to-text"
TTS_URL = "https://api.sarvam.ai/text-to-speech"

_MAX_RETRIES = 2
_RETRY_WAIT_S = 2


def _headers(json_content: bool = False) -> dict:
    h = {"api-subscription-key": SARVAM_API_KEY or ""}
    if json_content:
        h["Content-Type"] = "application/json"
    return h


def transcribe(audio_bytes: bytes, filename: str = "audio.webm", language_code: str = "hi-IN") -> dict:
    """Speech-to-text-TRANSLATE via Saaras v3 (mode=translate).

    Whatever Indian language OR English the user speaks, Saaras v3 in translate mode
    returns clean ENGLISH text. We deliberately omit `language_code` so Saaras
    auto-detects the spoken language — this is why English speech no longer comes back
    as Hindi-script phonetics. Gemini then gets plain English and can focus on matching
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


def text_to_speech(text: str, language_code: str = "hi-IN", speaker: str = "meera") -> str:
    """Text-to-speech. Returns a base64-encoded WAV string (the first audio)."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in backend/.env")

    payload = {
        "inputs": [text[:500]],  # bulbul:v1 caps a single input around 500 chars
        "target_language_code": language_code,
        "speaker": speaker,
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": "bulbul:v1",
    }

    print(f"[sarvam] → TTS (bulbul:v1, lang={language_code}, chars={len(text)})")
    resp = None
    for attempt in range(_MAX_RETRIES + 1):
        resp = requests.post(TTS_URL, headers=_headers(json_content=True), json=payload, timeout=60)
        if resp.status_code == 429 and attempt < _MAX_RETRIES:
            print(f"[sarvam] TTS rate-limited (429) — retrying in {_RETRY_WAIT_S}s…")
            time.sleep(_RETRY_WAIT_S)
            continue
        break

    resp.raise_for_status()
    audios = resp.json().get("audios", [])
    return audios[0] if audios else ""
