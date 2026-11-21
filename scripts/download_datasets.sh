#!/usr/bin/env bash
# Usage: scripts/download_datasets.sh [esc50|fsd50k|urbansound8k|mimii|stead|ucihar|all]
# Only free/open sources. Large sets: pass a name explicitly. Check licences in docs/DATASETS.md first.
set -euo pipefail
cd "$(dirname "$0")/.."; RAW=data/raw; mkdir -p "$RAW"
get() { echo ">> $1"; case "$1" in
  esc50)  [ -d $RAW/ESC-50 ] || git clone --depth 1 https://github.com/karolpiczak/ESC-50 $RAW/ESC-50 ;;
  fsd50k) echo "FSD50K (~24 GB): download dev/eval zips + ground truth from https://zenodo.org/record/4060432 into $RAW/FSD50K (use zenodo_get or browser)";;
  urbansound8k) echo "UrbanSound8K: request/download from https://urbansounddataset.weebly.com/urbansound8k.html into $RAW/UrbanSound8K (or mirror via https://zenodo.org/record/1203745)";;
  mimii)  echo "MIMII: https://zenodo.org/record/3384388 -> $RAW/MIMII (use only 6 dB / 0 dB noise subsets first)";;
  stead)  [ -d $RAW/STEAD ] || git clone --depth 1 https://github.com/smousavi05/STEAD $RAW/STEAD; echo "STEAD waveforms hosted separately: follow its README (subset only)";;
  ucihar) mkdir -p $RAW/UCI_HAR && curl -L -o $RAW/UCI_HAR.zip "https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip" && unzip -oq $RAW/UCI_HAR.zip -d $RAW/UCI_HAR ;;
  *) echo "unknown: $1"; exit 1;; esac; }
if [ "${1:-all}" = all ]; then for d in esc50 ucihar stead; do get $d; done; echo "Large sets (fsd50k, urbansound8k, mimii) must be requested by name."; else get "$1"; fi
