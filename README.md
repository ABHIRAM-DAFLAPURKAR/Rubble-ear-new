# RubbleEar — offline acoustic-vibrational survivor detection 

Progressive Web App that listens (mic) and feels (accelerometer) through a phone pressed to rubble, suppresses generator/excavator noise, flags rhythmic human taps/knocks/shouts, and estimates range; readings from ≥2 positions are intersected into a proximity heatmap. 100 % free/open-source, runs offline in the browser.

## Quick start
```bash
make setup          # pip deps (numpy/scipy/pytest/ruff) + npm install
make test           # 14 pytest + 8 vitest (incl. Python<->TS parity)
make dev            # http://localhost:3000  -> press "Demo (simulated)"
cd web && npm run build && npm run start   # production build: service worker + offline
# training (optional, needs TensorFlow):  pip install -r ml/requirements-train.txt && make synth-train
```
Phone testing needs HTTPS: `npx localtunnel --port 3000` or deploy `web/` to GitHub Pages/Netlify/Vercel free tier.

### Windows (PowerShell)
From the repository root, install the Python and web dependencies, then run the app:
```powershell
py -3.12 -m pip install -r ml\requirements.txt
Set-Location web
npm ci
npm run dev
```
In a second terminal, run Python tests with `Set-Location ml; py -3.12 -m pytest -q`,
and web checks with `Set-Location web; npm run test; npm run typecheck; npm run build`.

## Repo map
| Path | Purpose |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `SKILL.md` | Agent rules, master skill |
| `.claude/{agents,skills,commands,settings.json}` | 5 subagents, 5 skills, 4 slash commands, permissions + post-edit hook |
| `docs/` | EXECUTION_PLAN (M0–M9), DATASETS, MODELS (+equations), ARCHITECTURE, UI_SPEC, TESTING, WORKFLOW, PROMPTS |
| `ml/` | `rubble_ear` package: features, synth, data, models, train · configs · 14 tests |
| `parity/golden.json` | Python→TS numeric contract for DSP |
| `web/` | Next.js 14 PWA prototype: dashboard, heuristic pipeline, heatmap, SW, vitest |
| `scripts/` | dataset downloader, icon generator, hook |

## Status
M0 complete (scaffold; all tests/build green). Next: M1 (see `docs/EXECUTION_PLAN.md`). Start with the **Kickoff** prompt in `docs/PROMPTS.md`.

## Measured results
_None yet._ The pitch targets (≈91 % accuracy at ≤3 m rubble, <2 s latency) are goals; this table is filled only from `models/*.metrics.json` and device measurements.

## Corrections to the earlier pitch document (the repo follows these)
1. Accelerometer in browsers is ~50–60 Hz, not 100 Hz (iOS needs DeviceMotion permission).
2. One phone yields **range**, not an (X,Y,Z) vector; position comes from multi-point ring intersection.
3. RNNoise weights cannot initialise the CRNN GRU; RNNoise is used as a comparison baseline.
4. YAMNet hops at 0.48 s, so rhythm is modelled by the MFCC-TCN branch; YAMNet supplies semantic embeddings.
5. Attenuation (Eq.13) is in `docs/MODELS.md` §4 (the pitch doc's "Section 5.4" reference was wrong); α is an assumption until field-calibrated.
6. AudioSet audio is YouTube-hosted and not redistributable: we use YAMNet weights and FSD50K/ESC-50 clips instead. Several datasets are non-commercial (see DATASETS.md).
7. Disable browser AGC/noise-suppression/echo-cancel on the mic stream.

## Licence
MIT (code). Datasets/models keep their own licences.
