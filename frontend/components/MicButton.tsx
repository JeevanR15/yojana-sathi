"use client";

import { useRef, useState } from "react";

type PageState = "idle" | "listening" | "processing" | "results";

interface MicButtonProps {
  pageState: PageState;
  // Label shown under the mic when idle (e.g. "Speak your situation" vs "Tap to answer").
  idleLabel?: string;
  onListeningStart: () => void;
  onProcessingStart: () => void;
  // Hand the recorded audio to the page, which drives the conversation (/converse).
  onAudioReady: (audio: Blob) => void;
  onError: (message: string) => void;
  onMicDenied: () => void;
}

const MAX_RECORDING_MS = 10_000; // auto-stop after 10s
const MIN_RECORDING_MS = 1_200; // ignore taps shorter than this (no real speech)
const MIN_BLOB_BYTES = 8_000; // a silent webm is ~6KB of header; real speech is much larger

export default function MicButton({
  pageState,
  idleLabel = "Speak your situation",
  onListeningStart,
  onProcessingStart,
  onAudioReady,
  onError,
  onMicDenied,
}: MicButtonProps) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const autoStopRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startTimeRef = useRef<number>(0);
  const [isRecording, setIsRecording] = useState(false);

  // Pick the first MediaRecorder mime type the browser actually supports.
  const pickMimeType = (): string => {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
    ];
    for (const c of candidates) {
      if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(c)) {
        return c;
      }
    }
    return "";
  };

  const stopTracks = () => {
    recorderRef.current?.stream.getTracks().forEach((t) => t.stop());
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = pickMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        stopTracks();
        const elapsed = Date.now() - startTimeRef.current;
        const blob = new Blob(chunksRef.current, { type: mimeType || "audio/webm" });
        // Reject clips that are too short or too small to contain real speech —
        // this avoids a wasted Sarvam call and the confusing "could not hear" error.
        if (blob.size < MIN_BLOB_BYTES || elapsed < MIN_RECORDING_MS) {
          console.warn("[MicButton] clip too short", { bytes: blob.size, ms: elapsed });
          onError(
            "मैंने सुना नहीं — माइक दबाएँ, 2–3 सेकंड बोलें, फिर दबाएँ।\n" +
              "I didn't catch that — tap the mic, speak for 2–3 seconds, then tap again."
          );
          return;
        }
        onProcessingStart();
        // Hand the audio to the page; it calls /converse with the conversation state.
        onAudioReady(blob);
      };

      // timeslice=250ms → data is flushed periodically, not only at stop, so we never
      // lose audio if something interrupts mid-recording.
      recorder.start(250);
      startTimeRef.current = Date.now();
      setIsRecording(true);
      onListeningStart();

      autoStopRef.current = setTimeout(stopRecording, MAX_RECORDING_MS);
    } catch (err) {
      // getUserMedia rejects when the user denies the mic permission.
      console.error("[MicButton] getUserMedia denied/failed", err);
      onMicDenied();
    }
  };

  const stopRecording = () => {
    if (autoStopRef.current) clearTimeout(autoStopRef.current);
    autoStopRef.current = null;
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const handleClick = () => {
    if (pageState === "processing") return; // ignore taps mid-pipeline
    if (isRecording) stopRecording();
    else startRecording();
  };

  const label =
    pageState === "processing"
      ? "Thinking…"
      : isRecording
      ? "Listening… (tap to stop)"
      : idleLabel;

  return (
    <div className="flex flex-col items-center gap-3">
      <button
        onClick={handleClick}
        disabled={pageState === "processing"}
        aria-label={label}
        className={`grid h-20 w-20 place-items-center rounded-full text-3xl transition duration-300
          ${
            isRecording
              ? "animate-pulse bg-red-500 text-white shadow-lg shadow-red-500/40"
              : "bg-accent text-black shadow-xl shadow-accent/30 hover:scale-105 hover:brightness-110"
          }
          ${pageState === "processing" ? "cursor-not-allowed opacity-60" : ""}`}
      >
        {pageState === "processing" ? "⏳" : isRecording ? "■" : "🎤"}
      </button>
      <span className="text-sm text-white/70">{label}</span>
    </div>
  );
}
