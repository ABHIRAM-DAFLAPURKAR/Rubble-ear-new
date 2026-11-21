import { AUDIO as A } from "./dsp/config";
import { melPower, periodicityScore, rms } from "./dsp/features";

export type Label = "tap_knock" | "shout" | "rubble_settling" | "background";
export interface Result {
  rawLogMel: Float64Array[]; filteredLogMel: Float64Array[];
  label: Label; confidence: number; rangeM: number | null; periodicity: number; rms: number;
}
/** Contract every pipeline (heuristic or TF.js) must implement. UI depends ONLY on this. */
export interface Pipeline { name: string; process(audio16k: Float32Array): Promise<Result> }

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

/** Default fallback: spectral-floor subtraction + periodicity detector. Works with no trained models. */
export class HeuristicPipeline implements Pipeline {
  name = "heuristic-v0";
  /** A0 calibration: rms at 1 m through rubble. Tunable in UI. */
  constructor(public a0 = 0.02, public alpha = 0.6) {}
  async process(x: Float32Array): Promise<Result> {
    const P = melPower(x);
    const T = P.length, M = A.nMels;
    const lm = P.map((f) => f.map((v) => Math.log(v + A.eps)));
    // Noise floor = per-band median power over the window (stationary hum/engine), in the POWER domain.
    const floor = new Float64Array(M);
    for (let m = 0; m < M; m++) {
      const col = Array.from({ length: T }, (_, t) => P[t][m]).sort((a, b) => a - b);
      floor[m] = col[Math.floor(0.5 * (T - 1))] + 1e-12;
    }
    // Keep only energy > ~6 dB above the floor: log1p(max(0, P/floor - 4)). Noise-only frames stay ~0.
    const filt = P.map((f) => f.map((v, m) => Math.log1p(Math.max(0, v / floor[m] - 4))));
    const act = Float64Array.from(filt, (f) => f.reduce((a, b) => a + b, 0));
    const per = periodicityScore(act);
    const meanAct = act.reduce((a, b) => a + b, 0) / Math.max(1, T);
    const gate = clamp(meanAct / 1.0, 0, 1);          // is there ANY non-stationary energy?
    const confidence = clamp(per * gate, 0, 1);
    const level = rms(x);
    const label: Label = confidence > 0.35 ? "tap_knock" : gate > 0.3 ? "rubble_settling" : "background";
    // Invert Eq.13 (A = a0*exp(-alpha d)/d^2) numerically for d in [0.3, 3] m
    let rangeM: number | null = null;
    if (label === "tap_knock") {
      let best = 0.3, err = Infinity;
      for (let d = 0.3; d <= 3.0; d += 0.05) {
        const e = Math.abs(Math.log(this.a0 * Math.exp(-this.alpha * d) / d ** 2) - Math.log(level + 1e-9));
        if (e < err) { err = e; best = d; }
      }
      rangeM = best;
    }
    return { rawLogMel: lm, filteredLogMel: filt, label, confidence, rangeM, periodicity: per, rms: level };
  }
}

/** Loads /models/<name>/model.json via TF.js when present; otherwise caller falls back to Heuristic. */
export async function createPipeline(): Promise<Pipeline> {
  try {
    const r = await fetch("/models/manifest.json", { cache: "no-store" });
    if (r.ok) {
      const { TfjsPipeline } = await import("./tfjsPipeline");
      return await TfjsPipeline.load();
    }
  } catch { /* offline or no models: fall through */ }
  return new HeuristicPipeline();
}
