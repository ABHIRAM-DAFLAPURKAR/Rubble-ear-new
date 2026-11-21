---
name: model-training
description: Use for training, evaluating and exporting models.
---
# model-training

1. Smoke first: `python -m rubble_ear.train <phase> --smoke`.
2. Full runs follow the phase order in docs/MODELS.md (denoiser -> classifier stage A -> stage B fine-tune -> range).
3. Evaluate on held-out recordings; write metrics JSON (accuracy, per-class recall, macro-F1, SDR for denoiser, MAE in metres for range).
4. Export: `tensorflowjs_converter --input_format=keras --quantize_float16 models/X.keras web/public/models/X`, then update web/public/models/manifest.json.
5. Never state unmeasured numbers. Label results synthetic vs real.
