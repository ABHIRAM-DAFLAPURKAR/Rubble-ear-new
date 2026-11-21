# TESTING
Pyramid: unit (pytest, vitest) → parity (golden) → model smoke → PWA/offline manual → field.
Run: `make test` (py+web) · `make typecheck` · `make lint` · `make build` · `make synth-train` (needs TF).
Rules: test first; numeric tolerance explicit (DSP 1e-6, models 1e-3); seeds fixed; no `.skip` to pass (model tests auto-skip only when TF/models are absent).
Required unit coverage per module: features (shape, finite, sine peak, edge short input), synth (SNR exact, attenuation monotonic, determinism), models (shapes), pipeline (taps→tap_knock, machinery→background), localize (3 rings recover source <0.3 m).
Add as you go (M3+): denoiser SI-SDR sanity (identity mask ⇒ 0 dB gain), classifier overfits 8 samples, range monotonic with depth, TF.js-vs-Keras parity, accuracy-vs-SNR table.
## PWA / offline checklist (manual, M8)
build+start → DevTools Application: manifest ok, SW activated → Offline → hard reload → Demo runs → Lighthouse PWA ≥ 90.
## Field protocol (👤, M5/M9)
Concrete slab or pipe, phone pressed on surface, generator/speaker noise playing at 3 levels; tap rhythm 100 BPM at 0.5/1/2/3 m; 10 trials each; record WAV + phone IMU; log ground-truth distance; report accuracy, recall, MAE, latency per condition.
