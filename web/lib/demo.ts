/** Browser-side synthetic source so the demo works with no mic (judges, CI, desktop). */
export function demoSeconds(startS: number, seconds: number, sr: number, opts: { taps: boolean; depthM: number }): Float32Array {
  const n = Math.floor(seconds * sr), x = new Float32Array(n);
  let seed = 12345 + Math.floor(startS * 1000);
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;
  const gain = Math.exp(-0.6 * opts.depthM) / Math.max(opts.depthM, 0.3) ** 2 * 0.25;
  for (let i = 0; i < n; i++) {
    const t = startS + i / sr;
    let v = 0.04 * rnd();
    for (let k = 1; k <= 8; k++) v += (0.12 / k) * Math.sin(2 * Math.PI * 60 * k * t);
    if (opts.taps) {
      const ph = t % 0.6; // 100 BPM tapping
      if (ph < 0.08) v += gain * Math.sin(2 * Math.PI * 900 * ph) * Math.exp(-60 * ph);
    }
    x[i] = v;
  }
  return x;
}
