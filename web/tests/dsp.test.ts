import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { AUDIO } from "../lib/dsp/config";
import { logMel, rms, zcr, resampleLinear, frameCount } from "../lib/dsp/features";

const golden = JSON.parse(readFileSync(resolve(__dirname, "../../parity/golden.json"), "utf8"));
const sig = Float64Array.from({ length: 4000 }, (_, n) => 0.5 * Math.sin((2 * Math.PI * 440 * n) / 16000) + 0.25 * Math.sin((2 * Math.PI * 1250 * n) / 16000));

describe("python/ts parity", () => {
  it("config mirrors ml/configs/default.yaml (via golden)", () => {
    for (const [k, v] of Object.entries(golden.config)) expect((AUDIO as any)[k === "n_fft" ? "nFft" : k === "n_mels" ? "nMels" : k]).toBe(v);
  });
  it("log-mel matches golden", () => {
    const lm = logMel(sig);
    expect(lm.length).toBe(golden.n_frames);
    lm.slice(0, 3).forEach((row, t) => row.forEach((v, m) => expect(Math.abs(v - golden.log_mel_first3[t][m])).toBeLessThan(1e-6)));
    const mean = lm.reduce((s, r) => s + r.reduce((a, b) => a + b, 0), 0) / (lm.length * AUDIO.nMels);
    expect(Math.abs(mean - golden.log_mel_mean)).toBeLessThan(1e-6);
  });
  it("rms and zcr match golden", () => {
    expect(Math.abs(rms(sig) - golden.rms)).toBeLessThan(1e-8);
    expect(Math.abs(zcr(sig) - golden.zcr)).toBeLessThan(1e-8);
  });
});

describe("utils", () => {
  it("frameCount", () => { expect(frameCount(399)).toBe(0); expect(frameCount(4000)).toBe(23); });
  it("resample length", () => { expect(resampleLinear(new Float32Array(48000), 48000, 16000).length).toBe(16000); });
});
