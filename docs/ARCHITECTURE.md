# OpenSourceRail architecture

OpenSourceRail v0.5 develops ferrite PM-biased active-attraction maglev for urban transport. Its current physical basis is fixed onboard magnetic modules, powered linear propulsion, passive reaction iron and compact elevated concrete guidebeams. Batteries and station charging support operation; independent protection, cooling, capture, braking, parking and recovery remain essential design obligations.

The objective is broad city access with a small ground footprint, few moving running-gear parts and practical local manufacture. Ordinary mainlines target repeated elevated bays. Route rights, foundations, utilities, curvature, station access and evacuation determine where the concept is feasible.

## Linked design layers

| Layer | Controlled definition | Evidence |
|---|---|---|
| Service and city | Geography, demand, capacity, headways, route lengths, station locations and local assumptions | Formation, fleet, energy/charging, quantities, provisional costs and unresolved route gates |
| Mechanical | Magnetic cartridges, structural frame, passenger systems, energy, doors and evacuation | Partial native solids, mass budgets, interface checks, analytical screens and production obligations |
| Civil | Guidebeams, reaction iron, joints, supports, foundations, stations and services | Section/beam calculations, support-demand studies, native envelopes and manufacturing/erection quantities |
| Software | Rust support control, protection interfaces, module allocation, fault handling and advisory evacuation | Offline executable tests, virtual replay and a two-way flexible-beam coupling |
| Industrialisation | Materials, fabrication processes, tooling, factory throughput, transport, erection and origin | Quantity-and-process planning allowances and explicit unpriced scope |
| Acceptance | Exact revision, requirements, tests, evidence, reviewer and serial identity | Source-bound receipts and open engineering/manufacturing/physical gates |

[Infrastructure policy](../lib/templates/infrastructure.toml), [configuration](../engineering/ferrite_maglev/reference-configuration.toml) and [engineering modules](../engineering/ferrite_maglev/README.md) control these interfaces. Generated city inputs use `city.json`; their outputs follow the same maglev compiler and cost model.

## Current evidence boundary

Native CAD covers selected partial assemblies. Assembly visibility videos reveal final-position geometry; they do not establish collision-free installation or deployment. Field-equation controls do not establish real magnetic lift capacity. Virtual control/beam replay does not establish physical SBC deadlines or qualified train dynamics. Open geographic data supports planning estimates, rather than surveyed boundaries, soil capacity or utility clearance.

A continuous-walkway-free guideway remains conditional on qualified onboard and route evacuation. Vertical spiral chutes require usable landings and assisted evacuation at every allowed stopping location. No blanket waiver of evacuation or structural requirements is implied by the compact layout.

All release flags remain false and accepted engineering/physical releases remain zero. Local content, installed programme cost and the funding requirement require complete origin-traced quantities, configured supplier offers, construction scope and financing terms. Successful publication integrity is separate from engineering acceptance.
