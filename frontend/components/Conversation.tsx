"use client";

import { useCallback, useRef, useState } from "react";
import VoiceOrb, { type OrbState } from "@/components/VoiceOrb";
import MicButton from "@/components/MicButton";
import SchemeCard from "@/components/SchemeCard";
import {
  converse,
  fetchTts,
  type BeneficiaryGroup,
  type ConverseState,
} from "@/lib/api";

type ChatTurn = { role: "user" | "bot"; text: string };

export default function Conversation() {
  const [phase, setPhase] = useState<OrbState>("idle");
  const [convState, setConvState] = useState<ConverseState | null>(null);
  const [chat, setChat] = useState<ChatTurn[]>([]);
  const [groups, setGroups] = useState<BeneficiaryGroup[]>([]);
  const [botAction, setBotAction] = useState<"ask" | "recommend" | null>(null);
  const [error, setError] = useState("");
  const [micDenied, setMicDenied] = useState(false);
  const [textInput, setTextInput] = useState("");
  const [lastBotAudio, setLastBotAudio] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const started = chat.length > 0 || convState !== null;

  const playAudio = useCallback((base64: string) => {
    try {
      const audio = new Audio(`data:audio/wav;base64,${base64}`);
      audioRef.current = audio;
      audio.play().catch((e) => console.warn("[page] autoplay blocked", e));
    } catch (e) {
      console.warn("[page] audio playback failed (ignored)", e);
    }
  }, []);

  // One conversation turn: send audio/text + the running state, then react to the
  // bot's reply (ask another question, or show the matched schemes). The reply is
  // always spoken aloud in the citizen's own language.
  const sendTurn = useCallback(
    async (input: { audio?: Blob; text?: string }) => {
      setPhase("processing");
      setError("");
      try {
        const res = await converse(input, convState);
        setConvState(res.state);
        setBotAction(res.action);

        setChat((prev) => {
          const next = [...prev];
          if (res.transcript) next.push({ role: "user", text: res.transcript });
          if (res.message) next.push({ role: "bot", text: res.message });
          return next;
        });

        if (res.action === "recommend") {
          setGroups(res.groups || []);
          setPhase("results");
        } else {
          setGroups([]);
          setPhase("idle"); // waiting for the citizen's next answer
        }

        // Speak the bot's message. TTS failure is non-fatal (text stays on screen).
        if (res.message) {
          const b64 = await fetchTts(res.message, res.tts_language);
          if (b64) {
            setLastBotAudio(b64);
            playAudio(b64);
          }
        }
      } catch (err) {
        console.error("[page] /converse failed", err);
        setError(
          err instanceof Error && err.message
            ? err.message
            : "Something went wrong. Please try again."
        );
        setPhase("idle");
      }
    },
    [convState, playAudio]
  );

  const submitText = async () => {
    const text = textInput.trim();
    if (!text) return;
    setTextInput("");
    await sendTurn({ text });
  };

  const resetConversation = () => {
    setConvState(null);
    setChat([]);
    setGroups([]);
    setBotAction(null);
    setError("");
    setLastBotAudio(null);
    setPhase("idle");
  };

  const micIdleLabel = !started
    ? "Speak your situation"
    : botAction === "recommend"
    ? "Ask about something else"
    : "Tap to answer";

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-2xl flex-col items-center px-4 py-10 sm:py-14">
      <header className="mb-4 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
          <span className="text-gradient">Yojana Sathi</span>
        </h1>
        <p className="mt-2 text-sm text-white/55 sm:text-base">
          आपकी आवाज़, आपका हक़ — सरकारी योजना हेल्पलाइन
        </p>
        <p className="mt-0.5 text-xs text-white/35">
          Speak in any Indian language · a helpline that talks with you and finds your schemes
        </p>
      </header>

      <VoiceOrb state={phase} />

      <div className="-mt-2">
        <MicButton
          pageState={phase}
          idleLabel={micIdleLabel}
          onListeningStart={() => {
            setError("");
            setPhase("listening");
          }}
          onProcessingStart={() => setPhase("processing")}
          onAudioReady={(audio) => sendTurn({ audio })}
          onError={(message) => {
            setError(message);
            setPhase("idle");
          }}
          onMicDenied={() => {
            setMicDenied(true);
            setError(
              "Please allow microphone access to talk. You can also type your answer below."
            );
            setPhase("idle");
          }}
        />
      </div>

      {!started && phase === "idle" && (
        <div className="mt-6 max-w-md text-center text-sm text-white/50">
          <p>अपनी स्थिति बताइए — मैं कुछ सवाल पूछकर आपके लिए सही योजनाएँ ढूँढूँगा।</p>
          <p className="mt-1">
            Tell me about yourself — I&apos;ll ask a few questions, then find the schemes you
            qualify for.
          </p>
        </div>
      )}

      {error && (
        <p className="mt-4 max-w-md whitespace-pre-line text-center text-sm text-red-400">
          {error}
        </p>
      )}

      {/* Text fallback (mic denied/unavailable) — also works as a typed answer each turn. */}
      {micDenied && (
        <div className="mt-4 flex w-full max-w-xl gap-2">
          <input
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submitText()}
            placeholder={started ? "Type your answer…" : "Type your situation…"}
            className="flex-1 rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/30 focus:border-accent focus:outline-none"
          />
          <button
            onClick={submitText}
            className="rounded-xl bg-accent px-5 py-3 text-sm font-semibold text-black"
          >
            Send
          </button>
        </div>
      )}

      {/* Conversation transcript — the back-and-forth with the helpline. */}
      {chat.length > 0 && (
        <section className="mt-6 flex w-full flex-col gap-3">
          {chat.map((t, i) => (
            <div
              key={i}
              className={`flex ${t.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  t.role === "user"
                    ? "rounded-br-sm bg-accent/15 text-white/90"
                    : "rounded-bl-sm border border-white/10 bg-white/5 text-white/85"
                }`}
              >
                {t.role === "bot" && (
                  <span className="mb-0.5 block text-[10px] uppercase tracking-wide text-accent/70">
                    Helpline
                  </span>
                )}
                {t.text}
              </div>
            </div>
          ))}
        </section>
      )}

      {lastBotAudio && (
        <button
          onClick={() => playAudio(lastBotAudio)}
          className="mt-4 flex items-center gap-2 rounded-full border border-white/15 px-4 py-2 text-sm text-white/80 hover:bg-white/10"
        >
          🔊 सुनिए / Replay
        </button>
      )}

      {/* Recommendations, grouped per beneficiary (you + each family member). */}
      {groups.length > 0 && (
        <section className="mt-8 flex w-full flex-col items-center gap-9">
          {groups.map((g, gi) => (
            <div key={g.relation + gi} className="flex w-full flex-col items-center gap-4">
              <div className="flex items-center gap-3 text-center">
                <span className="h-px w-8 bg-white/15" />
                <h2 className="text-base font-semibold text-white/80 sm:text-lg">
                  <span className="text-accent">{g.label}</span>
                  <span className="ml-2 text-sm font-normal text-white/45">
                    {g.schemes.length} scheme{g.schemes.length > 1 ? "s" : ""}
                  </span>
                </h2>
                <span className="h-px w-8 bg-white/15" />
              </div>
              {g.schemes.map((s, i) => (
                <SchemeCard key={g.relation + s.name} scheme={s} index={i} />
              ))}
            </div>
          ))}
        </section>
      )}

      {started && (
        <button
          onClick={resetConversation}
          className="mt-8 text-xs text-white/40 underline-offset-4 hover:text-white/70 hover:underline"
        >
          ↺ Start a new conversation
        </button>
      )}

      <footer className="mt-12 flex items-center gap-2 text-xs text-white/30">
        <span className="h-1.5 w-1.5 rounded-full bg-accent/70" />
        Powered by Sarvam AI · Gemini · MongoDB Atlas Vector Search
      </footer>
    </main>
  );
}
