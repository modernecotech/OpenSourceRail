# City planning proposals

The planning workspace edits route, stop, service and origin–destination proposals over the current city geography and map context. Open it from [`index.html`](index.html).

Export an edit bundle from the workspace, then compile and verify the handoff:

```sh
./osr plan compile edits.json --output build/my-plan
./osr plan verify build/my-plan
```

The immutable handoff is bound to the selected v0.6 candidate and the source identities used for the proposal. It carries route, stop, service and OD proposals only. It contains no vehicle, propulsion, fleet, civil quantity, cost, performance or cashflow results.

Missing unit prices can be covered in a separate candidate-specific low/base/high Class C estimate from calculated quantities and declared assumptions. Supplier quotes improve procurement readiness but are not required for design-stage cost comparison. A complete installed city estimate still needs route-specific quantities and site scope.

The [calculated city atlas](../../design-engine/city-atlas/README.md) provides current outline service, fleet, civil quantities, complete estimated costs and delivery studies for all 266 cities. A completed local study can be opened here for candidate-bound editing and recalculation. The ordinary planning handoff remains a proposal, while the calculated study carries its own result identities and assumptions. Verified physical performance, procurement approval, construction release and movement authority remain separate.

For the connected candidate workflow, see the [coordinated railway design](../../design-engine/coupled-railway/README.md), [current platform capabilities](../../capabilities/README.md) and [current engineering dossier](../../design-engine/current/README.md).
