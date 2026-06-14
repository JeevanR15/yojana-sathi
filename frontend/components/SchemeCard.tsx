"use client";

import { useState } from "react";
import { downloadSchemePdf, type Scheme } from "@/lib/api";

interface SchemeCardProps {
  scheme: Scheme;
  index: number;
}

export default function SchemeCard({ scheme, index }: SchemeCardProps) {
  const pct = Math.round((scheme.match_score || 0) * 100);
  const [downloading, setDownloading] = useState(false);

  // Download a PDF summary for later use — the backend renders it (Indic-script aware),
  // so the Hindi/Telugu explanation shows correctly. Includes benefit, why-you-qualify,
  // the documents/certificates to carry, and the official portal link.
  const downloadScheme = async () => {
    if (downloading) return;
    setDownloading(true);
    try {
      const blob = await downloadSchemePdf(scheme);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${scheme.name.replace(/[^a-z0-9]+/gi, "_")}_yojana-saathi.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("[card] PDF download failed", err);
    } finally {
      setDownloading(false);
    }
  };

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
          <p className="mt-2 text-lg font-semibold text-accent">{scheme.benefit}</p>
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
          onClick={downloadScheme}
          disabled={downloading}
          className="flex items-center justify-center gap-2 rounded-xl border border-accent/30 bg-white/5 px-5 py-3 font-semibold text-accent transition duration-300 hover:bg-white/10 hover:border-accent/50 disabled:opacity-60 sm:py-2.5"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v12M7 10l5 5 5-5M5 21h14" /></svg>
          {downloading ? "Preparing PDF…" : "Download PDF"}
        </button>
      </div>
    </div>
  );
}
