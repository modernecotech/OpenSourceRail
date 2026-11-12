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
The remaining workstreams below remain open.

The [agent delivery and tool migration plan](plans/v0.7-agent-delivery-plan.md)
assigns bounded work to agents and subagents, with Rust migration benchmarks,
CAD/FEA/GIS promotion criteria, legacy retirement gates and resource budgets.

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

1. **Handover and baseline:** finish the finite v0.6 installation/documentation
   checks; identify the Samawah before/after cases, one vehicle candidate, one
   civil assembly and the door operator. Capture baseline outputs and timings.
2. **Project continuity:** get the station edit through service, fleet and a
   preliminary quantity/cost delta in the existing Workbench early. Every result
   has a source identity, and missing interfaces are visible.
3. **Engineering and native GIS:** develop the vehicle, civil and module evidence
   against those fixed interfaces; complete the native return path and reconcile
   costs from actual quantity changes.
4. **Lifecycle and generalisation:** connect the module BOM to the ERP lifecycle,
   compile the dossier and replay one Baghdad corridor.
5. **Release acceptance:** resolve defects exposed by both journeys, run the
   clean-install v0.7 acceptance case, and publish supported scope and remaining
   engineering limitations.

The indicative small-team sequence is baseline/handover first, continuity in
weeks 1–2, engineering and GIS in weeks 3–6, lifecycle/Baghdad in weeks 7–8, and
acceptance in weeks 9–10. These are planning estimates. Supplier inputs, physical
measurements and unresolved structural assumptions have separate milestones;
software can show exactly which conclusions depend on them.

## Consolidate existing computation

Use selected-city source binding, verified caches and incremental publication
checks already in the repository. Measure wall time by stage at the corridor
entry point. If a station edit launches an unchanged vehicle analysis, repair
the dependency first. Benchmark an expensive required kernel before extending
Rust or vectorisation. Avoid broad rewrites, all-city regeneration and duplicate
calculation pipelines for this milestone. Preserve failed, interrupted and
out-of-domain evidence and maintain the project disk reserve during execution.

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
