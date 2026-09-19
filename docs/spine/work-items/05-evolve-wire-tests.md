# Evolve and wire tests

Type: work-item
Profile: software
Status: done
Owner: ASabale
Claimed-at: 2026-09-19T06:47:22.842542+00:00
Links: 
Deliverable: src/spine/evolve.py

## Intent

Add `tests/test_evolve.py`: `set_pack` rewrites `default_pack`; `evolve` refresh writes binder without requiring npx (mock shutil.which None). Do not edit `tests/test_spine.py`. Do not run `npx skills add`.