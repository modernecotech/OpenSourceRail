# Current platform capabilities

OpenSourceRail's active v0.6 workflow connects planning proposals, one identified
railway candidate, engineering evaluation, delivery records and business or
supervision handoffs.

| Capability | Current entry point |
|---|---|
| Candidate engineering and coupled design | [`./osr design railway`](../design-engine/coupled-railway/README.md) |
| Selected vehicle mass account | [Current mass reconciliation and roof-finish distribution estimate](../design-engine/mass-reconciliation/current/README.md#provisional-roof-finish-distribution-estimate) |
| Candidate CAD/IFC, BOM, procurement, assembly and control records | [Current export manifest](../design-engine/current/exports/manifest.json) and [delivery package index](../design-engine/coupled-railway/delivery-index.json) |
| City geography, map context and route/service proposals | [Planning workspace](../workbench/planning/index.html); `./osr plan compile` and `./osr plan verify` |
| Candidate-bound factory work package | [Current Workbench](../workbench/current/index.html); `./osr twin factory-draft compile` and `./osr twin factory-draft verify` |
| Calculated manufacturing and lifecycle scenarios | [Selected-candidate 6 km system estimate](../design-engine/current/exports/selected-system-cost.json), [selected vehicle estimate](../design-engine/current/exports/selected-vehicle-cost.json), and [cost and delivery method](../design-engine/model-based-cost-and-delivery.md) |
| Business and workforce workflows | [ERPNext and Frappe HR integration](../../deployment/erpnext/README.md) |
| Equipment observation and review records | [FUXA and gateway integration](../../deployment/supervision/README.md) |
| Open control software | [Rust control workspace](../../crates/README.md) |

A factory draft is compiled from a verified planning handoff. It creates an immutable six-car production work package from the selected candidate's Class C ledger and low/base/high process-hour proxies under two 8-hour production shifts. The schedule represents one serialized lane; it does not infer crew counts, parallel capacity or calendar dates. It is not an ERPNext import, purchase order or manufacturing release. Civil and railway-operations schedules remain held.

The planning handoff itself contains route, stop, service and OD proposals only.
It excludes vehicle, propulsion, fleet, civil quantity, cost, performance and
cashflow results; candidate-specific evaluations remain separate.

The selected vehicle ledger retains a 10.090 t/car reference or unlocated residual. A separate calculated roof-finish estimate distributes the already-accounted 47.809 kg/car over 45.05 m² of source roof surface; it adds no mass or candidate CAD occurrence and does not establish installed location.

Planning and delivery records are proposals or research drafts. Route
performance, complete installed quantities, physically supported journeys,
city-specific costs, equipment commissioning and safety acceptance remain
separate work. Software functionality does not grant movement authority or
release a design for manufacture or operation.
