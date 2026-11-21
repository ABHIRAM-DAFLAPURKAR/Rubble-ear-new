# CLAUDE.md — RubbleEar (read fully before any action)

Offline PWA that detects human distress taps/knocks/shouts through rubble using phone mic + accelerometer.
Stack: Next.js 14 (App Router, TS strict) PWA + Python/TensorFlow training + TF.js/ONNX-Web inference. **Everything free/open-source. No paid APIs, no servers at runtime.**

## Source of truth (do not duplicate, do not drift)
| What | Where |
|---|---|
| DSP constants | `ml/configs/default.yaml` ⇄ `web/lib/dsp/config.ts` (must match) |
| Feature math | `ml/src/rubble_ear/features.py` ⇄ `web/lib/dsp/features.ts` (golden-vector parity) |
| Plan / milestones | `docs/EXECUTION_PLAN.md` (work milestone by milestone, in order) |
| Datasets / licences | `docs/DATASETS.md` · Models: `docs/MODELS.md` · UI: `docs/UI_SPEC.md` |
| Pipeline contract (UI ↔ model) | `Pipeline` interface in `web/lib/pipeline.ts` |

## Commands (use these, nothing else)
- `make setup` · `make test` (py+web+parity) · `make test-py` · `make test-web` · `make typecheck` · `make build`
- `make golden` regenerates `parity/golden.json` (only when features math intentionally changes; commit both sides)
- `make synth-train` smoke-trains all 3 models on synthetic data (needs `pip install -r ml/requirements-train.txt`)
- `make dev` (web at :3000)

## Workflow rules (non-negotiable)
1. Start every task by reading the active milestone in `docs/EXECUTION_PLAN.md`; state its Definition of Done.
2. **Test first**: write/extend a failing test, then implement, then `make test`. Never claim done with red tests.
3. One milestone = one branch/commit series. Do not start M(n+1) until M(n) DoD is met and checked off in the plan.
4. Any change to features/config ⇒ update BOTH Python and TS, run `make golden && make test`.
5. UI talks only to `Pipeline`. Swapping heuristic → TF.js must not touch components.
6. Keep PRs small; no new dependencies without justification in the commit message and a free OSS licence.
7. Use subagents (`.claude/agents/`) for: data (`data-engineer`), training (`ml-trainer`), UI/PWA (`web-frontend`), tests (`test-engineer`), parity audits (`dsp-parity-reviewer`). Delegate in parallel when tasks touch disjoint files.

## Honesty rules (hackathon credibility)
- Targets (≈91% acc under 3 m rubble, <2 s latency) are **targets**. Never print/commit them as results. Report only measured numbers from `models/*.metrics.json` and label synthetic-only results "synthetic".
- A single phone gives **range only**. X/Y comes from multi-position ring intersection (`web/lib/localize.ts`). Do not fabricate (X,Y,Z) from one reading.
- Browser accelerometer ≈ 50–60 Hz (Chrome/Android Generic Sensor; iOS needs DeviceMotion permission via user gesture). Never assume 100 Hz.
- getUserMedia must disable echoCancellation/noiseSuppression/autoGainControl (they delete the signal we want).
- Mic/sensors require HTTPS (or localhost). Service worker only registers in production builds.
- Check dataset licences in `docs/DATASETS.md` before using any data in a shipped model (RAVDESS is non-commercial).

## Forbidden
Browser storage of raw audio; network calls at inference time; committing datasets or `node_modules`; editing `parity/golden.json` by hand; skipping tests with `.skip` to go green; changing public `Pipeline` shape without updating docs + tests.

## Style
Python: ruff (line 100), type hints, numpy-first, deterministic seeds. TS: strict, no `any` except sensor browser shims, pure functions in `lib/`, components stay thin.
