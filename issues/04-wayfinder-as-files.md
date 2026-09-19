# Wayfinder as files

Type: grilling
Status: resolved

## Question

Spine’s planning profile is Wayfinder. How do map, tickets, types, blocking, frontier, fog, and out-of-scope sit as files in a target so a stranger’s agent can operate without GitHub Issues?

Must cover: map body sections, ticket identity (number + name), `Type` / `Status` / `Blocked by` / claim, where answers live, that the map is an index (does not restate decisions). Paths themselves are [Two-tier paths](05-two-tier-paths.md).

Recommended: one map file; child ticket files; research write-ups linked not pasted; native `Blocked by: NN`; claim is a field the CLI owns. Match this workspace’s tracker ([docs/issue-tracker.md](../docs/issue-tracker.md)) unless a concrete defect shows up.

## Answer

Planning in a target matches this workspace’s tracker, without GitHub Issues.

- One map file. Sections: Destination, Notes, Decisions so far, Not yet specified (fog), Out of scope. The map is an **index**: gist plus link; it does not restate a ticket’s answer.
- Child ticket files. Identity is number + name (`NN-<slug>.md`, title is the name). Types: research, prototype, grilling, task (`Type:`). Status includes open / claimed / resolved (`Status:`). Blocking is `Blocked by: NN`. Claim is a field the **CLI** owns. Answers live under `## Answer` on the ticket.
- Research write-ups are separate files, linked from the ticket, not pasted onto the map.
- Frontier: open, unblocked, unclaimed tickets.
- Paths themselves stay on [Two-tier paths](05-two-tier-paths.md).
