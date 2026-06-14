import { NextRequest, NextResponse } from "next/server";

// Server-side proxy for Sarvam TTS. Keeps SARVAM_API_KEY out of the browser.
const SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech";

export async function POST(req: NextRequest) {
  const apiKey = process.env.SARVAM_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "SARVAM_API_KEY not configured on the server." },
      { status: 500 }
    );
  }

  let text = "";
  let language = "hi-IN";
  try {
    const body = await req.json();
    text = (body.text ?? "").toString();
    language = (body.language ?? "hi-IN").toString();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!text.trim()) {
    return NextResponse.json({ error: "Missing text" }, { status: 400 });
  }

  // bulbul caps a single input around 500 chars — stay safely under it.
  const safeText = text.slice(0, 500);

  console.log("[/api/sarvam] → Sarvam TTS (bulbul:v2)", {
    chars: safeText.length,
    language,
  });

  try {
    const res = await fetch(SARVAM_TTS_URL, {
      method: "POST",
      headers: {
        "api-subscription-key": apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inputs: [safeText],
        target_language_code: language,
        // bulbul:v1 + its old speakers (meera, …) are deprecated; v2 speakers are
        // anushka, manisha, vidya, arya (female), karun, hitesh, abhilash (male), …
        speaker: "anushka",
        pitch: 0,
        pace: 1.0,
        loudness: 1.5,
        speech_sample_rate: 22050,
        enable_preprocessing: true,
        model: "bulbul:v2",
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error("[/api/sarvam] Sarvam TTS failed", res.status, errText);
      return NextResponse.json({ error: "TTS failed" }, { status: 502 });
    }

    const data = await res.json();
    const audio = Array.isArray(data.audios) ? data.audios[0] : null;
    if (!audio) {
      return NextResponse.json({ error: "No audio returned" }, { status: 502 });
    }

    // Base64-encoded WAV. The browser plays it via a data: URL.
    return NextResponse.json({ audio });
  } catch (err) {
    console.error("[/api/sarvam] error", err);
    return NextResponse.json({ error: "TTS error" }, { status: 500 });
  }
}
