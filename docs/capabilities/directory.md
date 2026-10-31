# Current OpenSourceRail capabilities

OpenSourceRail connects city planning, railway engineering and manufacturing,
business workflows, equipment supervision and open train-control software.
The current v0.6 reference is a six-car, wheel-supported railway with
station-powered linear induction motors. Software completion and physical
qualification are tracked separately.

| Product | Current entrypoint | Available scope and boundary |
|---|---|---|
| Design and delivery platform | [Planning workspace](../workbench/planning/index.html), `./osr plan compile` and `./osr plan verify` | Edits local geography, route, stop, service and OD proposals. The immutable handoff is bound to the selected candidate and carries proposals only; route performance, procurement quantities, construction schedules, city costs and movement authority are outside its scope. |
| Railway and manufacturing system | [Current engineering dossier](../design-engine/current/README.md), `./osr design railway` | Coordinates one candidate through geometry, mass, engineering analysis, inventory, propulsion, braking, civil and manufacturing work. Installed equipment, physical journey evidence and release remain incomplete where identified in the dossier. |
| Cost and production planning | [Model-based cost and delivery](../design-engine/model-based-cost-and-delivery.md), [sourcing guide](../../engineering/sourcing/README.md) | Calculates provisional candidate costs and production assumptions when quotations are unavailable. Assumptions and uncertainty remain visible; estimates are not supplier commitments or complete installed project prices. |
| Business and workforce workflows | [ERPNext and Frappe HR](../../deployment/erpnext/README.md) | Provides configurable project, procurement, workforce, manufacturing, quality and maintenance integrations. Site configuration, reviewed imports and operational procedures remain deployment work. |
| Equipment supervision | [FUXA and gateway](../../deployment/supervision/README.md) | Provides integration components for equipment observations, alarms, history and review-linked records. Device bindings and commissioning are deployment work; the integration does not provide movement authority. |
| Open GoA4 controls | [Rust controls and integration](../../crates/README.md), [system architecture](../ARCHITECTURE.md) | Develops station-led dispatch, ATP, interlocking, train supervision and fault-response software. Current work is research and simulation; there is no live railway or safety approval. |

For the whole-system purpose and a controlled adoption sequence, see the
[project README](../../README.md) and [first adoption path](../first-adoptable-product.md).
