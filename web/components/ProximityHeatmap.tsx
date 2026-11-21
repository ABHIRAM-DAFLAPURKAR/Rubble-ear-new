"use client";
import { useEffect, useRef } from "react";
import { argmaxCell, ringHeatmap, type Reading } from "@/lib/localize";

export const EXTENT_M = 6, SIZE = 60;

export function ProximityHeatmap({ readings, onPlace }: { readings: Reading[]; onPlace: (x: number, y: number) => void }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current; if (!c) return;
    const ctx = c.getContext("2d")!, px = c.width / SIZE;
    ctx.fillStyle = "#111"; ctx.fillRect(0, 0, c.width, c.height);
    if (readings.length) {
      const g = ringHeatmap(readings, SIZE, EXTENT_M), mx = Math.max(...g, 1e-9);
      for (let j = 0; j < SIZE; j++) for (let i = 0; i < SIZE; i++) {
        const u = g[j * SIZE + i] / mx;
        ctx.fillStyle = `rgba(255,${Math.floor(200 * (1 - u))},0,${u * 0.9})`;
        ctx.fillRect(i * px, j * px, px, px);
      }
      if (readings.length >= 2) {
        const b = argmaxCell(g, SIZE, EXTENT_M);
        ctx.strokeStyle = "#0f0"; ctx.lineWidth = 2; ctx.beginPath();
        ctx.arc((b.x / EXTENT_M) * c.width, (b.y / EXTENT_M) * c.height, 8, 0, 7); ctx.stroke();
      }
    }
    ctx.fillStyle = "#4af";
    for (const r of readings) { ctx.beginPath(); ctx.arc((r.x / EXTENT_M) * c.width, (r.y / EXTENT_M) * c.height, 4, 0, 7); ctx.fill(); }
  }, [readings]);
  return (
    <canvas ref={ref} width={300} height={300} aria-label="Proximity heatmap"
      style={{ width: "100%", maxWidth: 360, borderRadius: 6, touchAction: "none" }}
      onClick={(e) => { const r = e.currentTarget.getBoundingClientRect();
        onPlace(((e.clientX - r.left) / r.width) * EXTENT_M, ((e.clientY - r.top) / r.height) * EXTENT_M); }} />
  );
}
