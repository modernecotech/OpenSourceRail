# OpenSourceRail architecture

v0.6 is a station-powered freewheeling railway. Six lightweight 17 m comfort cars run on twelve passive steel-wheel bogies. Conventional rails on precast concrete support the train; station LIM primaries act on passive onboard aluminium secondaries. The train has no normal-service traction motor or traction battery. Service/essential power, sensing, communications and independent mechanical braking remain onboard.

## The wider platform

OpenSourceRail has three connected products: an owner/builder/operator design and
delivery platform, a reference railway and manufacturing system, and open GoA4
control software. Its lifecycle is plan, design, procure, manufacture, construct,
commission, operate, maintain and renew. Local design authority, competitive
sourcing, repair capability and whole-life affordability apply across all three.

The [ERPNext/Frappe HR app](../deployment/erpnext/README.md) retains business,
workforce, procurement, manufacturing, QA and maintenance functions. The
[FUXA/gateway services](../deployment/supervision/README.md) retain observations,
alarms, history and review-linked lifecycle records. The
[planning workspace](workbench/planning/index.html) retains geographic/service
proposals over historical packets; its v0.6 compilation is unconnected. These are
distinct from the read-only engineering Workbench; company
masters, permissions, device bindings and reviewed imports are deployment inputs.
Their interfaces do not supply movement authority.

The coordinator connects candidate geometry and materials to engineering,
inventory, manufacturing tasks and research CAD/IFC/ERP drafts. A full priced
construction/cashflow plan, qualified shop package and operational asset twin
require additional current-candidate data. Earlier project-twin and lifecycle
examples retain their actual configuration; changing the vehicle does not
requalify them. See [the adoption boundary](first-adoptable-product.md).

## One physical candidate

[development-baseline.toml](../engineering/development-baseline.toml) resolves the selected `wheel_rail_station_lim` family through [the v0.6 engineering layer](../engineering/station_rail/README.md). Vehicle, body, support and propulsion identities are separate. Candidate identity describes physical stock; evaluation identity describes models and scenarios; selection identity records purpose and policy. The retained `pm_maglev_station_powered` and conceptual `wheel_rail_station_lsm` families remain explicit comparisons.

Unchanged component records retain source identities. New bogies, concentrated structural supports, reaction fin and service supply produce a new complete vehicle identity. Counted geometry, supplier reference masses and unlocated allowances are distinguished. Unknown installed mass, force, cost and qualification never become zero.

## Station-led GoA4

Existing Rust ATP, interlocking, OCC, TCMS, door control, station SCADA and train-to-ground communication remain the foundation. Stations reserve route and receiving berth, prove train readiness, sequence motor sections and supervise arrival. Onboard ATP continuously enforces authority and speed using independent brake capability. It must stop the train on communications, authority, receiving or integrity failure. Mainline switches are excluded; depot exceptions remain explicit.

Loss of propulsion does not remove wheel support. Motorless off-zone stopping still requires rescue/towing and evacuation provision. The new wheel/station adapter exercises protection predicates; no physical brake curve, operational GoA4 acceptance or full train motion is implied.

## Coupled engineering

| Domain | Required relationship |
|---|---|
| Vehicle | Full fitout, bogies, service supply, thermal equipment and actual load paths feed mass and inertia |
| Station motor | Force/current/frequency/gap/temperature map, normal forces, slip, heat and section handoff feed the journey |
| Rail/civil | Moving axle reactions, alignment, deflection, torsion, rails/fasteners, piers, foundations and construction |
| Journey | Same mass and geometry, wheel dynamics, independent brakes, service SOC, station power and protection |
| Delivery | BOM, processes, procurement, assembly, CAD/IFC and maintenance share the selected physical IDs |
| Economics | Equal passenger service, routes, reliability, life and price coverage; unavailable totals stay unknown |

The CLI, [current dossier](design-engine/current/README.md), Workbench and [reader](../OpenSourceRail-Book.pdf) resolve this selection. Build runs deterministic reference calculations and produces research delivery records. City performance publication remains held; retained city maps and route inputs are accessible without reusing old magnetic masses or fleet figures.

[The v0.5 archive](archives/v0.5-maglev/README.md) authenticates former sources and results at their Git revision. Historical numerical reproduction requires that pinned checkout. Ordinary current publication never rewrites historical scientific packets.
