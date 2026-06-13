"""Diagnostic: list which models the current GEMINI_API_KEY can actually access.

Run once with:  python list_models.py
This makes ONE cheap metadata call (no generation, no embedding) and prints every
model the key can see, plus which ones support embedContent / generateContent.
"""

import os
import sys

# Windows PowerShell/cmd default to cp1252, which crashes on … etc. Force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from google import genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
if not key:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")

print(f"[diag] Key starts with: {key[:6]}…  (a real AI Studio key starts with 'AIzaSy')")
print("[diag] Asking Google which models this key can use…\n")

client = genai.Client(api_key=key)

try:
    for m in client.models.list():
        actions = getattr(m, "supported_actions", None) or []
        print(f"  {m.name:45s}  supports={actions}")
except Exception as e:
    print(f"[diag] Listing models FAILED: {type(e).__name__}: {e}")
    print("\n[diag] If this is a 401/403 → the key is invalid.")
    print("[diag] If it printed nothing → the key has no model access.")
