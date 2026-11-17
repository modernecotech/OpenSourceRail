# v0.7 corridor-to-lifecycle roadmap

[v0.6.1 — Open Engineering Platform](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.6.1)
is the published v0.6-series software release at
`5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea`. Use its
[installation route, downloads and known limitations](releases/v0.6.1/README.md).
The existing `v0.6.0` and `v0.6.1` tags stay at their recorded commits.

OpenSourceRail continues to connect railway design and engineering,
manufacturing/delivery and maintenance, and city planning and service. Local
manufacture, repairability, open knowledge, ERPNext/Frappe HR and FUXA/gateway
integration remain part of the platform's purpose.

## Finish the v0.6 handover

The handover is complete. A fresh public clone of the published tag followed
its installation asset, verified SHA256SUMS and completed the documented
Samawah journey twice. [Installation results](releases/v0.6.1/installation-verification.md)
record commands, identities, timings and the environment limits. The retained
readiness-browser harness now uses an external temporary output directory;
[its repaired CI job passed](https://github.com/modernecotech/OpenSourceRail/actions/runs/43183752707/job/131065771211)
on main `0472a4f3cadb23847e071e693294a418bf54c3b0`.

The [older design-closure campaign](../campaigns/v06-design-integration-closure.toml)
is superseded only where it controlled software publication. Its seven
open/partial engineering findings remain visible in the
[engineering ledger](design-engine/v06-design-closure/README.md). The retained
[authenticated-review profile](design-engine/v06-software-release/README.md)
keeps its truthful pending records; it is not a reason to repeat publication
checks or withhold the already published release.

## Governing v0.7 result: one affordable railway that can be built locally

The next system-level benchmark is the reproducible **synthetic 30 km,
12-station level corridor** in the [current-source line30 packet](design-engine/line30-current-20261117/README.md).
The distinct **Samawah city demonstration** carries its actual alignment and
station edit through the same-candidate journey. A **1.5–2 km physical
demonstrator** must prove vehicle, propulsion, stopping, recovery and civil
interfaces on a declared route and load case. Use one stated passenger demand,
route, station spacing, grade, accessibility, crowd and emergency requirements
for each equal-service comparison. The 120-second comfort reference and the
former higher-capacity formation are named alternatives, not automatic
selections. Keep unsupported quantities bounded or unknown.

| Priority | Decision evidence required |
|---|---|
| Complete corridor | One same-candidate chain from route and service through installed vehicle, propulsion, civil quantities, construction, fleet, energy, fourteen-scope capital and lifecycle cost, local production and maintenance. Show the Workbench before/after edit and all unresolved holds. |
| Propulsion | Compare station-powered unpowered-wheel, powered-wheel and ferrite-assisted lightweight support research at equal service, with separate candidate and evaluation identities. Test the adverse grade and longest gap, wet-rail and emergency stopping, rescue, electrical and thermal duty. Do not promote the best-modelled option by default. |
| Civil and train | Select one beam–pier–foundation–erection sequence and one representative car with a removable, testable door module. Count installed mass, interfaces, access, tooling, factory hours, erection hours and repair work. |
| Local delivery | Report make/buy by material value, fabrication and QA hours, tooling, supplier availability and imported critical inputs; count construction months and disruption per kilometre. Component count alone is not local value added. |

Rank candidates by complete installed cost per route-kilometre, cost per unit of
normal passenger capacity, lifecycle cost per passenger-kilometre, accepted
viaduct cost per kilometre, local manufacturing and maintenance value, and
construction time and disruption per kilometre. Show each numerator, service
denominator, price basis and uncertainty; safety and accessibility remain
mandatory screens. The current 30 km estimate is a comparison control, not a
price promise or evidence of physical acceptance.
The [first v0.7 engineering gate](design-engine/v07-affordable-corridor/README.md)
records the distinct Samawah service and longest-gap screen, equal-service
propulsion bounds, a segmented civil sequence and one removable door proposal.

Before accepting an architecture, subsystem or major toolchain change, record
whether it improves whole-railway cost or necessary service, local build and
repair, independence from hard-to-source technology, complete system behaviour,
and open reproducibility. A software-only change needs a measured runtime,
memory, storage, reliability or user-journey gain that warrants its upkeep.
The 266-city catalogue supports this deep example; it does not substitute for
one integrated, buildable corridor.

## First v0.7 milestone: the Samawah station merge

Open the published Samawah example, apply the retained station-merge intent,
and produce a side-by-side report of station count, service assumptions, fleet,
civil quantities, fourteen-scope costs and unresolved inputs. Each difference
must trace to the edit and its dependent calculation. Reuse unaffected vehicle
and manufacturing outputs rather than rerunning them.

The retained engineering case found two station markers **79.977 m apart**
against a **120 m platform assumption**. Its
[midpoint merge packet](design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-03/README.md)
provides the before/after edit and provenance. Carry both cases through the new
workflow. That packet belongs to its declared candidate/source epoch: applying
the edit to the published example must produce and identify the matching new
revision, not silently transfer old compact-drive results to another vehicle.
Access, catchment, platform fit, route feasibility and unpriced work remain
explicit inputs or findings.

The [first Workbench comparison is implemented and browser-verified](design-engine/v07-project-continuity/README.md).
The published case already groups the close pair operationally: raw markers
change from 26 to 25, operational stops remain 25 and fleet remains 81. Both
sides retain the same vehicle candidate and unchanged civil quantity identity;
the report exposes actual service, access and fourteen-scope cost changes.
The [17 November engineering gate](design-engine/v07-affordable-corridor/README.md)
replayed the after-edit Samawah city calculation against current sources and
retained its provisional price, while showing the 5.738 km line-1 coast failure
and powered-axle research fallback. This is not a surveyed grade, selected
propulsion installation or completed native GIS return journey.
The remaining workstreams below remain open.

The [agent delivery and tool migration plan](plans/v0.7-agent-delivery-plan.md)
assigns bounded work to agents and subagents, with Rust migration benchmarks,
CAD/FEA/GIS promotion criteria, legacy retirement gates and resource budgets.
The [execution record](design-engine/v07-execution/README.md) now contains the
verified two-worker improvement, opt-in Rust scheduler, fresh CAD/FEA controls,
native Samawah/Baghdad cycles and clean-install CI evidence. Its task ledger
keeps the remaining installed-candidate, detailed module and lifecycle work open.

## v0.7 delivery workstreams

| Workstream | Required integrated result |
|---|---|
| Project continuity | One project entry point binds corridor revision, vehicle candidate, civil option, quantities, cost and dossier. A station edit invalidates its dependants; the Workbench shows changed results and verified reuse of unaffected work. |
| Installed vehicle | Select one six-car candidate for detailed integration. Resolve recurring geometry definitions, door motion, equipment access/removal and mass bounds. Keep the passive reference and propulsion alternatives separate; supplier and measurement dependencies remain explicit. |
| Civil works and station | Carry one span, support and station interface through bearing assumptions, moving loads, construction sequence and lifting checks. Establish crane capacity at the actual installation radius. Retain SolidCraft/FieldCraft and independent FreeCAD/CalculiX evidence. |
| GIS and economics | Complete a fresh native GIS edit–export–import–reprice cycle for the selected Samawah revision. Trace station count, fleet, guideway quantities and all fourteen cost scopes; identify transferred rates and unpriced quantities. Check the implementation on one Baghdad corridor afterward. |
| Manufacture and lifecycle | Use the door operator as the representative module. Bind drawings, tolerances, BOM, assembly/tooling and QA criteria to its geometry and revision; exercise removal/replacement, wiring and motion clearance. Run that actual candidate-linked module through the existing ERPNext/FUXA lifecycle rather than inheriting the synthetic one-unit kit result. |
| Workbench and release | Guide one corridor edit through service, cost and revised dossier, with links to calculations, drawings and open findings. Open the same module for manufacture planning, QA and maintenance. Preserve before/after outputs and replay the full journey from a clean install. |

## Delivery order and acceptance evidence

1. **Handover and baseline — complete:** the published v0.6.1 installation,
   Samawah before/after comparison, candidate boundaries and bounded performance
   baseline have recorded source identities and timings.
2. **Complete corridor — active:** finish one Samawah same-candidate installed
   vehicle, propulsion, civil, fleet, cost and delivery handoff. The station
   edit already reaches service, fleet and fourteen cost scopes; missing
   installed stages stay visible until supported inputs and measurements exist.
3. **Equal-service decisions — active:** resolve grade, stopping, recovery and
   thermal limits across the three explicit propulsion/support families; then
   compare one buildable civil sequence and representative car/door assembly.
   Source-bound calculations alone do not choose a physical system.
4. **Local delivery and interaction — active:** measure make/buy value and
   factory/erection hours, then run the actual candidate-linked module through
   ERPNext receipt, QA, replacement and handback. Show the complete Samawah
   journey in the Workbench before generalising to one Baghdad corridor.
5. **Release acceptance:** resolve defects exposed by both journeys, run the
   clean-install v0.7 acceptance case, and publish supported scope and remaining
   engineering limitations.

The original week ranges were planning estimates and are superseded by the
[execution ledger](design-engine/v07-execution/README.md). Supplier inputs,
physical measurements and unresolved structural assumptions have separate
milestones; software can show exactly which conclusions depend on them.

## Consolidate existing computation

Use selected-city source binding, verified caches and incremental publication
checks already in the repository. Measure wall time by stage at the corridor
entry point. If a station edit launches an unchanged vehicle analysis, repair
the dependency first. Benchmark an expensive required kernel before extending
Rust or vectorisation. Avoid broad rewrites, all-city regeneration and duplicate
calculation pipelines for this milestone. Preserve failed, interrupted and
out-of-domain evidence and maintain the project disk reserve during execution.
Keep full historical method replay as an explicit reproduction task; ordinary
development should check bounded source/payload integrity and label current-tool
compatibility separately. A retained verifier's tool-version mismatch remains
a recorded historical replay hold, not a reason to pin the active CAD/FEA
toolchain or grant physical acceptance.
The [15 November runtime and toolchain review](plans/v0.7-runtime-toolchain-review.md)
records the current storage inventory, bounded memory experiments and upstream
CAD/FEA/GIS compatibility probes. It does not change the selected reference or
the [execution ledger](../campaigns/v07-execution.json).

## Retained engineering foundation

The [reconciled recovery pilot](design-engine/reconciled-pilot/README.md) and
[no-store control](design-engine/reconciled-pilot-no-store/README.md) connect an
installed-body hypothesis, separately owned drive/BOP additions, mass and axle
loads, civil design, concurrent trains, station energy allocation and
fourteen-scope costs. Several nominal model timetables complete 16/16 arrivals.
Source-linked CAD and independent structural comparisons are retained within
their declared applicability. These achievements close important software and
calculated-outline links; equipment characteristics remain provisional.

The [selected development reference](../engineering/development-baseline.toml)
remains passive and wheel-supported. The newer powered-wheel pilots are research
alternatives, with separate physical and evaluation identities. No installed
propulsion architecture is physically selected. Body-plus-reserve subtotals
exclude external motors, gearboxes, drive BOP and recovery interfaces; integrated
mass and cost must come from the same candidate. A child revision must propagate
through all affected evaluations rather than inherit its parent's results.


Coordinated work continues through
[`./osr design railway`](design-engine/coupled-railway/README.md), the
[cost and delivery method](design-engine/model-based-cost-and-delivery.md),
[pilot delivery compiler](../engineering/pilot_delivery/README.md),
[ERPNext/FUXA lifecycle](integration/v06-platform.md) and
[capability register](capabilities/README.md). Retain the
[v0.4 platform](https://github.com/modernecotech/OpenSourceRail/tree/v0.4.0),
[v0.5.1 research](https://github.com/modernecotech/OpenSourceRail/tree/v0.5.1)
and [source-bound archives](archives/pre-comfort-default/manifest.json)
independently reproducible.

## Cost, resource and production assumptions

Keep inexpensive screening ahead of detailed CAD/FEM. Reuse numerical work
only for the exact source, tool, physical candidate, load, mesh and resource
request. Run independent cases within measured memory budgets, preserve failed
runs and benchmark useful candidates per compute-hour. Python remains useful
for orchestration and specialist integration.

Current outline scenarios use two 8-hour production shifts and two 8-hour civil
shifts. Operating cost uses two shifts for 16/18-hour service and three for the
24-hour case. Utilisation, shift premiums, relief staffing and wages remain
explicit hypotheses. Equivalent resource hours do not establish an actual crew,
production calendar, construction critical path or approved roster.

Every price retains quantity, source or assumption, scope, uncertainty and
exclusions. Factory, delivered, installed and lifecycle totals remain distinct.
Direct part/process allowances, external reserves and fourteen-scope accounts
must reconcile without counting the delivery decomposition or capacity proxies
again. China sourcing, bulk procurement and local manufacture can be compared
using explicit production/supply evidence; an automatic discount is not evidence.

## Open physical engineering gates

| Area | Required next evidence |
|---|---|
| Vehicle | Installed mounting and movement geometry, remaining equipment, qualified joints/running gear, measured or validated mass/CG/inertia |
| Propulsion and recovery | Attainable force-speed-duty envelopes, capture/reset/release losses, thermal limits, independent stopping and recovery |
| Electrical and HVAC | Hot-weather charge/discharge/converter limits, cooling, emergency endurance, fire/isolation and maintenance access |
| Protected service | Model bounds plus validated braking/WSP, degraded operation, terminal protection, separation, rescue and actual controls |
| Civil and construction | Prestress/joints/cracking/fatigue, bearing/contact and dynamic behaviour, site ground, temporary works and verified lift/transport configurations |
| Production and business | Controlled drawings, tolerances, materials/process qualification, QA hold points, reviewed ERP conversion, actual capacity and traceable installation |
| Economics and site | Equal-service factory-to-installed/lifecycle ranges, renewals/recovery/disposal, local demand, utility/land/ground and supplier evidence |
| Prototype and release | Authenticated measurements, model correlation, independent review and separate manufacturing/operating approvals |

Software completion, numerical convergence and a favourable estimate do not
substitute for physical evidence or independent acceptance. Draft tasks and
calculated outlines remain useful completed design-stage results.
