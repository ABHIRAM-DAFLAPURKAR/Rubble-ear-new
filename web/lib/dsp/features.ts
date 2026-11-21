import { AUDIO as A } from "./config";
import { fft } from "./fft";

export const hann = (n: number): Float64Array =>
  Float64Array.from({ length: n }, (_, i) => 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / n));
export const hzToMel = (f: number) => 2595 * Math.log10(1 + f / 700);
export const melToHz = (m: number) => 700 * (Math.pow(10, m / 2595) - 1);
export const frameCount = (n: number, win = A.win, hop = A.hop) => (n < win ? 0 : 1 + Math.floor((n - win) / hop));

export function melFilterbank(): Float64Array[] {
  const lo = hzToMel(A.fmin), hi = hzToMel(A.fmax);
  const pts = Array.from({ length: A.nMels + 2 }, (_, i) => melToHz(lo + ((hi - lo) * i) / (A.nMels + 1)));
  const bins = A.nFft / 2 + 1;
  return Array.from({ length: A.nMels }, (_, m) => {
    const [l, c, r] = [pts[m], pts[m + 1], pts[m + 2]];
    const row = new Float64Array(bins);
    for (let k = 0; k < bins; k++) {
      const f = (k * A.sr) / A.nFft;
      row[k] = Math.max(0, Math.min((f - l) / (c - l), (r - f) / (r - c)));
    }
    return row;
  });
}
const FB = melFilterbank();
const WIN = hann(A.win);

/** Eq.1 power spectrogram frames -> (frames x nFft/2+1). Mirrors Python stft_power. */
export function stftPower(x: ArrayLike<number>): Float64Array[] {
  const n = frameCount(x.length);
  const out: Float64Array[] = [];
  const re = new Float64Array(A.nFft), im = new Float64Array(A.nFft);
  for (let t = 0; t < n; t++) {
    re.fill(0); im.fill(0);
    for (let i = 0; i < A.win; i++) re[i] = x[t * A.hop + i] * WIN[i];
    fft(re, im);
    const p = new Float64Array(A.nFft / 2 + 1);
    for (let k = 0; k < p.length; k++) p[k] = re[k] * re[k] + im[k] * im[k];
    out.push(p);
  }
  return out;
}

export function melPower(x: ArrayLike<number>): Float64Array[] {
  return stftPower(x).map((p) => Float64Array.from(FB, (row) => row.reduce((s, w, k) => s + w * p[k], 0)));
}
export const logMel = (x: ArrayLike<number>): Float64Array[] =>
  melPower(x).map((f) => f.map((v) => Math.log(v + A.eps)));

export function rms(x: ArrayLike<number>): number {
  let s = 0; for (let i = 0; i < x.length; i++) s += x[i] * x[i];
  return Math.sqrt(s / x.length);
}
export function zcr(x: ArrayLike<number>): number {
  let s = 0;
  for (let i = 1; i < x.length; i++) s += Math.abs(Math.sign(x[i]) - Math.sign(x[i - 1]));
  return s / 2 / (x.length - 1);
}

/** Half-wave-rectified spectral flux of a log-mel matrix. */
export function onsetEnvelope(lm: Float64Array[]): Float64Array {
  const e = new Float64Array(lm.length);
  for (let t = 1; t < lm.length; t++) {
    let s = 0;
    for (let m = 0; m < lm[t].length; m++) s += Math.max(0, lm[t][m] - lm[t - 1][m]);
    e[t] = s;
  }
  return e;
}
/** Max normalised autocorrelation of the onset envelope over lags 0.15-1.5 s. Mirrors Python. */
export function periodicityScore(env: Float64Array, loS = 0.15, hiS = 1.5): number {
  const n = env.length;
  if (n < 4) return 0;
  const mean = env.reduce((a, b) => a + b, 0) / n;
  const e = env.map((v) => v - mean);
  const denom = e.reduce((s, v) => s + v * v, 0);
  if (denom < 1e-12) return 0;
  const fps = A.sr / A.hop;
  const lo = Math.floor(loS * fps), hi = Math.min(Math.floor(hiS * fps), n - 1);
  let best = 0;
  for (let k = lo; k <= hi; k++) {
    let s = 0; for (let i = 0; i + k < n; i++) s += e[i] * e[i + k];
    best = Math.max(best, s / denom);
  }
  return best;
}

/** Linear-interpolation resampler for browsers that ignore AudioContext({sampleRate}). */
export function resampleLinear(x: Float32Array, from: number, to: number): Float32Array {
  if (from === to) return x;
  const n = Math.floor((x.length * to) / from);
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const p = (i * from) / to, i0 = Math.floor(p), f = p - i0;
    out[i] = x[i0] * (1 - f) + (x[Math.min(i0 + 1, x.length - 1)] * f);
  }
  return out;
}
