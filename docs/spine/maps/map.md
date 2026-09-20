# Map

## Destination

This target's product docs match the fleet-capable spine already in the tree.
`spec.md`, `CONTEXT.md`, and README describe one-winner claims, real eval/review
gates, doctor recovery, and `spine migrate`. Publish/tag is later.

## Notes

This repo is the dogfood target. The engine rewrite is done — see
[productionize.md](productionize.md). This map is docs=code on 0.2.0, not
another orchestration pass. One ticket per session. The reviewer does not edit.

## Decisions so far

- [Dogfood this target](../tickets/01-dogfood-this-target.md): live-repo dogfood
  (not the throwaway proof). Docs=code on 0.2.0; Claim is one-winner; publish
  stays later.
- [Review the productionize diff](../tickets/14-review-the-productionize-diff.md):
  code matches productionize tickets; spec/README/binder lagged. Architecture
  top remaining: deepen Claim. Not graduated onto this map.
- [Align spec.md with the 0.2.0 tree](../tickets/15-align-spec-md-with-the-0-2-0-tree.md):
  spec, README, binder eval/review, productionize fog, CHANGELOG describe the
  shipped machine.

## Not yet specified

- Publish/tag a 0.3.0 (version, changelog, PyPI).

## Out of scope

Hosted orchestration; multi-repo / cross-machine coordination; rewriting the
0.2.0 machine; changing shipped 0.1.0/0.2.0 history; deepening Claim / doctor /
board (ticket 14) unless a later map names that work.
