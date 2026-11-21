/** Honest localisation: one phone gives RANGE only. X/Y come from ring-intersection of readings taken
 * at several user-marked positions (multilateration heatmap). Units: metres. */
export interface Reading { x: number; y: number; d: number; w?: number }

export function ringHeatmap(readings: Reading[], size: number, extent: number, sigma = 0.35): Float64Array {
  const g = new Float64Array(size * size);
  for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) {
    const px = ((i + 0.5) / size) * extent, py = ((j + 0.5) / size) * extent;
    let s = 0;
    for (const r of readings) {
      const dist = Math.hypot(px - r.x, py - r.y);
      s += (r.w ?? 1) * Math.exp(-((dist - r.d) ** 2) / (2 * sigma * sigma));
    }
    g[j * size + i] = s;
  }
  return g;
}
export function argmaxCell(g: Float64Array, size: number, extent: number) {
  let b = 0; for (let k = 1; k < g.length; k++) if (g[k] > g[b]) b = k;
  return { x: ((b % size) + 0.5) / size * extent, y: (Math.floor(b / size) + 0.5) / size * extent };
}
