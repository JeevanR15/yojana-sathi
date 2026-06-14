"use client";

import { useState } from "react";
import type { Scheme } from "@/lib/api";

interface SchemeCardProps {
  scheme: Scheme;
  index: number;
}

export default function SchemeCard({ scheme, index }: SchemeCardProps) {
  const [showForm, setShowForm] = useState(false);
  const pct = Math.round((scheme.match_score || 0) * 100);

  return (
    <div
      className="glass animate-slide-in w-full max-w-xl rounded-3xl p-6 transition duration-300 hover:-translate-y-0.5 hover:border-accent/30"
      style={{ animationDelay: `${index * 0.12}s` }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-accent/15 text-sm font-bold text-accent ring-1 ring-accent/30">
            {index + 1}
          </span>
          <h3 className="text-xl font-bold leading-snug text-white sm:text-2xl">
            {scheme.name}
          </h3>
        </div>
        <span className="shrink-0 rounded-full border border-accent/40 bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
          {pct}% match
        </span>
      </div>

      <p className="mt-3 text-base font-semibold text-accent sm:text-lg">
        {scheme.benefit}
      </p>

      {scheme.hindi_explanation && (
        <p className="mt-4 rounded-2xl border border-white/5 bg-black/30 px-4 py-3 text-base leading-relaxed text-white/85">
          {scheme.hindi_explanation}
        </p>
      )}

      <div className="mt-5">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-white/55">
          <span className="h-1 w-1 rounded-full bg-accent/70" /> Why you qualify
        </p>
        <p className="mt-1.5 text-sm leading-relaxed text-white/65">
          {scheme.eligibility_summary}
        </p>
      </div>

      <div className="mt-4">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-white/55">
          <span className="h-1 w-1 rounded-full bg-accent/70" /> Documents you need
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {scheme.required_docs.map((doc) => (
            <span
              key={doc}
              className="rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-white/70"
            >
              {doc}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <a
          href={scheme.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-black shadow-lg shadow-accent/20 transition hover:brightness-110"
        >
          Apply Now →
        </a>
        <button
          onClick={() => setShowForm(true)}
          className="rounded-xl border border-white/20 px-5 py-2.5 text-sm font-semibold text-white/90 transition hover:bg-white/10"
        >
          🎙️ Fill Form by Voice
        </button>
      </div>

      {/* "Coming soon" modal — the voice form-fill flow is wired on the backend
          but intentionally not connected to the UI yet (later in the hackathon). */}
      {showForm && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"
          onClick={() => setShowForm(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl border border-white/10 bg-[#111] p-6 text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-4xl">🎙️</p>
            <h4 className="mt-3 text-xl font-semibold text-white">Voice Form-Fill</h4>
            <p className="mt-2 text-sm text-white/60">
              Coming soon — answer a few questions by voice and we&rsquo;ll generate a
              filled application PDF for{" "}
              <span className="text-accent">{scheme.name}</span>.
            </p>
            <button
              onClick={() => setShowForm(false)}
              className="mt-5 rounded-xl bg-accent px-5 py-2 text-sm font-semibold text-black"
            >
              Got it
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
