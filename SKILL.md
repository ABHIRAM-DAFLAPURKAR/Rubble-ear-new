---
name: rubble-ear
description: Master skill for the RubbleEar repo. Use for any work on the offline survivor-detection PWA, its DSP, datasets, models or tests.
---
# RubbleEar master skill
Read `CLAUDE.md`, then `docs/EXECUTION_PLAN.md`. Pick the task-specific skill:
- Features/config change → `.claude/skills/dsp-parity`
- Data work → `.claude/skills/dataset-pipeline`
- Training/export → `.claude/skills/model-training`
- PWA/offline/sensors → `.claude/skills/pwa-build`
- Every task → `.claude/skills/testing-loop`
Pipeline: sensors → log-mel (16 kHz, 25/10 ms, 64 mels) → denoise (CRNN mask) → classify (1D-CNN+TCN ⊕ YAMNet) → range (MLP, Eq.13) → ring-intersection heatmap.
