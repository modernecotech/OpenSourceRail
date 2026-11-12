# v0.6 engineering and delivery roadmap

The next milestone is one reconciled, prototype-ready **research dossier** from
passenger requirements through vehicle, stations, civil works, manufacturing,
service and whole-life cost. A useful calculated outline can be complete while
its installed engineering and physical acceptance remain open.

The proposed v0.6.1 software release has a separate SR-01–SR-06 readiness
contract. Software readiness does not close the seven engineering gates or
assert physical acceptance; see the [software-release ledger](design-engine/v06-software-release/README.md).

The proposed v0.6 software-release scope is limited to three journeys: one fresh
Samawah calculation and source-pinned read-only Baghdad and candidate examples.
The 266-city portfolio and existing engineering evidence remain available; new
broad campaigns, native sweeps and historical archive migration are v0.7+ work
unless a specific release journey is blocked. No frozen release candidate is
pinned yet. See the [release package](releases/v0.6.1/README.md) for maturity,
setup and validation instructions. Software release does not assert that the
railway is accepted or authorized for manufacture, movement or operation.

OpenSourceRail continues to develop three connected products: railway design
and engineering, manufacturing/delivery and maintenance, and city planning and
service. Local manufacture, repairability, open knowledge, business/workforce
integration and equipment observation remain part of that purpose.

## What the integrated pilot now provides

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

## Active work sequence

1. **Optimise equal-service alternatives.** Compare no storage, smaller recovery
   modules, capture/release timing, operating speed, grade and station spacing.
   Preserve the powered-wheel control and station-powered alternatives. Rank
   whole-life cost, energy, reliability and service together; the current store
   adds cost for limited simulated grid-energy savings. No free recovery energy,
   assumed procurement discount or mandatory 900 m LIM is permitted.
2. **Close the installed vehicle.** Resolve motor/gear mounts, bogie and wheel
   geometry, joints, suspension movement, wiring/cooling/protection, access and
   component removal. Reconcile counted body stock, external equipment and
   remaining positive reserves once. Keep failed designs and measured versus
   proposed mass/CG/inertia clearly distinguished.
3. **Extend structural and electrical evidence.** Progress body/running-gear
   fatigue, joints and exceptional loads; civil cracking, prestress losses,
   segment joints, bearings, moving loads and erection. Establish actual
   battery, charger, converter and HVAC duty at hot-weather conditions. Preserve
   exact CAD/FEM source, load, mesh and resource identities and independent
   comparisons; do not transfer numerical proof across physical revisions.
4. **Complete manufacturing and construction definition.** Use the
   [pilot delivery compiler](../engineering/pilot_delivery/README.md) to prepare
   candidate-linked stock/material, make/buy, source process, workstation/tool,
   assembly, inspection, installation/removal and serial/lot planning drafts.
   Replace provisional routes with controlled mating drawings, qualified
   processes, real factory capacities and actual crane/transport configurations.
   Price terminal structures, tooling, temporary works and site scope explicitly.
   Validated hours and missing equipment detail remain unknown, not zero.
5. **Review business and operating handoffs.** Convert reviewed engineering
   quantities through actual ERPNext Item, drawing and inspection mappings;
   preserve approval in ERPNext and workforce planning in Frappe HR. Exercise
   revision → BOM → work → inspection → installation → observation → defect →
   repair → reviewed handback with the new candidate. Retain FUXA/gateway as an
   observation/review interface; draft exports never authorise train movement.
6. **Apply the candidate to a real corridor.** Start with a representative
   Baghdad alignment and one smaller pilot. Replace shared assumptions with
   declared route gradients, access, utilities, ground, demand and local rates.
   Recalculate each cost owner from route quantities instead of multiplying a
   pilot cost/km. Keep editable GIS proposals and validated engineering return
   paths distinguishable.
7. **Consolidate the Workbench and prepare prototypes.** Make requirements,
   alternative comparisons, selected research configuration, costs, confidence,
   manufacturing drafts and next tests visible in one journey. Build the
   highest-risk mechanism and structural rigs first. Correlate measurements
   before independent engineering review and subsequent release decisions.

Coordinated work starts with
[`./osr design railway`](design-engine/coupled-railway/README.md). The
[current dossier](design-engine/current/README.md),
[cost and delivery method](design-engine/model-based-cost-and-delivery.md) and
[capability register](capabilities/README.md) distinguish current reference
outputs from new research workflows. Keep the
[v0.4 platform](https://github.com/modernecotech/OpenSourceRail/tree/v0.4.0),
[v0.5.1 research](https://github.com/modernecotech/OpenSourceRail/tree/v0.5.1)
and [source-bound archives](archives/pre-comfort-default/manifest.json)
independently reproducible.

## Cost, resource and production assumptions

Keep inexpensive Rust screening ahead of detailed CAD/FEM. Reuse numerical work
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

## Physical and release gates

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
