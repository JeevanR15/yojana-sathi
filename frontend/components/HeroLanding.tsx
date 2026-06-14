"use client";

import { useRef } from "react";

/**
 * HeroLanding — the dark, luxury landing hero for Yojna Sathi.
 *
 * Data-binding ready: every piece of copy comes from props so your backend can map
 * straight in (e.g. <HeroLanding site={site} user={user} copy={copy} />). All props are
 * optional and fall back to the default content.
 */
export interface HeroLandingProps {
  site?: { title?: string; subtitleHi?: string; subtitleEn?: string };
  user?: { firstName?: string };
  copy?: {
    greeting?: string; // supports "{firstName}" token
    ctaLine1?: string;
    ctaLine2?: string;
    paragraph?: string;
    ctaButton?: string;
  };
  /** Public Spline scene embedded in the bot stage. */
  splineUrl?: string;
  onStart?: () => void;
  onHome?: () => void;
  onCall?: () => void;
  onProfile?: () => void;
}

const DEFAULTS = {
  site: {
    title: "Yojna Sathi",
    subtitleHi: "आपके हक़ की आवाज़",
    subtitleEn: "The voice of your rights",
  },
  user: { firstName: "Aarav" },
  copy: {
    greeting: "Hi, {firstName}!",
    ctaLine1: "Tell me your needs.",
    ctaLine2: "I'll find your scheme.",
    paragraph: "I'm here to help — from quick answers to smart recommendations.",
    ctaButton: "Speak your situation",
  },
  splineUrl: "https://my.spline.design/customerservice-JllV1UmWKUimJfPZUQR4Bxgh/",
};

const HomeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M3 11l9-8 9 8" /><path d="M5 10v10h14V10" /></svg>
);
const PhoneIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L20 13l-1 4-2 1A16 16 0 0 1 5 6z" /></svg>
);
const ProfileIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><circle cx="9" cy="8" r="3.2" /><path d="M3.5 20a5.5 5.5 0 0 1 11 0" /><path d="M19 8v6M22 11h-6" /></svg>
);
const MicIcon = () => (
  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" /></svg>
);

const CSS = `
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
.ys-hero{position:relative;z-index:4;display:flex;flex-direction:column;align-items:center;text-align:center;padding:clamp(104px,14vh,180px) 24px 96px}
.ys-title{font-family:'gc epicpro','GC Epic Pro','Times New Roman',serif;font-size:clamp(54px,8.5vw,108px);line-height:.98;font-weight:400;letter-spacing:.045em;margin:0;background:linear-gradient(180deg,#fff,#e3f0ea 46%,#a4c8ba);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 2px 44px rgba(110,231,183,.15))}
.ys-sub{margin:24px 0 0;display:flex;align-items:center;gap:15px;font-size:16px}
.ys-sub .hi{color:rgba(245,247,246,.92);font-weight:500;letter-spacing:.01em}
.ys-sub .d{width:4px;height:4px;border-radius:50%;background:var(--acc);opacity:.75}
.ys-sub .en{color:var(--mut);font-weight:300;letter-spacing:.08em}
.ys-stage{position:relative;width:clamp(240px,26vw,340px);height:clamp(240px,26vw,340px);margin:clamp(64px,8vh,96px) 0 clamp(56px,7vh,84px);display:grid;place-items:center;will-change:transform;transition:transform .25s ease-out}
.ys-halo{position:absolute;width:128%;height:128%;border-radius:50%;background:radial-gradient(circle,rgba(110,231,183,.16),rgba(124,58,237,.08) 45%,transparent 66%);filter:blur(14px);pointer-events:none}
.ys-spline{position:absolute;inset:0;width:100%;height:100%;border:0;background:transparent}
.ys-orb{position:relative;width:62%;height:62%;border-radius:50%;background:radial-gradient(circle at 34% 28%,rgba(255,255,255,.92),rgba(186,205,255,.32) 38%,rgba(60,78,150,.18) 70%);box-shadow:inset 0 0 46px rgba(255,255,255,.28),inset 0 -18px 40px rgba(40,60,140,.4),0 0 70px rgba(90,130,255,.22);animation:ys-flo 6.5s ease-in-out infinite}
.ys-orb::after{content:"";position:absolute;inset:-10px;border-radius:50%;border:1px solid rgba(255,255,255,.08);animation:ys-spin 18s linear infinite}
.ys-orb::before{content:"";position:absolute;inset:14px;border-radius:50%;background:conic-gradient(from 0deg,transparent,rgba(110,231,183,.35),transparent 55%);opacity:.5;animation:ys-spin 9s linear infinite reverse;mix-blend-mode:screen}
@keyframes ys-flo{50%{transform:translateY(-13px)}}
@keyframes ys-spin{to{transform:rotate(360deg)}}
.ys-greet{margin:0;font-size:18px;font-weight:300;letter-spacing:.16em;color:var(--mut)}
.ys-cta{margin:16px 0 0;font-size:clamp(32px,4.8vw,56px);line-height:1.05;font-weight:600;letter-spacing:-.02em;color:var(--ink)}
.ys-cta span{background:linear-gradient(90deg,#fff,#bfeede);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.ys-p{margin:28px 0 0;max-width:440px;font-size:16px;line-height:1.78;font-weight:300;letter-spacing:.015em;color:var(--mut2)}
.ys-go{margin-top:40px;display:inline-flex;align-items:center;gap:13px;padding:14px 26px 14px 14px;border-radius:999px;background:var(--glass);border:1px solid var(--line);color:var(--ink);font-size:15px;font-weight:500;letter-spacing:.01em;cursor:pointer;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);transition:transform .4s,box-shadow .4s,border-color .4s}
.ys-go:hover{transform:translateY(-2px);border-color:rgba(110,231,183,.36);box-shadow:0 0 44px rgba(110,231,183,.18)}
.ys-go .m{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:rgba(110,231,183,.14);color:var(--acc)}
.ys-up{opacity:0;animation:ys-up 1s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes ys-up{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){.ys-aur,.ys-orb,.ys-orb::before,.ys-orb::after,.ys-up{animation:none}.ys-up{opacity:1}}
`;

export default function HeroLanding({
  site,
  user,
  copy,
  splineUrl = DEFAULTS.splineUrl,
  onStart,
  onHome,
  onCall,
  onProfile,
}: HeroLandingProps) {
  const s = { ...DEFAULTS.site, ...site };
  const u = { ...DEFAULTS.user, ...user };
  const c = { ...DEFAULTS.copy, ...copy };
  const greeting = c.greeting.replace("{firstName}", u.firstName ?? "");

  const stageRef = useRef<HTMLDivElement>(null);

  // Cursor parallax on the bot stage (mirrors the Spline scene's cursor interactivity).
  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const el = stageRef.current;
    if (!el) return;
    const r = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    el.style.transform = `translate(${(x * 30).toFixed(1)}px, ${(y * 24).toFixed(1)}px)`;
  };
  const onLeave = () => {
    if (stageRef.current) stageRef.current.style.transform = "translate(0,0)";
  };

  return (
    <div className="ys-wrap" onMouseMove={onMove} onMouseLeave={onLeave}>
      <style dangerouslySetInnerHTML={{ __html: CSS }} />

      {/* atmosphere */}
      <div className="ys-aur a1" /><div className="ys-aur a2" /><div className="ys-aur a3" />
      <div className="ys-grain" /><div className="ys-vig" />

      {/* navigation */}
      <nav className="ys-nav">
        <button className="ys-ico" aria-label="Home" onClick={onHome}><HomeIcon /></button>
        <div className="ys-navr">
          <button className="ys-ico" aria-label="Call" onClick={onCall}><PhoneIcon /></button>
          <button className="ys-ico" aria-label="Profile" onClick={onProfile}><ProfileIcon /></button>
        </div>
      </nav>

      <main className="ys-hero">
        <h1 className="ys-title ys-up" style={{ animationDelay: ".05s" }}>{s.title}</h1>
        <p className="ys-sub ys-up" style={{ animationDelay: ".18s" }}>
          <span className="hi">{s.subtitleHi}</span>
          <span className="d" />
          <span className="en">{s.subtitleEn}</span>
        </p>

        {/* ───────────────────────────────────────────────────────────────
            SPLINE BOT — cursor-interactive 3D assistant
            Scene: https://my.spline.design/customerservice-JllV1UmWKUimJfPZUQR4Bxgh/
            The labeled stage below is sized/centered for the bot. The ambient
            orb is a graceful fallback that sits behind the embed.
            ─────────────────────────────────────────────────────────────── */}
        <div className="ys-stage ys-up" ref={stageRef} style={{ animationDelay: ".3s" }}>
          <div className="ys-halo" />
          {splineUrl ? (
            <iframe className="ys-spline" src={splineUrl} title="Yojna Sathi assistant" loading="lazy" />
          ) : (
            <div className="ys-orb" />
          )}
        </div>

        <p className="ys-greet ys-up" style={{ animationDelay: ".42s" }}>{greeting}</p>
        <h2 className="ys-cta ys-up" style={{ animationDelay: ".52s" }}>
          {c.ctaLine1}<br /><span>{c.ctaLine2}</span>
        </h2>
        <p className="ys-p ys-up" style={{ animationDelay: ".64s" }}>{c.paragraph}</p>
        <button className="ys-go ys-up" style={{ animationDelay: ".76s" }} onClick={onStart}>
          <span className="m"><MicIcon /></span>{c.ctaButton}
        </button>
      </main>
    </div>
  );
}
