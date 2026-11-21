# DATASETS (all free; verify licence before shipping a model trained on it)

| Dataset | Use | Licence / access | Notes |
|---|---|---|---|
| ESC-50 | env. noise + knock/click negatives | CC BY-NC (clips from Freesound, see per-clip CC) | `git clone` works; 2,000×5 s |
| FSD50K | Knock/Tap/Bang/Thump/Speech/Shout positives & negatives | CC (per-clip: CC0/BY/BY-NC/Sampling+) — **filter by licence** | ~24 GB; use ground-truth CSV to pull only needed classes |
| UrbanSound8K | drilling, jackhammer, engine idling | CC BY-NC 3.0 | 8,732 clips, 10 folds → **use official folds as splits** |
| MIMII | pumps/fans/valves machinery noise | CC BY-SA 4.0 | use 6 dB/0 dB subsets |
| AudioSet | pretraining origin of YAMNet/VGGish | annotations CC BY 4.0; audio = YouTube clips (not redistributable) | **Do not scrape.** We use YAMNet *weights* only |
| RAVDESS | distress-like vocalisation | CC BY-NC-SA 4.0 | acted emotion, not real distress; non-commercial only |
| Speech Commands | human voice negatives | CC BY 4.0 | |
| STEAD | structural/seismic vibration shape priors | CC BY 4.0 | waveforms are 100 Hz seismometer data — resample to 50 Hz for IMU realism; subset only |
| UCI HAR | phone-IMU noise floor | CC BY 4.0 | |
| Synthetic (ours) | everything, CI-safe | MIT | `synth.py`; Eq.13 attenuation + low-pass damping |

## Honest caveats (state them in the pitch)
- **No public dataset of taps heard through rubble on a phone exists.** Real-mix + synthetic + a small self-recorded field set (M5/M9) is the plan; label results accordingly.
- Non-commercial licences (ESC-50 BY-NC, UrbanSound8K, RAVDESS) are fine for a hackathon prototype but restrict commercial deployment; prefer CC0/BY FSD50K clips, MIMII and synthetic for a shippable model.
- Split by **recording/fold**, never by clip (leakage inflates accuracy).

## Class mapping (4 classes)
`tap_knock` ← FSD50K Knock/Tap/Thump(rhythmic mixes), ESC-50 door_wood_knock · `shout` ← FSD50K Shout/Yell, RAVDESS (calm/neutral excluded; fearful/angry) · `rubble_settling` ← FSD50K Crack/Crumble/Rattle/Rock-like + synthetic · `background` ← UrbanSound8K/MIMII/ESC-50 engine/wind/chainsaw.

## Layout
`data/raw/<name>/` (git-ignored) → `data/processed/<name>/*.wav` (16 kHz mono) → `data/manifest.csv`.

## Local inventory

| Dataset | Files ingested | Status |
|---|---:|---|
| ESC-50 | 0 | Dataset not present locally |
| FSD50K | 0 | Dataset not present locally |
| UrbanSound8K | 0 | Dataset not present locally |
| MIMII | 0 | Dataset not present locally |

Counts describe this checkout, not the upstream dataset releases. Update them only after
ingestion; do not estimate them from upstream catalog sizes.

The Python ingestion helpers are in `ml/src/rubble_ear/manifest.py`. They accept the
datasets' metadata CSVs (and MIMII's WAV directory), map known labels to the four project
classes, retain ESC-50/UrbanSound8K official folds, require FSD50K per-clip licence values,
and group MIMII clips by machine. `build_manifest` writes the normalized CSV, assigning
recording-level splits only where an official split is absent. `load_audio16k` returns
mono float32 audio resampled to 16 kHz.
