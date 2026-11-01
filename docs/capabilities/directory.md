# Current OpenSourceRail capabilities

OpenSourceRail connects city planning, railway engineering and manufacturing,
business workflows, equipment supervision and open train-control software.
The current v0.6 reference is a six-car, wheel-supported railway with
station-powered linear induction motors. Software completion and physical
qualification are tracked separately.

| Product | Current entrypoint | Available scope and boundary |
|---|---|---|
| Design and delivery platform | [Planning workspace](../workbench/planning/index.html), `./osr plan compile` and `./osr plan verify` | Verifies and displays current city map context, then edits route, stop, service and OD proposals. The immutable handoff is bound to the selected candidate and carries proposals only; route performance, procurement quantities, construction schedules, city costs and movement authority are outside its scope. |
| Six-car factory work-package draft | [Current Workbench](../workbench/current/index.html); `./osr twin factory-draft compile` and `./osr twin factory-draft verify` | From a verified planning handoff, creates an immutable draft using the selected candidate's Class C ledger and source-linked low/base/high process-hour lines under two 8-hour production shifts. It models one serialized lane; crew counts, parallel capacity and calendar dates are not inferred. Civil schedules, procurement, staffing, railway operations and release remain held. |
| Vehicle mass reconciliation | [Occurrence-level ledger](../design-engine/mass-reconciliation/current/README.md) and its [roof-finish distribution estimate](../design-engine/mass-reconciliation/current/README.md#provisional-roof-finish-distribution-estimate) | The 47.809 kg/car roof-finish estimate uses 45.05 m² of source roof surfaces and declared thickness/density. It is already in the scalar account, adds no geometry or tare, leaves the 10.090 t/car residual unchanged, and does not establish installed mass or position. |
| Railway and manufacturing system | [Current engineering dossier](../design-engine/current/README.md), `./osr design railway` | Coordinates one candidate through geometry, mass, engineering analysis, inventory, propulsion, braking, civil and manufacturing work. Installed equipment, physical journey evidence and release remain incomplete where identified in the dossier. |
| Cost and production planning | [Selected-candidate synthetic corridor estimate](../design-engine/current/exports/selected-system-cost.json), [selected-vehicle estimate](../design-engine/current/exports/selected-vehicle-cost.json), [model and sourcing method](../design-engine/model-based-cost-and-delivery.md) | Generated research bundles retain separate identities. The selected candidate has a low/base/high Class C estimate across 14 scopes for one synthetic 6 km, three-station corridor; city/site quantities, supplier offers, qualified service and physical acceptance remain open. |
| Business and workforce workflows | [ERPNext and Frappe HR](../../deployment/erpnext/README.md) | Provides configurable project, procurement, workforce, manufacturing, quality and maintenance integrations. Site configuration, reviewed imports and operational procedures remain deployment work. |
| Equipment supervision | [FUXA and gateway](../../deployment/supervision/README.md) | Provides integration components for equipment observations, alarms, history and review-linked records. Device bindings and commissioning are deployment work; the integration does not provide movement authority. |
| Open GoA4 controls | [Rust controls and integration](../../crates/README.md), [system architecture](../ARCHITECTURE.md) | Develops station-led dispatch, ATP, interlocking, train supervision and fault-response software. Current work is research and simulation; there is no live railway or safety approval. |

For the whole-system purpose and a controlled adoption sequence, see the
[project README](../../README.md) and [first adoption path](../first-adoptable-product.md).
