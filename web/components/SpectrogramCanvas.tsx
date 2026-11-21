"use client";
import { useEffect, useRef } from "react";

export function SpectrogramCanvas({ frames, title }: { frames: Float64Array[]; title: string }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current; if (!c || frames.length === 0) return;
    const ctx = c.getContext("2d")!; const T = frames.length, M = frames[0].length;
    let lo = Infinity, hi = -Infinity;
    for (const f of frames) for (const v of f) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    const img = ctx.createImageData(c.width, c.height);
    for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) {
      const v = frames[Math.floor((x / c.width) * T)][M - 1 - Math.floor((y / c.height) * M)];
      const u = (v - lo) / (hi - lo + 1e-9), o = (y * c.width + x) * 4;
      img.data[o] = 255 * Math.min(1, 2 * u); img.data[o + 1] = 255 * Math.max(0, 2 * u - 1) * 0.9;
      img.data[o + 2] = 120 * (1 - u); img.data[o + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  }, [frames]);
  return (
    <figure style={{ margin: 0 }}>
      <figcaption style={{ fontSize: 12, opacity: 0.7 }}>{title}</figcaption>
      <canvas ref={ref} width={400} height={128} style={{ width: "100%", borderRadius: 6, background: "#111" }} aria-label={title} />
    </figure>
  );
}
