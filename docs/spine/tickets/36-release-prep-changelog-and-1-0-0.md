# Release prep: changelog and 1.0.0

Type: task
Status: open
Blocked by: 31-ci-matrix-three-os-three-python.md
Owner:
Claimed-at:

## Question

Prepare the release: changelog Unreleased becomes the 1.0.0 entry (trust chain
+ engineering + docs), version bumps to 1.0.0, coverage floor raises 70→85 and
is green, full release gate passes.

Gates: 26, 31, 33, 35

Resolved = 1.0.0 changelog written, version bumped, coverage 85 green,
`make release` fully green.

- [ ] CHANGELOG: 1.0.0 entry lists trust chain, engineering, docs; Unreleased reset
- [ ] Version 1.0.0 in pyproject; `spine --version` reports it
- [ ] Coverage floor raised 70→85 and green
- [ ] `make release` fully green
