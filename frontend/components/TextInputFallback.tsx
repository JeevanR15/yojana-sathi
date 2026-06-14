"use client";

interface TranscriptDisplayProps {
  transcript: string;
  languageDetected?: string | null;
}

export default function TranscriptDisplay({
  transcript,
  languageDetected,
}: TranscriptDisplayProps) {
  if (!transcript) return null;

  return (
    <div className="mt-8 w-full rounded-2xl border border-accent/20 bg-gradient-to-br from-white/8 to-white/3 p-6 backdrop-blur-md sm:p-8">
      <p className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-accent/70">
        <span>👂</span> We Heard
        {languageDetected && <span className="text-white/50">({languageDetected})</span>}
      </p>
      <p className="text-lg leading-relaxed text-white/90 sm:text-xl">
        &ldquo;{transcript}&rdquo;
      </p>
    </div>
  );
}