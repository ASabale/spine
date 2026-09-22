# CI matrix: 3 OS × 3 Python

Type: task
Status: open
Blocked by: 30-zero-pyright-errors.md
Owner:
Claimed-at:

## Question

CI is a single ubuntu job. The OS-agnostic claim is currently asserted, not
verified. Run the release gate across the matrix: ubuntu/macos/windows ×
Python 3.11/3.12/3.13.

Gates: 30

Resolved = all nine legs run `make release` green; a failure blocks merge.

- [ ] Matrix: 3 OS × 3 Python, each running the full release gate
- [ ] All legs green on the current tree
- [ ] A failing leg blocks merge
- [ ] Windows failures (if any) diagnosed and fixed, not skipped
