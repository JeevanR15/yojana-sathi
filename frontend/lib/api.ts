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
  // valid=false when the spoken input was gibberish/irrelevant (no schemes).
  // tts_language is the BCP-47 code audio_explanation_text should be spoken in.
  valid: boolean;
  tts_language: string;
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

// ── Conversational helpline (/converse) ──────────────────────────────────────
// The whole conversation state is carried by the client between turns; we send it
// back to the backend unchanged on every turn (the backend is stateless).
export interface Person {
  relation: string; // "self" | "daughter" | "son" | ...
  facts: Record<string, unknown>;
}

export interface ConverseState {
  people: Person[]; // the caller + any family members mentioned
  history: { role: string; text: string }[];
  asked: string[];
  language: string;
  turn: number;
}

// One beneficiary's recommended schemes (the caller, or a family member).
export interface BeneficiaryGroup {
  label: string; // localized, e.g. "You" / "आप" / "Your daughter"
  relation: string;
  schemes: Scheme[];
}

export interface ConverseResponse {
  action: "ask" | "recommend";
  message: string; // what the bot says, in the citizen's language
  transcript: string; // what we heard this turn (English)
  groups: BeneficiaryGroup[]; // per-beneficiary recommendations (action === "recommend")
  schemes: Scheme[]; // flattened union (compatibility)
  state: ConverseState; // send this back on the next turn
  tts_language: string; // language code to speak `message` in
  done: boolean;
}

// One turn of the helpline conversation. Pass audio (preferred) or typed text, plus the
// state returned by the previous turn (null on the first turn).
export async function converse(
  input: { audio?: Blob; text?: string },
  state: ConverseState | null
): Promise<ConverseResponse> {
  const form = new FormData();
  if (input.audio) form.append("file", input.audio, "recording.webm");
  if (input.text) form.append("text", input.text);
  if (state) form.append("state", JSON.stringify(state));

  console.log("[api] → POST /converse", {
    turn: state?.turn ?? 0,
    via: input.audio ? "audio" : "text",
  });
  const res = await fetch(`${BACKEND_URL}/converse`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await safeError(res));
  return (await res.json()) as ConverseResponse;
}

// POST /scheme-pdf — the backend renders a downloadable PDF summary of a scheme
// (Indic-script aware, so Hindi/Telugu/etc. explanations render properly). Returns a Blob.
export async function downloadSchemePdf(scheme: Scheme): Promise<Blob> {
  const res = await fetch(`${BACKEND_URL}/scheme-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scheme),
  });
  if (!res.ok) throw new Error(await safeError(res));
  return res.blob();
}

// Text → speech via the BACKEND /tts (bulbul:v2). The backend already holds the Sarvam
// key and is proven working, so we don't depend on the Next dev-server env / proxy.
// Returns base64 WAV, or null on any failure (TTS is non-fatal — we still show the text).
export async function fetchTts(text: string, language = "hi-IN"): Promise<string | null> {
  try {
    console.log("[api] → POST /tts", { chars: text.length, language });
    const res = await fetch(`${BACKEND_URL}/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language }),
    });
    if (!res.ok) {
      console.error("[api] TTS failed", res.status);
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
