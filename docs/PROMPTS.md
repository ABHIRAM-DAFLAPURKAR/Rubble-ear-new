# COPY-PASTE PROMPTS (paste into Claude Code at repo root)

## Kickoff
Read CLAUDE.md and docs/EXECUTION_PLAN.md. Run `make setup && make test`. Report status, then execute the first unchecked milestone using the testing-loop skill. Do not deviate from docs/MODELS.md or docs/UI_SPEC.md. Ask before adding dependencies.

## M1/M2 data
Use the data-engineer subagent. Implement ml/src/rubble_ear/manifest.py and mixtures.py per docs/EXECUTION_PLAN.md M1–M2 with tests using tiny generated WAV fixtures. No downloads in tests. Split by recording. Finish with `make test-py`.

## M3–M6 training
Use the ml-trainer subagent. For phase <denoiser|classifier|range>: run --smoke, then train on the mixture generator per docs/MODELS.md, evaluate on held-out recordings, write models/<phase>.metrics.json, and report measured numbers labelled synthetic or real. Never invent metrics. Then export per MODELS §5 and update web/public/models/manifest.json.

## M7 in-browser inference
Use the web-frontend subagent. Replace the TfjsPipeline stub in web/lib/tfjsPipeline.ts so process() runs denoiser→classifier→range from /models/manifest.json inside a Web Worker (backend order webgl→wasm→cpu), computing features with lib/dsp. Keep the Pipeline interface unchanged, keep HeuristicPipeline as fallback, add vitest model-parity test, measure latency.

## UI / PWA (any time)
Use the web-frontend subagent and docs/UI_SPEC.md. Add <feature>. Constraints: UI depends only on Pipeline; mic constraints AGC/NS/EC off; must work offline; bump sw.js VERSION; run make typecheck test-web build; verify offline reload in production build and report the result.

## Parity audit
Use the dsp-parity-reviewer subagent, then run `make golden && make test`.

## Pitch prep (M9)
Read README "Measured results" and docs/TESTING.md field protocol. Produce docs/PITCH_SCRIPT.md: 3-minute demo script, architecture figure (mermaid), limitations slide, and only measured numbers.
