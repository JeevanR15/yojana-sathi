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

const MAX_RECORDING_MS = 10_000;

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
      console.error("[MicButton] getUserMedia denied/failed", err);
      onMicDenied();
    }
  };

  const stopRecording = () => {
    if (autoStopRef.current) clearTimeout(autoStopRef.current);
    autoStopRef.current = null;
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleButtonClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const isActive = pageState === "listening" || pageState === "processing";
  const isDisabled = pageState === "processing";

  return (
    <div className="flex flex-col items-center gap-6">
      <button
        onClick={handleButtonClick}
        disabled={isDisabled}
        className={`group relative h-24 w-24 rounded-full font-semibold text-white transition-all duration-300 sm:h-28 sm:w-28 ${
          isActive
            ? "bg-gradient-to-br from-red-500 to-red-600 shadow-lg shadow-red-500/50"
            : "bg-gradient-to-br from-accent to-teal-500 shadow-lg shadow-accent/50 hover:shadow-xl hover:shadow-accent/70"
        } ${isDisabled ? "cursor-not-allowed opacity-75" : "cursor-pointer hover:scale-105"}`}
      >
        <span className="text-3xl sm:text-4xl">
          {isRecording ? "⏹️" : "🎙️"}
        </span>
      </button>

      <div className="text-center">
        <p className="text-sm font-medium text-white">
          {pageState === "listening"
            ? "Listening... Tap to stop"
            : pageState === "processing"
              ? "Processing your request..."
              : pageState === "results"
                ? "Done! See your results below"
                : "Tap to speak"}
        </p>
        <p className="mt-1 text-xs text-white/50">
          {pageState === "idle" && "Or scroll down for text input"}
        </p>
      </div>
    </div>
  );
}