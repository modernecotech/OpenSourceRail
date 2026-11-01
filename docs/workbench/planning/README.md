# City planning proposals

The planning workspace edits route, stop, service and origin–destination proposals over the current city geography and map context. Open it from [`index.html`](index.html).

Export an edit bundle from the workspace, then compile and verify the handoff:

```sh
./osr plan compile edits.json --output build/my-plan
./osr plan verify build/my-plan
```

The immutable handoff is bound to the selected v0.6 candidate and the source identities used for the proposal. It carries route, stop, service and OD proposals only. It contains no vehicle, propulsion, fleet, civil quantity, cost, performance or cashflow results.

Missing unit prices can be covered in a separate candidate-specific low/base/high Class C estimate from calculated quantities and declared assumptions. Supplier quotes improve procurement readiness but are not required for design-stage cost comparison. A complete installed city estimate still needs route-specific quantities and site scope.

Candidate-specific route performance, procurement groups, construction schedules and full city costs remain held until their supporting evidence is available. Planning changes do not grant movement authority.

For the connected candidate workflow, see the [coordinated railway design](../../design-engine/coupled-railway/README.md), [current platform capabilities](../../capabilities/README.md) and [current engineering dossier](../../design-engine/current/README.md).
