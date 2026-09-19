# Evolve and wire tests

Type: work-item
Profile: software
Status: done
Owner: 
Claimed-at: 
Links: 
Deliverable: src/spine/evolve.py

## Intent

Add `tests/test_evolve.py`: `set_pack` rewrites `default_pack`; `evolve` refresh writes binder without requiring npx (mock shutil.which None). Do not edit `tests/test_spine.py`. Do not run `npx skills add`.