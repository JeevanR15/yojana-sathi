"use client";

import { useCallback, useRef, useState } from "react";
import VoiceOrb, { type OrbState } from "@/components/VoiceOrb";
import MicButton from "@/components/MicButton";
import SchemeCard from "@/components/SchemeCard";
import TranscriptDisplay from "@/components/TranscriptDisplay";
import {
  fetchTts,
  matchSchemesFromText,
  type MatchResponse,
  type Scheme,
} from "@/lib/api";

export default function Home() {
  const [state, setState] = useState<OrbState>("idle");
  const [transcript, setTranscript] = useState("");
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [error, setError] = useState("");
  const [micDenied, setMicDenied] = useState(false);
  const [textInput, setTextInput] = useState("");
  const [audioBase64, setAudioBase64] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const playAudio = useCallback((base64: string) => {
    try {
      const audio = new Audio(`data:audio/wav;base64,${base64}`);
      audioRef.current = audio;
      audio.play().catch((e) => console.warn("[page] autoplay blocked", e));
    } catch (e) {
      console.warn("[page] audio playback failed (ignored)", e);
    }
  }, []);

  // Shared by both the voice path and the text fallback.
  const handleResults = useCallback(
    async (data: MatchResponse) => {
      setTranscript(data.transcript || "");
      setSchemes(data.schemes || []);
      setError("");
      setState("results");

      // Speak the top explanation aloud. TTS failure is non-fatal.
      if (data.audio_explanation_text) {
        const b64 = await fetchTts(data.audio_explanation_text);
        if (b64) {
          setAudioBase64(b64);
          playAudio(b64);
        }
      }
    },
    [playAudio]
  );

  const handleError = useCallback((message: string) => {
    setError(message);
    setState("idle");
  }, []);

  const submitText = async () => {
    const text = textInput.trim();
    if (!text) return;
    setState("processing");
    setError("");
    setSchemes([]);
    try {
      const data = await matchSchemesFromText(text);
      await handleResults(data);
    } catch (err) {
      console.error("[page] text match failed", err);
      handleError("Could not process your request. Please try again.");
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center px-4 py-10">
      <header className="mb-6 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Yojana <span className="text-accent">Sathi</span>
        </h1>
        <p className="mt-1 text-sm text-white/50">
          आपकी आवाज़, आपका हक़ — सरकारी योजनाएँ खोजें
        </p>
      </header>

      <VoiceOrb state={state} />

      <div className="mt-2">
        <MicButton
          pageState={state}
          onListeningStart={() => {
            setError("");
            setSchemes([]);
            setTranscript("");
            setAudioBase64(null);
            setState("listening");
          }}
          onProcessingStart={() => setState("processing")}
          onResults={handleResults}
          onError={handleError}
          onMicDenied={() => {
            setMicDenied(true);
            handleError(
              "Please allow microphone access to use voice. You can also type your situation below."
            );
          }}
        />
      </div>

      {state === "idle" && schemes.length === 0 && (
        <div className="mt-6 max-w-md text-center text-sm text-white/50">
          <p>अपनी स्थिति बताइए — उम्र, राज्य, काम, और कोई कार्ड।</p>
          <p className="mt-1">Tell us your age, state, work, and any cards you have.</p>
        </div>
      )}

      {error && (
        <p className="mt-4 max-w-md text-center text-sm text-red-400">{error}</p>
      )}

      {/* Text fallback appears if the mic is denied/unavailable. */}
      {micDenied && (
        <div className="mt-4 flex w-full max-w-xl gap-2">
          <input
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submitText()}
            placeholder="Type your situation, e.g. 60 साल की विधवा, बिहार, BPL कार्ड…"
            className="flex-1 rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/30 focus:border-accent focus:outline-none"
          />
          <button
            onClick={submitText}
            className="rounded-xl bg-accent px-5 py-3 text-sm font-semibold text-black"
          >
            Find
          </button>
        </div>
      )}

      <TranscriptDisplay transcript={transcript} />

      {state === "results" && audioBase64 && (
        <button
          onClick={() => playAudio(audioBase64)}
          className="mt-4 flex items-center gap-2 rounded-full border border-white/15 px-4 py-2 text-sm text-white/80 hover:bg-white/10"
        >
          🔊 सुनिए / Replay explanation
        </button>
      )}

      {schemes.length > 0 && (
        <section className="mt-6 flex w-full flex-col items-center gap-4">
          <h2 className="text-lg font-semibold text-white/80">
            आपके लिए {schemes.length} योजनाएँ — Top {schemes.length} schemes for you
          </h2>
          {schemes.map((s, i) => (
            <SchemeCard key={s.name} scheme={s} index={i} />
          ))}
        </section>
      )}

      <footer className="mt-12 text-xs text-white/30">
        Powered by Sarvam AI · Gemini · MongoDB Atlas Vector Search
      </footer>
    </main>
  );
}
