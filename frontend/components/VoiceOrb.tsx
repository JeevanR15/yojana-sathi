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

// The bundled Spline scene is just a placeholder cube with axis lines (looks broken),
// so we render our polished CSS orb instead. Flip this to true once a real, branded
// Spline scene is available — all the loading/fallback logic below still works.
const USE_SPLINE = false;

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
    <div className="relative grid h-[280px] w-[280px] place-items-center">
      {USE_SPLINE && !useFallback && (
        <div className={`spline-wrap spline-wrap--${state} absolute inset-0`}>
          <Spline
            scene={SPLINE_SCENE}
            onLoad={() => setLoaded(true)}
            onError={() => setUseFallback(true)}
          />
        </div>
      )}

      {/* CSS orb: the default visual, and also the fallback while/if Spline fails. */}
      {(!USE_SPLINE || useFallback || !loaded) && (
        <div className={`css-orb css-orb--${state}`} aria-hidden>
          <div className="css-orb__ring" />
          <div className="css-orb__core" />
        </div>
      )}
    </div>
  );
}
