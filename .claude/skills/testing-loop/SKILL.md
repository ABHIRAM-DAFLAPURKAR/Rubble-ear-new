---
name: testing-loop
description: Use at the start and end of every task.
---
# testing-loop

1. Write a failing test (pytest in ml/tests or vitest in web/tests).
2. Implement the minimum to pass.
3. `make test`, `make typecheck`, `ruff check ml`.
4. For UI changes also `make build`.
5. Commit as `<milestone>: <what> (tests: N passing)`.
