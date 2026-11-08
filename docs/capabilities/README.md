# Current platform capabilities

OpenSourceRail connects three products: an open railway design and engineering
system, a manufacturing/delivery and maintenance platform, and city planning and
service tools. The aim is affordable whole-life transport supported by local
design, manufacture and repair knowledge. Planning, engineering, business and
equipment-observation records have distinct identities and review gates.

## Reference and research configurations

The [development baseline](../../engineering/development-baseline.toml) remains a
six-car, wheel-supported **passive reference**: six 17 m cars, 44 fixed seats and
two wheelchair places per car, with independently sized service batteries and
brakes. It has no selected onboard traction installation. Speed, headway,
propulsion architecture and powered length are candidate decisions; neither a
900 m LIM nor the historical 120-second schedule is mandatory.

The [reconciled research pilot](../design-engine/reconciled-pilot/README.md) and
[no-store control](../design-engine/reconciled-pilot-no-store/README.md) are newer,
separately identified **powered-wheel research candidates**. They join counted
body parts, explicit external drives and reserves, axle loads, civil geometry,
concurrent-train simulations, station storage alternatives and fourteen-scope
cost ledgers. Several declared nominal timetables complete 16/16 model arrivals.
This is conditional simulation evidence; it neither changes the passive
reference nor selects an installed architecture for physical deployment.

Body mass subtotals, including a provisional installation reserve, remain
separate from external motors, gearboxes, drive BOP and recovery fittings.
Whole-train mass and cost must be read from the matching integrated evaluation.
Proposed component positions, CAD volume comparisons and solver agreement do
not establish measured installed mass, a collision-free assembly or qualified
hardware. Native results apply only to their exact source, load, mesh and
candidate; the no-store alternative does not inherit recovery-candidate FEM.

## Available workflows

| Capability | Current entry point and boundary |
|---|---|
| Coordinated candidate engineering | [`./osr design railway`](../design-engine/coupled-railway/README.md); preserves component/evaluation identities and open evidence gates |
| Reconciled research assembly and service | [Recovery pilot](../design-engine/reconciled-pilot/README.md) and [no-store control](../design-engine/reconciled-pilot-no-store/README.md); conditional model-level arrivals, economics and fault cases |
| Native CAD and structural comparison | [SolidCraft/FieldCraft pilot](../design-engine/craft-backends/README.md), [viaduct alternatives](../design-engine/viaduct-backends/README.md) and reconciled pilot; independent FreeCAD/CalculiX comparisons where recorded |
| Counted vehicle manufacturing definition | [Vehicle parts catalogue](../design-engine/vehicle-parts/README.md) and pilot installed-body records; materials, processes and stock quantities with detailed-drawing holds |
| Candidate-bound pilot manufacturing and installation proposals | [Delivery compiler](../../engineering/pilot_delivery/README.md); local draft parts, source assembly routes, inspection holds, external ownership and existing cost-scope references |
| Selected reference mass account | [Mass reconciliation and roof-finish distribution estimate](../design-engine/mass-reconciliation/current/README.md#provisional-roof-finish-distribution-estimate); distinct from powered-wheel research mass |
| Reference CAD/IFC, BOM, procurement, assembly and control records | [Current export manifest](../design-engine/current/exports/manifest.json) and [delivery package index](../design-engine/coupled-railway/delivery-index.json) |
| City geography, maps and route/service proposals | [Planning guide](../workbench/planning/README.md), [workspace](../workbench/planning/index.html); `./osr plan compile` / `verify`; route-specific engineering remains separate |
| Selected-candidate factory work package | [Current Workbench](../workbench/current/index.html); `./osr twin factory-draft compile` / `verify`; planning draft from the selected Class C ledger |
| Calculated manufacturing and lifecycle scenarios | [Selected 6 km system estimate](../design-engine/current/exports/selected-system-cost.json), [vehicle estimate](../design-engine/current/exports/selected-vehicle-cost.json), [cost and delivery method](../design-engine/model-based-cost-and-delivery.md), and separate pilot ledgers |
| Business and workforce workflows | [ERPNext/Frappe HR](../../deployment/erpnext/README.md); retained integration contracts and native business-platform acceptance scenario, with reviewed conversion required for the new pilot |
| Equipment observation and maintenance review | [FUXA/gateway](../../deployment/supervision/README.md); observations and reviewed maintenance handoffs, without safety movement authority |
| Open control software | [Rust workspace](../../crates/README.md); software tests remain distinct from physical qualification |

The pilot delivery compiler preserves part definitions, engineering revisions,
occurrence patterns and future serial/lot allocation separately. Its
ready-for-planning-review tasks support material/route review and preparation of
supplier information requests. Production, installation, procurement release
and ERP conversion remain held for actual controlled drawings, reviewed native
Item mappings, inspection references and engineering evidence. No accepted
serial installation or approved work order is generated. Its process-hour
ranges are declared capacity hypotheses, not measured cycle times or a second
labour charge on existing direct prices.

The retained factory-draft command creates a six-car work package from a verified
planning handoff and the selected candidate's Class C ledger, under two 8-hour
production shifts. Its schedule represents one serialized lane and does not
infer crews, parallel capacity or dates. It is not an ERPNext import, purchase
order or manufacturing release. The planning handoff itself contains route,
stop, service and OD proposals; vehicle, propulsion, fleet, civil, financial and
performance evaluations remain separate candidate-specific records.

The selected reference ledger retains a 10.090 t/car reference or unlocated
residual. Its separate roof-finish estimate distributes already-accounted
47.809 kg/car over 45.05 m² of source surface; it adds no mass or CAD occurrence.
Those reference-scope figures must not be combined with research-pilot totals.

## Preserved platform and open evidence

The [v0.4 operating/manufacturing release](https://github.com/modernecotech/OpenSourceRail/tree/v0.4.0)
and [v0.5.1 maglev research](https://github.com/modernecotech/OpenSourceRail/tree/v0.5.1)
remain distinct historical foundations. ERPNext/Frappe HR, FUXA/gateway,
revision-controlled assets, city planning, workforce and maintenance are retained
platform capabilities, not replaced by a new mechanical candidate. The
[source-pinned historical manifest](../archives/pre-comfort-default/manifest.json)
records preserved engineering evidence. Historical results do not qualify a new
wheel-supported design.

Calculated outlines can be complete under stated assumptions. Installed
interfaces, actual force/duty and thermal behaviour, independent braking,
structural joints/fatigue, site-specific works, controlled production drawings,
physical prototypes and independent acceptance remain open gates. The new
pilot's drafts do not yet constitute a seamless approved ERPNext project or an
operational commissioning workflow. Software functionality grants no
manufacturing release, physical acceptance or movement authority.
