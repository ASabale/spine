# Doctor rollups

Type: work-item
Profile: software
Status: done
Owner: ASabale
Claimed-at: 2026-09-19T06:47:22.304816+00:00
Links: 
Deliverable: src/spine/doctor.py

## Intent

Doctor auto-fix includes rollups the CLI owns: if `Blocked by: NN` points at a missing ticket, report BROKEN blocker; if apply, clear the field when the number does not exist. Do not rewrite content sections. Tests in `tests/test_doctor_rollup.py` only. Do not edit `tests/test_spine.py`.