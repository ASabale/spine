# Publish pipeline: tag to PyPI

Type: task
Status: open
Blocked by: 31-ci-matrix-three-os-three-python.md
Owner:
Claimed-at:

## Question

Publish is a manual upload today. Adopt tag→publish: a `vX.Y.Z` tag triggers a
workflow that runs the release gate, builds, and publishes to PyPI via trusted
publishing (no long-lived token in the repo). Prerequisite (owner, manual):
PyPI trusted publishing configured for the repo.

Gates: 31

Resolved = a tag publishes to PyPI without a manual step or a repo secret.

- [ ] `vX.Y.Z` tag triggers the workflow: gate → build → publish
- [ ] Trusted publishing (no long-lived token in the repo)
- [ ] A test tag publishes to Test PyPI, or the first run is documented
- [ ] Publish gated on matrix green
