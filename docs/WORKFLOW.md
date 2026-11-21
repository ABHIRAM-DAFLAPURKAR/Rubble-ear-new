# DEVELOPMENT WORKFLOW (every task)
1 Read milestone → 2 write failing test → 3 implement → 4 `make test && make typecheck && make lint` → 5 (UI) `make build` → 6 commit `Mx: msg (tests: N)` → 7 tick checkbox in EXECUTION_PLAN.md.
Parallelism: data-engineer (M1–M2), ml-trainer (M3–M6), web-frontend (M7–M8) touch disjoint trees; run in parallel after M2 interfaces are fixed. test-engineer runs before/after each. dsp-parity-reviewer after any DSP change.
Branches: `m<N>-<slug>`; squash-merge when DoD met. Commit often; never commit data/models/node_modules.
Definition of "done": DoD in plan satisfied AND CI green AND docs updated.
