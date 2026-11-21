import { describe, expect, it } from "vitest";
import { demoSeconds } from "../lib/demo";
import { HeuristicPipeline } from "../lib/pipeline";

describe("HeuristicPipeline", () => {
  it("detects rhythmic taps over generator hum", async () => {
    const r = await new HeuristicPipeline().process(demoSeconds(0, 2, 16000, { taps: true, depthM: 1 }));
    expect(r.label).toBe("tap_knock");
    expect(r.confidence).toBeGreaterThan(0.35);
    expect(r.rangeM).not.toBeNull();
  });
  it("does not flag machinery alone", async () => {
    const r = await new HeuristicPipeline().process(demoSeconds(0, 2, 16000, { taps: false, depthM: 1 }));
    expect(r.label).not.toBe("tap_knock");
  });
});
