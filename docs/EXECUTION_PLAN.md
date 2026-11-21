# EXECUTION PLAN (agent: work strictly top-down; tick a box only when its DoD is verified by `make test`)

Legend: 🤖 = agent-executable now · 👤 = needs human (device, large download, recording)

## M0 — Scaffold ✅
- [x] Python DSP reference + synthetic generator + 14 pytest · TS DSP port + parity golden + heuristic pipeline + localize + 8 vitest · Next.js PWA prototype builds · CI · agents/skills.
DoD: `make test && make typecheck && make build` green.

## M1 — Real data ingest 🤖(+👤 downloads)
- [ ] `ml/src/rubble_ear/manifest.py`: build/read `data/manifest.csv` (`path,label,source,licence,split`); split by recording id.
- [ ] Loaders: ESC-50 (classes: door_wood_knock, keyboard/mouse click, footsteps, wind, engine, chainsaw…), FSD50K (Knock, Tap, Bang, Thump, Speech/Shout subset), UrbanSound8K (drilling, jackhammer, engine_idling, generator-like), MIMII.
- [ ] Resample → 16 kHz mono float32 (`soundfile`+`scipy.signal.resample_poly`).
DoD: tests with tiny fixture WAVs (generated in test) prove resample length, label mapping, no train/val leakage; `docs/DATASETS.md` counts table filled.

## M2 — Mixture builder 🤖
- [ ] `mixtures.py`: real tap/knock/shout clip → `rubble_channel(depth, alpha)` → `mix_at_snr` with real machinery noise; emits (noisy, clean, label, depth, snr). Seeded, deterministic, on-the-fly generator for Keras.
- [ ] Hard negatives: settling impulses, single knocks (non-rhythmic), speech.
DoD: tests for SNR exactness (±0.01 dB), reproducibility with same seed, label balance.

## M3 — Denoiser (Phase 1) 🤖
- [ ] Train CRNN (docs/MODELS.md §1) on mixtures; baseline = spectral-floor heuristic (TS) and RNNoise (offline comparison only).
- [ ] Metric: SI-SDR improvement on held-out recordings.
DoD: `models/denoiser.metrics.json` with measured SI-SDRi (synthetic and real-mix reported separately); beats heuristic baseline or documented why not.

## M4 — Classifier (Phases 2–3) 🤖
- [ ] Stage A: fusion classifier with frozen YAMNet embedding; Stage B: unfreeze top layers (lr 1e-5) — see MODELS §2–3.
- [ ] Metrics: accuracy, per-class recall (tap_knock recall is the headline), macro-F1, confusion matrix, accuracy vs SNR and depth buckets.
DoD: metrics JSON + confusion matrix PNG in `models/`; results table pasted into README "Measured results" (only measured values).

## M5 — Range regressor (Phase 4) 🤖/👤
- [ ] Train MLP on synthetic+real-mix; **calibrate `a0`, `alpha` with a 👤 field test** (tap on concrete at 0.5/1/2/3 m of a slab/pipe; record with phone) — procedure in docs/TESTING.md §Field.
DoD: MAE (m) reported on held-out; calibration constants committed in `ml/configs/default.yaml` and `web/lib/pipeline.ts` defaults.

## M6 — Export 🤖
- [ ] Convert to TF.js graph models (float16) into `web/public/models/{denoiser,classifier,range}/`; write `manifest.json`; total size < 10 MB.
- [ ] Numeric check: TF.js output vs Keras within 1e-3 on 5 fixed inputs (node script `web/tests/model-parity.test.ts`, skipped automatically if models absent).
DoD: bundle size printed in CI; parity test green.

## M7 — In-browser inference 🤖
- [ ] Implement `TfjsPipeline.process` (replace stub) keeping the `Pipeline` contract; TS MFCC port (+golden); run inference in a Web Worker (`web/lib/worker.ts`); WASM/WebGL backend fallback order: webgl → wasm → cpu.
- [ ] Fuse accelerometer band-energy as an extra feature channel (50 Hz, 1 s windows).
DoD: end-to-end latency measured (mid-range phone, Chrome Android) < 2 s per decision window, logged in README; heuristic remains fallback when models absent.

## M8 — UI/PWA polish 🤖
- [ ] Three.js 3D depth view (optional toggle), WebGL spectrogram, EN/HI i18n, large-button "field mode", dark/high-contrast, wake-lock, install prompt, Lighthouse PWA ≥ 90.
DoD: Lighthouse report committed; offline reload test passes (docs/TESTING.md §PWA).

## M9 — Validation & pitch 👤
- [ ] Field validation protocol run; confusion/latency numbers into README; 3-min demo script; one-page architecture figure; honest limitations slide.
