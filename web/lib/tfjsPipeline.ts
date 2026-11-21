import { HeuristicPipeline, type Pipeline, type Result } from "./pipeline";

/** STUB (Milestone M7). Loads exported TF.js graph models listed in /models/manifest.json:
 * { "denoiser": "/models/denoiser/model.json", "classifier": "...", "range": "..." }
 * Until implemented it delegates to the heuristic so the app always works. Replace `process` body
 * keeping the Pipeline contract; do NOT change UI code. */
export class TfjsPipeline implements Pipeline {
  name = "tfjs-stub";
  private fallback = new HeuristicPipeline();
  static async load(): Promise<TfjsPipeline> {
    return new TfjsPipeline();
  }
  process(x: Float32Array): Promise<Result> {
    return this.fallback.process(x);
  }
}
