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
      className="animate-slide-in w-full max-w-xl rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.07] to-white/[0.02] p-6"
      style={{ animationDelay: `${index * 0.12}s` }}
    >
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-2xl font-semibold text-white">{scheme.name}</h3>
        <span className="shrink-0 rounded-full border border-accent/40 bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
          {pct}% match
        </span>
      </div>

      <p className="mt-2 text-lg font-medium text-accent">{scheme.benefit}</p>

      {scheme.hindi_explanation && (
        <p className="mt-3 rounded-xl bg-black/30 px-4 py-3 text-base leading-relaxed text-white/85">
          {scheme.hindi_explanation}
        </p>
      )}

      <div className="mt-4">
        <p className="text-sm font-semibold text-white/70">Why you qualify</p>
        <p className="mt-1 text-sm leading-relaxed text-white/60">
          {scheme.eligibility_summary}
        </p>
      </div>

      <div className="mt-4">
        <p className="text-sm font-semibold text-white/70">Documents you need</p>
        <ul className="mt-1 list-inside list-disc space-y-0.5 text-sm text-white/60">
          {scheme.required_docs.map((doc) => (
            <li key={doc}>{doc}</li>
          ))}
        </ul>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <a
          href={scheme.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-black transition hover:brightness-110"
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
