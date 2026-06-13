"use client";

import { useRef, useState } from "react";
import { matchSchemesFromAudio, type MatchResponse } from "@/lib/api";

type PageState = "idle" | "listening" | "processing" | "results";

interface MicButtonProps {
  pageState: PageState;
  onListeningStart: () => void;
  onProcessingStart: () => void;
  onResults: (data: MatchResponse) => void;
  onError: (message: string) => void;
  onMicDenied: () => void;
}

const MAX_RECORDING_MS = 10_000; // auto-stop after 10s

export default function MicButton({
  pageState,
  onListeningStart,
  onProcessingStart,
  onResults,
  onError,
  onMicDenied,
}: MicButtonProps) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const autoStopRef = useRef<ReturnType<typeof setTimeout> | null>(null);
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

      recorder.onstop = async () => {
        stopTracks();
        const blob = new Blob(chunksRef.current, { type: mimeType || "audio/webm" });
        if (blob.size === 0) {
          onError("No audio was captured. Please try again.");
          return;
        }
        onProcessingStart();
        try {
          const data = await matchSchemesFromAudio(blob);
          onResults(data);
        } catch (err) {
          console.error("[MicButton] /match failed", err);
          // Surface the backend's real reason (api.ts throws it as err.message)
          // instead of a generic string, so failures are actually diagnosable.
          onError(
            err instanceof Error && err.message
              ? err.message
              : "Voice recognition failed. Please try again."
          );
        }
      };

      recorder.start();
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
      ? "Finding your schemes…"
      : isRecording
      ? "Listening… (tap to stop)"
      : "Speak your situation";

  return (
    <div className="flex flex-col items-center gap-3">
      <button
        onClick={handleClick}
        disabled={pageState === "processing"}
        aria-label={label}
        className={`grid h-20 w-20 place-items-center rounded-full text-3xl transition
          ${
            isRecording
              ? "animate-pulse bg-red-500 text-white"
              : "bg-accent text-black hover:brightness-110"
          }
          ${pageState === "processing" ? "cursor-not-allowed opacity-60" : ""}`}
      >
        {pageState === "processing" ? "⏳" : isRecording ? "■" : "🎤"}
      </button>
      <span className="text-sm text-white/70">{label}</span>
    </div>
  );
}
