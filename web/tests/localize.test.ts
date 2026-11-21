import { describe, expect, it } from "vitest";
import { argmaxCell, ringHeatmap } from "../lib/localize";

describe("ringHeatmap", () => {
  it("intersects rings at the true source", () => {
    const src = { x: 3, y: 2 };
    const pts = [{ x: 1, y: 5 }, { x: 5, y: 5 }, { x: 0.5, y: 1 }];
    const rs = pts.map((p) => ({ ...p, d: Math.hypot(p.x - src.x, p.y - src.y) }));
    const g = ringHeatmap(rs, 60, 6);
    const b = argmaxCell(g, 60, 6);
    expect(Math.hypot(b.x - src.x, b.y - src.y)).toBeLessThan(0.3);
  });
});
