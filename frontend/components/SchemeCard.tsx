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
      className="animate-slide-in group rounded-2xl border border-accent/20 bg-gradient-to-br from-white/8 via-white/5 to-white/2 p-6 backdrop-blur-md transition-all duration-300 hover:border-accent/40 hover:shadow-xl hover:shadow-accent/10 sm:p-8"
      style={{ animationDelay: `${index * 0.12}s` }}
    >
      <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div className="flex-1">
          <h3 className="font-poppins text-xl font-bold text-white sm:text-2xl">
            {scheme.name}
          </h3>
          <p className="mt-2 text-lg font-semibold text-accent">
            {scheme.benefit}
          </p>
        </div>
        <div className="shrink-0">
          <span className="inline-flex items-center rounded-full border border-accent/40 bg-gradient-to-r from-accent/20 to-accent/10 px-4 py-2 text-sm font-bold text-accent">
            {pct}% Match
          </span>
        </div>
      </div>

      {scheme.hindi_explanation && (
        <div className="mt-5 rounded-xl border border-accent/10 bg-black/40 px-4 py-3 text-sm leading-relaxed text-white/85 sm:text-base">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-accent">
            हिंदी में
          </p>
          {scheme.hindi_explanation}
        </div>
      )}

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-accent/70">
            Why You Qualify
          </p>
          <p className="mt-2 text-sm leading-relaxed text-white/70">
            {scheme.eligibility_summary}
          </p>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-accent/70">
            Documents Needed
          </p>
          <ul className="mt-2 space-y-1">
            {scheme.required_docs.slice(0, 3).map((doc) => (
              <li key={doc} className="flex items-start gap-2 text-sm text-white/70">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                {doc}
              </li>
            ))}
            {scheme.required_docs.length > 3 && (
              <li className="text-xs text-white/50">
                +{scheme.required_docs.length - 3} more
              </li>
            )}
          </ul>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <a
          href={scheme.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 rounded-xl bg-gradient-to-r from-accent to-teal-500 px-5 py-3 text-center font-semibold text-black transition duration-300 hover:shadow-lg hover:shadow-accent/40 active:scale-95 sm:py-2.5"
        >
          Apply Now →
        </a>
        <button
          onClick={() => setShowForm(true)}
          className="rounded-xl border border-accent/30 bg-white/5 px-5 py-3 font-semibold text-accent transition duration-300 hover:bg-white/10 hover:border-accent/50 sm:py-2.5"
        >
          🎙️ Voice Form
        </button>
      </div>

      {showForm && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm"
          onClick={() => setShowForm(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl border border-accent/20 bg-gradient-to-b from-white/10 to-white/5 p-6 text-center backdrop-blur-xl sm:p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-4xl">🎙️</p>
            <p className="mt-4 font-poppins text-xl font-bold text-white">
              Coming Soon
            </p>
            <p className="mt-2 text-sm text-white/70">
              Voice-guided form filling will be available in the next update
            </p>
            <button
              onClick={() => setShowForm(false)}
              className="mt-6 rounded-lg bg-accent/20 px-4 py-2 text-sm font-semibold text-accent transition hover:bg-accent/30"
            >
              Got it
            </button>
          </div>
        </div>
      )}
    </div>
  );
}