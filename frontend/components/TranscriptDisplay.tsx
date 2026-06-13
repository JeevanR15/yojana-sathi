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
    <div className="mt-6 w-full max-w-xl rounded-2xl border border-white/10 bg-white/5 px-5 py-4">
      <p className="mb-1 text-xs uppercase tracking-widest text-accent/80">
        We heard {languageDetected ? `(${languageDetected})` : ""}
      </p>
      <p className="text-lg leading-relaxed text-white/90">&ldquo;{transcript}&rdquo;</p>
    </div>
  );
}
