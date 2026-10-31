# Current platform capabilities

OpenSourceRail's active v0.6 workflow connects planning proposals, one identified
railway candidate, engineering evaluation, delivery records and business or
supervision handoffs.

| Capability | Current entry point |
|---|---|
| Candidate engineering and coupled design | [`./osr design railway`](../design-engine/coupled-railway/README.md) |
| Candidate CAD/IFC, BOM, procurement, assembly and control records | [Current export manifest](../design-engine/current/exports/manifest.json) and [delivery package index](../design-engine/coupled-railway/delivery-index.json) |
| City geography, map context and route/service proposals | [Planning workspace](../workbench/planning/index.html); `./osr plan compile` and `./osr plan verify` |
| Calculated manufacturing and lifecycle scenarios | [Model-based cost and delivery plan](../design-engine/model-based-cost-and-delivery.md) |
| Business and workforce workflows | [ERPNext and Frappe HR integration](../../deployment/erpnext/README.md) |
| Equipment observation and review records | [FUXA and gateway integration](../../deployment/supervision/README.md) |
| Open control software | [Rust control workspace](../../crates/README.md) |

Planning and delivery records are proposals or research drafts. Route
performance, complete installed quantities, physically supported journeys,
site-specific costs, equipment commissioning and safety acceptance remain
separate work. Software functionality does not grant movement authority or
release a design for manufacture or operation.
