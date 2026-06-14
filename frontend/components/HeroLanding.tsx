"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import SchemeCard from "@/components/SchemeCard";
import {
  converse,
  fetchTts,
  type BeneficiaryGroup,
  type ConverseState,
} from "@/lib/api";

/**
 * HeroLanding — the dark luxury landing AND the voice conversation, on ONE page.
 * Tapping the mic records, calls /converse, and renders questions + grouped results
 * inline in this same hero. No navigation away.
 */
export interface HeroLandingProps {
  site?: { title?: string; subtitleHi?: string; subtitleEn?: string };
  user?: { firstName?: string };
  copy?: { ctaLine1?: string; ctaLine2?: string; paragraph?: string };
  /** Public Spline scene embedded in the bot stage. */
  splineUrl?: string;
  onHome?: () => void;
  onCall?: () => void;
  onProfile?: () => void;
}

const DEFAULTS = {
  site: { title: "Yojna Sathi", subtitleHi: "आपके हक़ की आवाज़", subtitleEn: "The voice of your rights" },
  user: { firstName: "" },
  copy: {
    ctaLine1: "Tell me your needs.",
    ctaLine2: "I'll find your scheme.",
    paragraph: "I'm here to help — from quick answers to smart recommendations.",
  },
  splineUrl: "https://my.spline.design/customerservice-JllV1UmWKUimJfPZUQR4Bxgh/",
};

// "Speak your situation" cycled through the languages Saaras understands. Edit freely —
// the rare-script lines are best-effort; have a native speaker confirm before the demo.
const SPEAK_LANGS = [
  "Speak your situation",
  "अपनी बात बोलिए",
  "আপনার কথা বলুন",
  "మీ సంగతి చెప్పండి",
  "तुमची परिस्थिती सांगा",
  "உங்கள் நிலையைச் சொல்லுங்கள்",
  "તમારી વાત કહો",
  "ನಿಮ್ಮ ಸ್ಥಿತಿ ಹೇಳಿ",
  "നിങ്ങളുടെ കാര്യം പറയൂ",
  "ਆਪਣੀ ਗੱਲ ਦੱਸੋ",
  "ଆପଣଙ୍କ କଥା କୁହନ୍ତୁ",
  "اپنی بات بتائیں",
  "আপোনাৰ কথা কওক",
  "आफ्नो कुरा भन्नुहोस्",
  "तुमची स्थिती सांगा",
  "अपन बात कहू",
  "अपनी गल्ल दस्सो",
  "پنھنجي ڳالهه ٻڌايو",
  "स्वस्थितिं वदतु",
];

const HomeIcon = () => (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M3 11l9-8 9 8" /><path d="M5 10v10h14V10" /></svg>);
const PhoneIcon = () => (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L20 13l-1 4-2 1A16 16 0 0 1 5 6z" /></svg>);
const ProfileIcon = () => (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><circle cx="9" cy="8" r="3.2" /><path d="M3.5 20a5.5 5.5 0 0 1 11 0" /><path d="M19 8v6M22 11h-6" /></svg>);
const MicIcon = () => (<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" /></svg>);
const StopIcon = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2" /></svg>);

const MAX_MS = 10000, MIN_MS = 1200, MIN_BYTES = 8000;
type ChatTurn = { role: "user" | "bot"; text: string };
type Phase = "idle" | "listening" | "processing" | "results";

const CSS = `
@font-face{font-family:'GC Epic Pro';src:url('/fonts/gc-epicpro.woff2') format('woff2'),url('/fonts/gc-epicpro.otf') format('opentype'),url('/fonts/gc-epicpro.ttf') format('truetype');font-weight:400 800;font-display:swap}
.ys-wrap{--ink:#f5f7f6;--mut:rgba(245,247,246,.56);--mut2:rgba(245,247,246,.36);--acc:#6ee7b7;--line:rgba(255,255,255,.06);--glass:rgba(255,255,255,.03);position:relative;width:100%;min-height:100vh;overflow:hidden;background:radial-gradient(125% 95% at 50% -8%,#0e1118 0%,#070809 56%,#040405 100%);font-family:'Inter','Helvetica Neue',sans-serif;isolation:isolate}
.ys-aur{position:absolute;border-radius:50%;filter:blur(95px);mix-blend-mode:screen;pointer-events:none}
.ys-aur.a1{width:640px;height:640px;left:-180px;top:-200px;background:radial-gradient(circle,#1e40af,transparent 64%);opacity:.55;animation:ys-dr1 26s ease-in-out infinite}
.ys-aur.a2{width:560px;height:560px;right:-170px;top:30px;background:radial-gradient(circle,#7c3aed,transparent 64%);opacity:.5;animation:ys-dr2 31s ease-in-out infinite}
.ys-aur.a3{width:560px;height:560px;left:28%;bottom:-260px;background:radial-gradient(circle,#0d9488,transparent 64%);opacity:.45;animation:ys-dr3 35s ease-in-out infinite}
@keyframes ys-dr1{50%{transform:translate(130px,90px) scale(1.18)}}
@keyframes ys-dr2{50%{transform:translate(-110px,70px) scale(1.12)}}
@keyframes ys-dr3{50%{transform:translate(90px,-100px) scale(1.22)}}
.ys-grain{position:absolute;inset:0;opacity:.045;mix-blend-mode:overlay;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.ys-vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(125% 105% at 50% 42%,transparent 52%,rgba(0,0,0,.62) 100%)}
.ys-nav{position:absolute;top:26px;left:26px;right:26px;display:flex;justify-content:space-between;align-items:center;z-index:6}
.ys-ico{width:46px;height:46px;display:grid;place-items:center;border-radius:14px;background:var(--glass);border:1px solid var(--line);color:var(--ink);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);cursor:pointer;transition:transform .4s,box-shadow .4s,border-color .4s,background .4s}
.ys-ico:hover{transform:translateY(-2px);background:rgba(255,255,255,.06);border-color:rgba(110,231,183,.32);box-shadow:0 0 26px rgba(110,231,183,.14)}
.ys-navr{display:flex;gap:12px}
.ys-hero{position:relative;z-index:4;display:flex;flex-direction:column;align-items:center;text-align:center;padding:clamp(72px,9vh,120px) 20px 90px}
.ys-title{font-family:'GC Epic Pro','gc epicpro','Times New Roman',serif;font-size:clamp(54px,8.5vw,108px);line-height:.98;font-weight:400;letter-spacing:.045em;margin:0;background:linear-gradient(180deg,#fff,#e3f0ea 46%,#a4c8ba);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 2px 44px rgba(110,231,183,.15))}
.ys-sub{margin:22px 0 0;display:flex;align-items:center;gap:15px;font-size:16px;flex-wrap:wrap;justify-content:center}
.ys-sub .hi{color:rgba(245,247,246,.92);font-weight:500}
.ys-sub .d{width:4px;height:4px;border-radius:50%;background:var(--acc);opacity:.75}
.ys-sub .en{color:var(--mut);font-weight:300;letter-spacing:.08em}
.ys-stage{position:relative;width:clamp(300px,34vw,440px);height:clamp(300px,34vw,440px);margin:clamp(40px,6vh,72px) 0 clamp(36px,5vh,56px);border-radius:30px;overflow:hidden}
.ys-halo{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:118%;height:118%;border-radius:50%;background:radial-gradient(circle,rgba(110,231,183,.16),rgba(124,58,237,.08) 45%,transparent 66%);filter:blur(14px);pointer-events:none}
.ys-spline{position:absolute;left:50%;top:50%;transform:translate(-50%,-53%);width:120%;height:134%;border:0;background:transparent}
.ys-stage::after{content:"";position:absolute;left:0;right:0;bottom:0;height:24%;background:linear-gradient(to top,#070809 18%,transparent);pointer-events:none}
.ys-greet{margin:0;font-size:18px;font-weight:300;letter-spacing:.16em;color:var(--mut)}
.ys-cta{margin:14px 0 0;font-size:clamp(32px,4.8vw,56px);line-height:1.05;font-weight:600;letter-spacing:-.02em;color:var(--ink)}
.ys-cta span{background:linear-gradient(90deg,#fff,#bfeede);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.ys-p{margin:26px 0 0;max-width:440px;font-size:16px;line-height:1.78;font-weight:300;color:var(--mut2)}
.ys-go{margin-top:36px;display:inline-flex;align-items:center;gap:13px;min-width:230px;justify-content:center;padding:14px 26px 14px 14px;border-radius:999px;background:var(--glass);border:1px solid var(--line);color:var(--ink);font-size:15px;font-weight:500;cursor:pointer;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);transition:transform .4s,box-shadow .4s,border-color .4s}
.ys-go:hover{transform:translateY(-2px);border-color:rgba(110,231,183,.36);box-shadow:0 0 44px rgba(110,231,183,.18)}
.ys-go.rec{border-color:rgba(248,113,113,.5);box-shadow:0 0 44px rgba(248,113,113,.18)}
.ys-go .m{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:rgba(110,231,183,.14);color:var(--acc);flex:none}
.ys-go.rec .m{background:rgba(248,113,113,.18);color:#fca5a5;animation:ys-pulse 1.2s ease-in-out infinite}
@keyframes ys-pulse{50%{box-shadow:0 0 0 8px rgba(248,113,113,.12)}}
.ys-lbl{display:inline-block;animation:ys-fade .55s ease}
@keyframes ys-fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.ys-chat{width:100%;max-width:640px;margin:34px auto 0;display:flex;flex-direction:column;gap:12px}
.ys-bub{max-width:86%;padding:12px 16px;border-radius:18px;font-size:15px;line-height:1.55;text-align:left}
.ys-bub.u{align-self:flex-end;background:rgba(110,231,183,.12);border:1px solid rgba(110,231,183,.18);color:#eafff6;border-bottom-right-radius:6px}
.ys-bub.b{align-self:flex-start;background:var(--glass);border:1px solid var(--line);color:var(--ink);border-bottom-left-radius:6px;backdrop-filter:blur(12px)}
.ys-bub .tag{display:block;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);opacity:.8;margin-bottom:4px}
.ys-replay{margin:18px auto 0;display:inline-flex;align-items:center;gap:8px;padding:9px 18px;border-radius:999px;background:transparent;border:1px solid var(--line);color:var(--mut);font-size:13px;cursor:pointer}
.ys-groups{width:100%;max-width:680px;margin:34px auto 0;display:flex;flex-direction:column;gap:34px}
.ys-ghd{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:14px}
.ys-ghd .ln{height:1px;width:30px;background:var(--line)}
.ys-ghd h3{font-size:17px;font-weight:500;color:rgba(245,247,246,.85);margin:0}
.ys-ghd .cnt{color:var(--mut2);font-size:13px;margin-left:6px}
.ys-gcards{display:flex;flex-direction:column;align-items:center;gap:18px}
.ys-err{margin:16px auto 0;max-width:440px;color:#fca5a5;font-size:14px;white-space:pre-line}
.ys-reset{margin:30px auto 0;display:block;background:none;border:none;color:var(--mut2);font-size:13px;cursor:pointer;text-decoration:underline;text-underline-offset:4px}
.ys-type{margin:16px auto 0;display:flex;gap:8px;width:100%;max-width:560px}
.ys-type input{flex:1;border-radius:12px;border:1px solid var(--line);background:rgba(255,255,255,.04);padding:12px 16px;font-size:14px;color:var(--ink);outline:none}
.ys-type button{border-radius:12px;background:var(--acc);color:#06241a;border:none;padding:0 20px;font-weight:600;cursor:pointer}
@media (prefers-reduced-motion: reduce){.ys-aur,.ys-lbl{animation:none}}
`;

export default function HeroLanding({ site, user, copy, splineUrl = DEFAULTS.splineUrl, onHome, onCall, onProfile }: HeroLandingProps) {
  const s = { ...DEFAULTS.site, ...site };
  const u = { ...DEFAULTS.user, ...user };
  const c = { ...DEFAULTS.copy, ...copy };

  const [phase, setPhase] = useState<Phase>("idle");
  const [convState, setConvState] = useState<ConverseState | null>(null);
  const [chat, setChat] = useState<ChatTurn[]>([]);
  const [groups, setGroups] = useState<BeneficiaryGroup[]>([]);
  const [botAction, setBotAction] = useState<"ask" | "recommend" | null>(null);
  const [error, setError] = useState("");
  const [micDenied, setMicDenied] = useState(false);
  const [textInput, setTextInput] = useState("");
  const [lastBotAudio, setLastBotAudio] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [langIdx, setLangIdx] = useState(0);

  const recRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const stopTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startTs = useRef(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const started = chat.length > 0;

  const playAudio = useCallback((b64: string) => {
    try {
      const a = new Audio(`data:audio/wav;base64,${b64}`);
      audioRef.current = a;
      a.play().catch((e) => console.warn("[hero] autoplay blocked", e));
    } catch (e) { console.warn("[hero] audio failed", e); }
  }, []);

  const sendTurn = useCallback(async (input: { audio?: Blob; text?: string }) => {
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
      if (res.action === "recommend") { setGroups(res.groups || []); setPhase("results"); }
      else { setGroups([]); setPhase("idle"); }
      if (res.message) {
        const b64 = await fetchTts(res.message, res.tts_language);
        if (b64) { setLastBotAudio(b64); playAudio(b64); }
      }
    } catch (err) {
      console.error("[hero] /converse failed", err);
      setError(err instanceof Error && err.message ? err.message : "Something went wrong. Please try again.");
      setPhase("idle");
    }
  }, [convState, playAudio]);

  // Keep the latest sendTurn reachable from the recorder's onstop closure.
  const sendTurnRef = useRef(sendTurn);
  useEffect(() => { sendTurnRef.current = sendTurn; }, [sendTurn]);

  // Cycle the button label through languages while idle on the landing.
  useEffect(() => {
    if (started || phase !== "idle") return;
    const t = setInterval(() => setLangIdx((i) => (i + 1) % SPEAK_LANGS.length), 2200);
    return () => clearInterval(t);
  }, [started, phase]);

  const pickMime = () => {
    const opts = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];
    for (const o of opts) if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(o)) return o;
    return "";
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = pickMime();
      const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      recRef.current = rec;
      chunksRef.current = [];
      rec.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      rec.onstop = () => {
        rec.stream.getTracks().forEach((t) => t.stop());
        const elapsed = Date.now() - startTs.current;
        const blob = new Blob(chunksRef.current, { type: mime || "audio/webm" });
        if (blob.size < MIN_BYTES || elapsed < MIN_MS) {
          setError("मैंने सुना नहीं — माइक दबाएँ, 2–3 सेकंड बोलें, फिर दबाएँ।\nI didn't catch that — tap, speak for 2–3 seconds, then tap again.");
          setPhase("idle");
          return;
        }
        sendTurnRef.current({ audio: blob });
      };
      rec.start(250);
      startTs.current = Date.now();
      setIsRecording(true);
      setError("");
      setPhase("listening");
      stopTimer.current = setTimeout(stopRecording, MAX_MS);
    } catch (err) {
      console.error("[hero] mic denied", err);
      setMicDenied(true);
      setError("Please allow microphone access to talk. You can also type your answer below.");
      setPhase("idle");
    }
  };

  const stopRecording = () => {
    if (stopTimer.current) { clearTimeout(stopTimer.current); stopTimer.current = null; }
    if (recRef.current && recRef.current.state !== "inactive") recRef.current.stop();
    setIsRecording(false);
  };

  const toggle = () => {
    if (phase === "processing") return;
    if (isRecording) stopRecording(); else startRecording();
  };

  const submitText = () => {
    const t = textInput.trim();
    if (!t) return;
    setTextInput("");
    sendTurn({ text: t });
  };

  const reset = () => {
    setConvState(null); setChat([]); setGroups([]); setBotAction(null);
    setError(""); setLastBotAudio(null); setPhase("idle");
  };

  let label = SPEAK_LANGS[langIdx];
  if (phase === "listening") label = "Listening… tap to stop";
  else if (phase === "processing") label = "Thinking…";
  else if (started && botAction === "ask") label = "Tap to answer";
  else if (started && botAction === "recommend") label = "Ask about something else";

  return (
    <div className="ys-wrap">
      <style dangerouslySetInnerHTML={{ __html: CSS }} />
      <div className="ys-aur a1" /><div className="ys-aur a2" /><div className="ys-aur a3" />
      <div className="ys-grain" /><div className="ys-vig" />

      <nav className="ys-nav">
        <button className="ys-ico" aria-label="Home" onClick={onHome}><HomeIcon /></button>
        <div className="ys-navr">
          <button className="ys-ico" aria-label="Call" onClick={onCall}><PhoneIcon /></button>
          <button className="ys-ico" aria-label="Profile" onClick={onProfile}><ProfileIcon /></button>
        </div>
      </nav>

      <main className="ys-hero">
        <h1 className="ys-title">{s.title}</h1>
        <p className="ys-sub"><span className="hi">{s.subtitleHi}</span><span className="d" /><span className="en">{s.subtitleEn}</span></p>

        {/* ───────────────────────────────────────────────────────────────
            SPLINE BOT — cursor-interactive 3D assistant
            Scene: https://my.spline.design/customerservice-JllV1UmWKUimJfPZUQR4Bxgh/
            The stage is overflow-hidden and the iframe is scaled up + nudged so the
            free-plan "Built with Spline" badge (bottom-right) is cropped out.
            ─────────────────────────────────────────────────────────────── */}
        <div className="ys-stage">
          <div className="ys-halo" />
          {splineUrl ? <iframe className="ys-spline" src={splineUrl} title="Yojna Sathi assistant" loading="lazy" /> : null}
        </div>

        {!started && (
          <>
            {/* <p className="ys-greet">Hi{u.firstName}!</p> */}
            <h2 className="ys-cta">{c.ctaLine1}<br /><span>{c.ctaLine2}</span></h2>
            <p className="ys-p">{c.paragraph}</p>
          </>
        )}

        <button className={`ys-go${isRecording ? " rec" : ""}`} onClick={toggle} disabled={phase === "processing"}>
          <span className="m">{isRecording ? <StopIcon /> : <MicIcon />}</span>
          <span className="ys-lbl" key={label}>{label}</span>
        </button>

        {error && <p className="ys-err">{error}</p>}

        {micDenied && (
          <div className="ys-type">
            <input value={textInput} onChange={(e) => setTextInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && submitText()} placeholder={started ? "Type your answer…" : "Type your situation…"} />
            <button onClick={submitText}>Send</button>
          </div>
        )}

        {chat.length > 0 && (
          <section className="ys-chat">
            {chat.map((t, i) => (
              <div key={i} className={`ys-bub ${t.role === "user" ? "u" : "b"}`}>
                {t.role === "bot" && <span className="tag">Helpline</span>}
                {t.text}
              </div>
            ))}
          </section>
        )}

        {lastBotAudio && (
          <button className="ys-replay" onClick={() => playAudio(lastBotAudio)}>🔊 सुनिए / Replay</button>
        )}

        {groups.length > 0 && (
          <section className="ys-groups">
            {groups.map((g, gi) => (
              <div key={g.relation + gi}>
                <div className="ys-ghd"><span className="ln" /><h3>{g.label}<span className="cnt">{g.schemes.length} scheme{g.schemes.length > 1 ? "s" : ""}</span></h3><span className="ln" /></div>
                <div className="ys-gcards">{g.schemes.map((sc, i) => <SchemeCard key={g.relation + sc.name} scheme={sc} index={i} />)}</div>
              </div>
            ))}
          </section>
        )}

        {started && <button className="ys-reset" onClick={reset}>↺ Start a new conversation</button>}
      </main>
    </div>
  );
}
