# Binder concern table

Type: grilling
Status: resolved

## Question

Which concerns ship as binder skills in v1? Each concern is one thin skill that routes to craft (or to a CLI verb). Do not vendor grilling/tdd/wayfinder bodies.

Must include routing into Wayfinder (planning fog), work-item execution, doctor, and the software profile’s build/eval/review as pointers — the software gates themselves are [Software profile](11-software-profile.md).

Recommended v1 concerns: `new` (capture), `wayfind`, `next` (what to run given frontier + work-item board), `doctor`, plus software-profile `build`, `eval`, `review`. Drop graph, tour, and a 19-skill `dev-*` palette.

## Answer

v1 binder concerns: `new` (capture), `wayfind`, `next` (frontier + work-item board), `doctor`, plus software-profile pointers `build`, `eval`, `review`.

Each is a thin skill that routes to craft or a CLI verb. Do not vendor grilling, TDD, or Wayfinder bodies. Drop graph, tour, and a 19-skill `dev-*` palette. Software gates stay on [Software profile](11-software-profile.md). Skill file shape stays on [Binder skill shape](10-binder-skill-shape.md).
