"use client";

interface TranscriptDisplayProps {
  transcript: string;
  languageDetected?: string | null;
}

// Shows the user exactly what the system heard (builds trust for a voice-only user).
export default function TranscriptDisplay({
  transcript,
  languageDetected,
}: TranscriptDisplayProps) {
  if (!transcript) return null;

  return (
    <div className="glass mt-7 w-full max-w-xl rounded-2xl px-6 py-5">
      <p className="mb-1.5 flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-accent/80">
        <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
        We heard {languageDetected ? `(${languageDetected})` : ""}
      </p>
      <p className="text-lg leading-relaxed text-white/90">&ldquo;{transcript}&rdquo;</p>
    </div>
  );
}
