"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

// Spline touches browser-only APIs, so load it client-side only (ssr: false).
// Cast to our own prop type so we don't depend on Spline's exact prop typings.
type SplineProps = {
  scene: string;
  onLoad?: () => void;
  onError?: () => void;
  className?: string;
};
const Spline = dynamic(() => import("@splinetool/react-spline"), {
  ssr: false,
}) as unknown as React.ComponentType<SplineProps>;

// Placeholder public scene from the spec. If it fails, the CSS orb takes over.
const SPLINE_SCENE = "https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode";

export type OrbState = "idle" | "listening" | "processing" | "results";

interface VoiceOrbProps {
  state: OrbState;
}

export default function VoiceOrb({ state }: VoiceOrbProps) {
  const [useFallback, setUseFallback] = useState(false);
  const [loaded, setLoaded] = useState(false);

  // If Spline hasn't loaded within 6s (unreliable wifi), drop to the CSS orb.
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!loaded) setUseFallback(true);
    }, 6000);
    return () => clearTimeout(timer);
  }, [loaded]);

  return (
    <div className="relative grid h-[300px] w-[300px] place-items-center">
      {!useFallback && (
        <div className={`spline-wrap spline-wrap--${state} absolute inset-0`}>
          <Spline
            scene={SPLINE_SCENE}
            onLoad={() => setLoaded(true)}
            onError={() => setUseFallback(true)}
          />
        </div>
      )}

      {/* CSS orb shows while Spline loads, and stays forever if Spline fails. */}
      {(useFallback || !loaded) && (
        <div className={`css-orb css-orb--${state}`} aria-hidden>
          <div className="css-orb__ring" />
          <div className="css-orb__core" />
        </div>
      )}
    </div>
  );
}
