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
 * Tap the mic ONCE: it auto-loops (listen → speak → listen) until scheme cards appear.
 */
export interface HeroLandingProps {
  site?: { title?: string; subtitleHi?: string; subtitleEn?: string };
  copy?: { ctaLine1?: string; ctaLine2?: string; paragraph?: string };
  splineUrl?: string;
  onHome?: () => void;
  onCall?: () => void;
  onProfile?: () => void;
}

const DEFAULTS = {
  site: { title: "Yojana Saathi", subtitleHi: "आपके हक़ की आवाज़", subtitleEn: "The voice of your rights" },
  copy: {
    ctaLine1: "Tell me your needs.",
    ctaLine2: "I'll find your scheme.",
    paragraph: "Speak in any of 23 Indian languages — I'll ask a few questions, then find every welfare scheme you and your family qualify for.",
  },
  splineUrl: "https://my.spline.design/customerservice-JllV1UmWKUimJfPZUQR4Bxgh/",
};

const SPEAK_LANGS = [
  "Speak your situation", "अपनी बात बोलिए", "আপনার কথা বলুন", "మీ సంగతి చెప్పండి",
  "तुमची परिस्थिती सांगा", "உங்கள் நிலையைச் சொல்லுங்கள்", "તમારી વાત કહો", "ನಿಮ್ಮ ಸ್ಥಿತಿ ಹೇಳಿ",
  "നിങ്ങളുടെ കാര്യം പറയൂ", "ਆਪਣੀ ਗੱਲ ਦੱਸੋ", "ଆପଣଙ୍କ କଥା କୁହନ୍ତୁ", "اپنی بات بتائیں",
  "আপোনাৰ কথা কওক", "आफ्नो कुरा भन्नुहोस्", "अपन बात कहू", "स्वस्थितिं वदतु",
];

// First glyph of each supported language — floats as glassy tiles in the background.
const LANG_GLYPHS = ["अ", "আ", "అ", "அ", "ಅ", "അ", "અ", "ਅ", "ଅ", "ا", "म", "ॐ", "ꯑ", "ᱚ", "न", "କ", "স", "ণ", "ক", "ఆ", "ਪ", "A"];
const CHIP_POS = [
  [8, 6, 90, 0], [16, 88, 72, 1.5], [30, 14, 64, 3], [40, 80, 96, 0.8],
  [54, 5, 80, 2.2], [62, 92, 60, 4], [73, 18, 88, 1], [82, 84, 72, 2.6],
  [12, 50, 56, 3.4], [88, 46, 64, 0.5], [25, 70, 60, 4.5], [48, 36, 52, 1.8],
  [68, 60, 56, 3.1], [90, 12, 80, 2], [6, 30, 60, 4.2], [36, 96, 56, 0.3],
  [78, 38, 52, 3.7], [20, 30, 52, 2.9], [58, 70, 60, 1.2], [44, 58, 48, 4.8],
  [70, 4, 64, 0.9], [94, 70, 56, 3.3],
];

const HomeIcon = () => (<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M3 11l9-8 9 8" /><path d="M5 10v10h14V10" /></svg>);
const PhoneIcon = () => (<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L20 13l-1 4-2 1A16 16 0 0 1 5 6z" /></svg>);
const ProfileIcon = () => (<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><circle cx="9" cy="8" r="3.2" /><path d="M3.5 20a5.5 5.5 0 0 1 11 0" /><path d="M19 8v6M22 11h-6" /></svg>);
const MicIcon = () => (<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" /></svg>);
const StopIcon = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2" /></svg>);

const MAX_MS = 10000, MIN_MS = 1200, MIN_BYTES = 8000;
type ChatTurn = { role: "user" | "bot"; text: string };
type Phase = "idle" | "listening" | "processing" | "speaking" | "results";

const CSS = `
@font-face{font-family:'Callen';src:url('/fonts/Callen-PERSONAL-USE-ONLY.ttf') format('truetype');font-weight:400 800;font-display:swap}
.ys-wrap{--ink:#f5f7f6;--mut:rgba(245,247,246,.56);--mut2:rgba(245,247,246,.36);--acc:#34d399;--acc2:#6ee7b7;--line:rgba(255,255,255,.06);--glass:rgba(255,255,255,.03);position:relative;width:100%;min-height:100vh;display:flex;flex-direction:column;overflow:hidden;background:radial-gradient(120% 80% at 50% -10%,#0b1411 0%,#070b09 55%,#040605 100%);font-family:'Inter','Helvetica Neue',sans-serif;isolation:isolate}
.ys-aur{position:absolute;border-radius:50%;filter:blur(100px);mix-blend-mode:screen;pointer-events:none;z-index:0}
.ys-aur.a1{width:660px;height:660px;left:-180px;top:-200px;background:radial-gradient(circle,#059669,transparent 64%);opacity:.5;animation:ys-dr1 28s ease-in-out infinite}
.ys-aur.a2{width:580px;height:580px;right:-180px;top:20px;background:radial-gradient(circle,#0d9488,transparent 64%);opacity:.42;animation:ys-dr2 33s ease-in-out infinite}
.ys-aur.a3{width:600px;height:600px;left:30%;bottom:-280px;background:radial-gradient(circle,#10b981,transparent 64%);opacity:.4;animation:ys-dr3 37s ease-in-out infinite}
@keyframes ys-dr1{50%{transform:translate(120px,90px) scale(1.16)}}
@keyframes ys-dr2{50%{transform:translate(-100px,70px) scale(1.12)}}
@keyframes ys-dr3{50%{transform:translate(80px,-90px) scale(1.2)}}
.ys-langbg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.ys-lang{position:absolute;display:grid;place-items:center;border-radius:18px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.05);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);color:rgba(167,243,208,.16);font-weight:600;animation:ys-float 14s ease-in-out infinite}
@keyframes ys-float{50%{transform:translateY(-22px) rotate(3deg)}}
.ys-grain{position:absolute;inset:0;opacity:.04;mix-blend-mode:overlay;pointer-events:none;z-index:1;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.ys-vig{position:absolute;inset:0;pointer-events:none;z-index:1;background:radial-gradient(125% 105% at 50% 40%,transparent 54%,rgba(0,0,0,.6) 100%)}
.ys-header{position:sticky;top:0;z-index:60;display:flex;justify-content:space-between;align-items:center;padding:16px clamp(18px,4vw,40px);background:rgba(8,11,9,.55);border-bottom:1px solid var(--line);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
.ys-brand{display:flex;align-items:center;gap:11px}
.ys-brand .dot{width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,var(--acc2),#0d9488);box-shadow:0 0 20px rgba(52,211,153,.35);display:grid;place-items:center;color:#04231a;font-weight:800;font-size:15px}
.ys-brand b{font-family:'Callen',serif;font-weight:700;font-size:19px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink)}
.ys-navr{display:flex;gap:10px}
.ys-ico{width:42px;height:42px;display:grid;place-items:center;border-radius:13px;background:var(--glass);border:1px solid var(--line);color:var(--ink);cursor:pointer;transition:transform .35s,box-shadow .35s,border-color .35s,background .35s}
.ys-ico:hover{transform:translateY(-2px);background:rgba(255,255,255,.06);border-color:rgba(52,211,153,.34);box-shadow:0 0 24px rgba(52,211,153,.16)}
.ys-hero{position:relative;z-index:4;flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;padding:clamp(48px,8vh,96px) 20px 80px}
.ys-title{font-family:'Callen',serif;font-size:clamp(54px,8.5vw,112px);line-height:.98;font-weight:700;letter-spacing:.05em;margin:0;text-transform:uppercase;background:linear-gradient(180deg,#fff,#d7f5e8 46%,#8fd3bb);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 2px 46px rgba(52,211,153,.18))}
.ys-sub{margin:22px 0 0;display:flex;align-items:center;gap:15px;font-size:16px;flex-wrap:wrap;justify-content:center}
.ys-sub .hi{color:rgba(245,247,246,.92);font-weight:500}
.ys-sub .d{width:4px;height:4px;border-radius:50%;background:var(--acc);opacity:.8}
.ys-sub .en{color:var(--mut);font-weight:300;letter-spacing:.08em}
.ys-cta{margin:42px 0 0;font-size:clamp(32px,4.8vw,58px);line-height:1.04;font-weight:600;letter-spacing:-.02em;color:var(--ink)}
.ys-cta span{background:linear-gradient(90deg,#fff,#9ff0d3);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.ys-p{margin:24px 0 0;max-width:480px;font-size:16px;line-height:1.78;font-weight:300;color:var(--mut2)}
.ys-go{margin-top:40px;display:inline-flex;align-items:center;gap:13px;min-width:248px;justify-content:center;padding:15px 28px 15px 15px;border-radius:999px;background:var(--glass);border:1px solid var(--line);color:var(--ink);font-size:15px;font-weight:500;cursor:pointer;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);transition:transform .4s,box-shadow .4s,border-color .4s}
.ys-go:hover{transform:translateY(-2px);border-color:rgba(52,211,153,.4);box-shadow:0 0 46px rgba(52,211,153,.2)}
.ys-go.live{border-color:rgba(52,211,153,.5);box-shadow:0 0 46px rgba(52,211,153,.22)}
.ys-go.rec{border-color:rgba(248,113,113,.5);box-shadow:0 0 46px rgba(248,113,113,.2)}
.ys-go .m{display:grid;place-items:center;width:38px;height:38px;border-radius:50%;background:rgba(52,211,153,.16);color:var(--acc);flex:none}
.ys-go.rec .m{background:rgba(248,113,113,.18);color:#fca5a5;animation:ys-pulse 1.1s ease-in-out infinite}
.ys-go.live .m{animation:ys-pulse 1.6s ease-in-out infinite}
@keyframes ys-pulse{50%{box-shadow:0 0 0 9px rgba(52,211,153,.1)}}
.ys-lbl{display:inline-block;animation:ys-fade .55s ease}
@keyframes ys-fade{from{opacity:0;transform:translateY(4px)}to{opacity:1}}
.ys-hint{margin-top:14px;font-size:12.5px;letter-spacing:.04em;color:var(--mut2)}
.ys-chat{width:100%;max-width:640px;margin:38px auto 0;display:flex;flex-direction:column;gap:12px}
.ys-bub{max-width:86%;padding:12px 16px;border-radius:18px;font-size:15px;line-height:1.55;text-align:left}
.ys-bub.u{align-self:flex-end;background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.2);color:#eafff6;border-bottom-right-radius:6px}
.ys-bub.b{align-self:flex-start;background:var(--glass);border:1px solid var(--line);color:var(--ink);border-bottom-left-radius:6px;backdrop-filter:blur(12px)}
.ys-bub .tag{display:block;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);opacity:.85;margin-bottom:4px}
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
.ys-type button{border-radius:12px;background:var(--acc);color:#04231a;border:none;padding:0 20px;font-weight:600;cursor:pointer}
.ys-stage{position:fixed;right:clamp(10px,2vw,28px);bottom:clamp(10px,2vw,24px);width:clamp(220px,22vw,300px);height:clamp(220px,22vw,300px);border-radius:50%;overflow:hidden;z-index:45;will-change:transform;transition:transform .12s ease-out;transform-style:preserve-3d}
.ys-stage::after{content:"";position:absolute;left:0;right:0;bottom:0;height:26%;background:linear-gradient(to top,#060807 42%,rgba(6,8,7,.6) 72%,transparent);pointer-events:none}
.ys-halo{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:108%;height:108%;border-radius:50%;background:radial-gradient(circle,rgba(52,211,153,.28) 0%,rgba(13,148,136,.14) 42%,transparent 70%);filter:blur(12px);pointer-events:none}
.ys-spline{position:absolute;left:50%;top:50%;transform:translate(-50%,-47%);width:150%;height:180%;border:0;background:transparent}
.ys-footer{position:relative;z-index:4;border-top:1px solid var(--line);background:rgba(6,9,7,.55);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
.ys-foot-grid{max-width:1080px;margin:0 auto;padding:46px clamp(20px,5vw,48px) 26px;display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:36px}
.ys-foot-brand b{font-family:'Callen',serif;font-weight:700;font-size:22px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink);display:block}
.ys-foot-brand p{margin:12px 0 0;font-size:13.5px;line-height:1.7;color:var(--mut);max-width:300px}
.ys-foot-col h4{margin:0 0 14px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);font-weight:600}
.ys-foot-col p{margin:0 0 9px;font-size:13.5px;color:var(--mut)}
.ys-foot-bottom{border-top:1px solid var(--line);padding:16px clamp(20px,5vw,48px);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:12.5px;color:var(--mut2)}
.ys-foot-bottom a{color:var(--mut2);text-decoration:none;margin-left:16px;transition:color .3s}
.ys-foot-bottom a:hover{color:var(--acc)}
@media(max-width:720px){.ys-foot-grid{grid-template-columns:1fr;gap:26px}.ys-stage{width:180px;height:180px}}
@media(prefers-reduced-motion:reduce){.ys-aur,.ys-lang,.ys-lbl{animation:none}}
`;

export default function HeroLanding({ site, copy, splineUrl = DEFAULTS.splineUrl, onHome, onCall, onProfile }: HeroLandingProps) {
  const s = { ...DEFAULTS.site, ...site };
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
  const autoRef = useRef(false); // true while the conversation auto-loops
  const stageRef = useRef<HTMLDivElement>(null);

  const started = chat.length > 0;

  const playAudio = useCallback((b64: string, onEnded?: () => void) => {
    try {
      const a = new Audio(`data:audio/wav;base64,${b64}`);
      audioRef.current = a;
      if (onEnded) a.onended = onEnded;
      a.play().catch(() => { if (onEnded) onEnded(); });
    } catch { if (onEnded) onEnded(); }
  }, []);

  // Defined before sendTurn but referenced via ref so the recorder closure stays fresh.
  const startRecordingRef = useRef<() => void>(() => {});

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
      if (res.action === "recommend") { setGroups(res.groups || []); autoRef.current = false; setPhase("results"); }
      else setGroups([]);

      const continueLoop = () => {
        if (res.action === "ask" && autoRef.current) startRecordingRef.current();
        else if (res.action !== "recommend") setPhase("idle");
      };
      if (res.message) {
        const b64 = await fetchTts(res.message, res.tts_language);
        if (res.action !== "recommend") setPhase("speaking");
        if (b64) { setLastBotAudio(b64); playAudio(b64, continueLoop); }
        else continueLoop();
      } else continueLoop();
    } catch (err) {
      console.error("[hero] /converse failed", err);
      setError(err instanceof Error && err.message ? err.message : "Something went wrong. Please try again.");
      autoRef.current = false;
      setPhase("idle");
    }
  }, [convState, playAudio]);

  const sendTurnRef = useRef(sendTurn);
  useEffect(() => { sendTurnRef.current = sendTurn; }, [sendTurn]);

  const pickMime = () => {
    const opts = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];
    for (const o of opts) if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(o)) return o;
    return "";
  };

  const stopRecording = () => {
    if (stopTimer.current) { clearTimeout(stopTimer.current); stopTimer.current = null; }
    if (recRef.current && recRef.current.state !== "inactive") recRef.current.stop();
    setIsRecording(false);
  };

  const startRecording = useCallback(async () => {
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
          autoRef.current = false;
          setError("मैंने सुना नहीं — बटन दबाएँ और 2–3 सेकंड बोलें।\nI didn't catch that — tap and speak for 2–3 seconds.");
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
      autoRef.current = false;
      setMicDenied(true);
      setError("Please allow microphone access to talk. You can also type your answer below.");
      setPhase("idle");
    }
  }, []);
  useEffect(() => { startRecordingRef.current = startRecording; }, [startRecording]);

  // Cycle the button label through languages while idle on the landing.
  useEffect(() => {
    if (started || phase !== "idle") return;
    const t = setInterval(() => setLangIdx((i) => (i + 1) % SPEAK_LANGS.length), 2200);
    return () => clearInterval(t);
  }, [started, phase]);

  // Orb stays FIXED bottom-right; only its orientation tilts toward the cursor.
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const el = stageRef.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      const max = 20;
      const ry = Math.max(-max, Math.min(max, ((e.clientX - cx) / (window.innerWidth / 2)) * max));
      const rx = Math.max(-max, Math.min(max, (-(e.clientY - cy) / (window.innerHeight / 2)) * max));
      el.style.transform = `perspective(780px) rotateX(${rx.toFixed(1)}deg) rotateY(${ry.toFixed(1)}deg)`;
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  const handleClick = () => {
    if (phase === "listening") { stopRecording(); return; }
    if (phase === "processing" || phase === "speaking") {
      autoRef.current = false;
      if (audioRef.current) audioRef.current.pause();
      setPhase(groups.length ? "results" : "idle");
      return;
    }
    autoRef.current = true; // begin the auto-loop (listen → speak → listen → … → cards)
    startRecording();
  };

  const submitText = () => {
    const t = textInput.trim();
    if (!t) return;
    setTextInput("");
    autoRef.current = false;
    sendTurn({ text: t });
  };

  const reset = () => {
    autoRef.current = false;
    setConvState(null); setChat([]); setGroups([]); setBotAction(null);
    setError(""); setLastBotAudio(null); setPhase("idle");
  };

  const busy = phase === "processing" || phase === "speaking";
  let label = SPEAK_LANGS[langIdx];
  if (phase === "listening") label = "Listening… (tap to stop)";
  else if (busy) label = "Speaking…";
  else if (started) label = "Ask a follow-up";

  return (
    <div className="ys-wrap">
      <style dangerouslySetInnerHTML={{ __html: CSS }} />
      <div className="ys-aur a1" /><div className="ys-aur a2" /><div className="ys-aur a3" />
      <div className="ys-langbg" aria-hidden="true">
        {CHIP_POS.map((p, i) => (
          <span className="ys-lang" key={i} style={{ top: `${p[0]}%`, left: `${p[1]}%`, width: p[2], height: p[2], fontSize: p[2] * 0.42, animationDelay: `${p[3]}s` }}>
            {LANG_GLYPHS[i % LANG_GLYPHS.length]}
          </span>
        ))}
      </div>
      <div className="ys-grain" /><div className="ys-vig" />

      <header className="ys-header">
        <div className="ys-brand">
          <span className="dot">य</span>
          <b>{s.title}</b>
        </div>
        <div className="ys-navr">
          <button className="ys-ico" aria-label="Home" onClick={onHome}><HomeIcon /></button>
          <button className="ys-ico" aria-label="Call" onClick={onCall}><PhoneIcon /></button>
          <button className="ys-ico" aria-label="Profile" onClick={onProfile}><ProfileIcon /></button>
        </div>
      </header>

      <main className="ys-hero">
        <h1 className="ys-title">{s.title}</h1>
        <p className="ys-sub"><span className="hi">{s.subtitleHi}</span><span className="d" /><span className="en">{s.subtitleEn}</span></p>

        {!started && (
          <>
            <h2 className="ys-cta">{c.ctaLine1}<br /><span>{c.ctaLine2}</span></h2>
            <p className="ys-p">{c.paragraph}</p>
          </>
        )}

        <button className={`ys-go${isRecording ? " rec" : busy ? " live" : ""}`} onClick={handleClick}>
          <span className="m">{isRecording ? <StopIcon /> : <MicIcon />}</span>
          <span className="ys-lbl" key={label}>{label}</span>
        </button>
        {!started && phase === "idle" && <p className="ys-hint">Tap once — I'll keep listening and replying until I find your schemes.</p>}

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

        {lastBotAudio && <button className="ys-replay" onClick={() => playAudio(lastBotAudio)}>🔊 सुनिए / Replay</button>}

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

      {/* SPLINE BOT — fixed bottom-right; orientation tilts toward the cursor.
          Scene: https://my.spline.design/customerservice-JllV1UmWKUimJfPZUQR4Bxgh/ */}
      <div className="ys-stage" ref={stageRef}>
        <div className="ys-halo" />
        {splineUrl ? <iframe className="ys-spline" src={splineUrl} title="Yojana Saathi assistant" loading="lazy" /> : null}
      </div>

      <footer className="ys-footer">
        <div className="ys-foot-grid">
          <div className="ys-foot-brand">
            <b>{s.title}</b>
            <p>{s.subtitleHi} — the voice of your rights. A voice-first helpline that finds the government welfare schemes you and your family qualify for, in your own language.</p>
          </div>
          <div className="ys-foot-col">
            <h4>Built with</h4>
            <p>Sarvam AI — speech &amp; language</p>
            <p>Google Gemini — embeddings</p>
            <p>MongoDB Atlas — vector search</p>
          </div>
          <div className="ys-foot-col">
            <h4>Reach</h4>
            <p>23 Indian languages</p>
            <p>150+ welfare schemes</p>
            <p>Voice-first · no reading</p>
          </div>
        </div>
        <div className="ys-foot-bottom">
          <span>© {new Date().getFullYear()} {s.title}. Built for Bharat.</span>
          <span><a href="#privacy">Privacy</a><a href="#terms">Terms</a><a href="#support">Support</a></span>
        </div>
      </footer>
    </div>
  );
}
