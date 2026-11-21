---
name: dsp-parity
description: Use when changing feature extraction, DSP config constants, or adding a feature that exists in both Python and TypeScript.
---
# dsp-parity

1. Edit the Python reference first (`ml/src/rubble_ear/features.py`) and add a pytest.
2. Port to `web/lib/dsp/features.ts` with identical framing, window, eps (see table in CLAUDE.md).
3. Extend `ml/scripts/make_golden.py` with the new quantity, run `make golden`.
4. Add the assertion in `web/tests/dsp.test.ts` (tolerance 1e-6, float64).
5. `make test` must be green. Then invoke the `dsp-parity-reviewer` agent.

Pitfalls: periodic (not symmetric) Hann; no centre padding; zero-pad 400->512; power not magnitude; natural log; unnormalised triangular mel.
