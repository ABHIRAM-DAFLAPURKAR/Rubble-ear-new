---
name: dataset-pipeline
description: Use when adding, processing or augmenting datasets.
---
# dataset-pipeline

1. Check the licence row in docs/DATASETS.md (add one if the dataset is new).
2. Download with scripts/download_datasets.sh into data/raw/<name> (git-ignored).
3. Resample to 16 kHz mono float32 into data/processed/<name>/ and append to data/manifest.csv (`path,label,source,licence,split`).
4. Split by source recording; never random-split clips cut from the same recording.
5. Augment only through `synth.mix_at_snr` / `synth.rubble_channel` (seeded). One unit test per transform.
6. Report class counts per split.
