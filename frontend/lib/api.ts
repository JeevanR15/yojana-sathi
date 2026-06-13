// All browser → backend calls live here. The backend URL is read from the
// NEXT_PUBLIC_BACKEND_URL env var — never hardcoded.

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") || "http://localhost:8000";

export interface Profile {
  age: number | null;
  gender: "male" | "female" | "other" | null;
  state: string | null;
  occupation:
    | "farmer"
    | "laborer"
    | "vendor"
    | "artisan"
    | "unemployed"
    | "other"
    | null;
  bpl_card: boolean | null;
  land_ownership: boolean | null;
  is_widow: boolean | null;
  is_pregnant: boolean | null;
  has_girl_child: boolean | null;
  is_elderly: boolean | null;
  is_urban: boolean | null;
}

export interface Scheme {
  name: string;
  benefit: string;
  eligibility_summary: string;
  required_docs: string[];
  apply_url: string;
  match_score: number;
  hindi_explanation: string;
}

export interface MatchResponse {
  transcript: string;
  profile: Profile;
  schemes: Scheme[];
  audio_explanation_text: string;
}

// POST /match with recorded audio — runs the full STT → profile → vector-search pipeline.
export async function matchSchemesFromAudio(
  audio: Blob,
  languageCode = "hi-IN"
): Promise<MatchResponse> {
  const form = new FormData();
  form.append("file", audio, "recording.webm");
  form.append("language_code", languageCode);

  console.log("[api] → POST /match (audio)", { bytes: audio.size, languageCode });
  const res = await fetch(`${BACKEND_URL}/match`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await safeError(res));
  return (await res.json()) as MatchResponse;
}

// POST /match with typed text — used by the mic-denied fallback path.
export async function matchSchemesFromText(text: string): Promise<MatchResponse> {
  const form = new FormData();
  form.append("text", text);

  console.log("[api] → POST /match (text)", { text });
  const res = await fetch(`${BACKEND_URL}/match`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await safeError(res));
  return (await res.json()) as MatchResponse;
}

// POST /api/sarvam — the Next.js proxy that hides the Sarvam key and returns base64 WAV.
// Returns null on any failure (TTS is non-fatal: we just show the text instead).
export async function fetchTts(text: string, language = "hi-IN"): Promise<string | null> {
  try {
    console.log("[api] → POST /api/sarvam (TTS)", { chars: text.length, language });
    const res = await fetch("/api/sarvam", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language }),
    });
    if (!res.ok) {
      console.error("[api] TTS proxy failed", res.status);
      return null;
    }
    const data = await res.json();
    return (data.audio as string) || null;
  } catch (err) {
    console.error("[api] TTS error (ignored)", err);
    return null;
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BACKEND_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

async function safeError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data.detail || data.error || `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}
