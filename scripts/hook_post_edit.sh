#!/usr/bin/env bash
# Fast guardrail after edits: lint changed Python, warn when DSP files change without parity refresh.
set -u
cd "$(dirname "$0")/.."
ruff check ml --quiet 2>/dev/null || echo "[hook] ruff reported issues (run: make lint)"
if git diff --name-only 2>/dev/null | grep -qE 'ml/src/rubble_ear/features.py|web/lib/dsp/|ml/configs/default.yaml'; then
  echo "[hook] DSP/config touched: run 'make golden && make test' to verify py/ts parity"
fi
exit 0
