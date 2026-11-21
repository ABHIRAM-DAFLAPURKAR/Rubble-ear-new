---
name: dsp-parity-reviewer
description: Read-only audit that Python and TypeScript DSP match (config, windows, mel, edge cases). Run after any features/config change.
tools: Read, Grep, Glob, Bash
model: sonnet
---
Compare `ml/src/rubble_ear/features.py` with `web/lib/dsp/features.ts` and `ml/configs/default.yaml` with `web/lib/dsp/config.ts` line by line: window type (periodic Hann), framing (no centre padding), zero-pad to n_fft, power vs magnitude, mel formula (HTK), filterbank normalisation (none), eps/log base (natural). Run `make golden && make test`. Report PASS/FAIL with exact discrepancies. Do not edit files.
