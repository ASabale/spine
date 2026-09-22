# Owner-checked advance

Type: task
Status: open
Blocked by: 16-claim-as-one-module.md
Owner:
Claimed-at:

## Question

`advance` accepts any actor and mutates any item: an agent can advance another
agent's claimed work item. The engine must validate the actor against the claim
owner: a non-owner advancing a claimed item is a typed violation; an owner
advancing their own item is fine; an unowned item advances for anyone.

Resolved = the engine rejects non-owner advance of a claimed item with a typed
error.

- [ ] Non-owner actor advancing a claimed item → typed error, no mutation
- [ ] Owner advancing their own claimed item succeeds
- [ ] Unclaimed / unowned items advance for any actor
- [ ] Tickets and work items subject to the same rule
- [ ] `make test` green
