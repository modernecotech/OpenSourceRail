# City geography and planning inputs

OpenSourceRail includes **266 city geography records** for local route and service planning. The selected v0.6 reference uses six wheel-supported comfort cars with station LIM propulsion. Routes and stops are planning inputs; **city performance evaluation is held** pending current drive, braking, complete vehicle/civil and cost evidence.

[Current geographic register and holds](../../docs/design-engine/current/cities.json) · [Current engineering](../../docs/design-engine/current/README.md) · [Workbench](../../docs/workbench/current/index.html) · [Planning proposals](../../docs/workbench/planning/index.html)

The planning workspace edits geography, stops, service and origin-destination proposals. Compile and verify an immutable handoff with:

```bash
./osr plan compile edits.json --output build/my-plan
./osr plan verify build/my-plan
```

The handoff is bound to the selected v0.6 candidate and carries route, stop, service and OD proposals only. It does not contain vehicle, propulsion, fleet, civil quantity, cost, performance or cashflow results. Candidate-specific route performance, procurement groups, construction schedules and full city costs remain held. Planning changes do not grant movement authority.

[Project introduction](../../README.md) · [Planning workspace](../../docs/workbench/planning/index.html) · [Current city evaluation status](../../docs/design-engine/current/cities.json).
