# Roadmap

This page tracks remaining validation and hardening work after the published
v0.3.1 baseline. It is a planning map, not a release contract.
The open-source CAD, survey, analysis, and simulation selections and the
evidence-producing work packages for the remaining engineering items are in
the [engineering design and simulation plan](engineering-design-simulation-plan.md).

## Reviewed Open Work

The [2026-09-09 substance review](substance-review-2026-09-09.md) now records
completed roof-drainage input/physical-balance repairs and per-site electrical
import/export gates. All seven drainage variants pass the corrected planning
screen. The [ethos audit](ethos-audit-2026-09-09.md) corrects the electrical
interpretation: the reported connection exceedances occur with PV and storage
disabled, while every existing coordinated daylight case meets connection
limits. The repaired gate reports grid-only findings as diagnostics; all 266
solar/storage snapshots pass, with full operating energy validation still open.
Stabling now accepts storage-backed stations without grid import or a 150 kW
minimum, and a grid outage alone does not disable a battery-backed destination.
The four two-day hybrid city replays pass against the repaired code. Historical
station-only experiments remain outside selected-plan package acceptance.
These findings do not prescribe grid upgrades. The depot energy quantity contract is now shared by operating tiers,
layout requirements and the BOM, with all 266 cities reporting PV area,
equipment-cost sensitivity and initial dispatch capacity requirements. Located
equipment, installed-cost reconciliation, physical stabling allocation,
procurement/calendar cashflow, battery renewal and shared factory scheduling
remain open. Distributed station holding, low-C charging and morning restart
now have an executable candidate and passing Samawah holding/restart behavior;
declared reserve roles and every planned departure direction are now checked.
Reference platform comparisons expose unresolved stabling space; verified
track capacity, reserve activation and full-day timetable/energy acceptance
remain open. See the
[station-stabling workflow](operations/distributed-stabling.md).
The charging-reachability gate repairs the six/ten-train overnight stranding
found in Samawah's first continuous replay. Both service cycles pass placement
and morning restart, with all trains at selected powered stations, but the
combined replay now fails the explicit two-train station-capacity gate.
Queues still reach 18 then 19 trains; recurring physical capacity, daytime
headways and outage/recovery duties remain unverified.
The overnight plan now assigns two revenue trains per selected station and the
remaining fleet to storage on its own line. Samawah allocates 40 to stations
and 37/16/15 to Line 1/2/3 storage, separately from workshop bays. The
station-only replay and seven-train redistribution study remain diagnostic
benchmarks. Explicit native home allocations now support same-line depot
returns and morning dispatch, validated across two cycles on a connected
eight-train fixture. Two-day city hybrid screens now pass for Samawah, Uíge, Quelimane and Edéa,
checking actual homes, storage capacity and morning launch stock. Lines operate independently, with no
interline depot connections; physical yard routing and city evening placement
remain subject to verification. The corrected RFC records the emitter's family-specific
fleet assumptions instead of the stale uniform 10% recovery factor.
Gulu, Rahim Yar Khan and Tanta also need their retained charging/grid
overrides represented explicitly in reproducible design inputs.

The 2026-09-08 repository review found no failing committed software, city,
project-twin, link, or browser acceptance baseline. The documentation audit
also reconciled the current rolling-stock product, assembly, tooling, factory,
mass and evidence-package counts; added mechanical and civil workface controls
plus the owner–builder–operator mobilisation plan; regenerated the global index
and reader book; and added checks that make those front-door claims fail when
their machine-readable contracts change.

The following work remains genuinely open and must not be represented as
complete merely by adding documentation:

| Boundary | Remaining evidence | Authoritative register |
|---|---|---|
| City and civil design | The 19 reusable IFC types now have exact accountability across six release packages and nine drawing-definition briefs, separating nine civil-owned types from ten controlled track/station/vehicle interfaces. Shared deployment gates cover field receipts, control, surveyed ground/alignment, route fit, SWMM replay, borehole-zoned foundation selection and an independent OSR/SUMO running-time comparison across every pilot line. Real observations, supplier freezes, first articles, junction-conflict evidence, signed studies, per-span calculations and local approvals remain external. | [Civil type/release register](../design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.md), [drawing briefs](../design/component-catalogue/catalog/buildable-civil/factory-drawings/index.md), [Samawah field brief](../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/field-evidence-brief.md), [alignment](../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/surveyed-alignment-readiness.md), [route fit](../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/route-station-fit-readiness.md), [operations cross-check](../cities/catalogue/west-asia/Iraq/Samawah/engineering/simulation/operations-crosscheck.md), [drainage/ground](../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/drainage-ground-readiness.md) and [civil checklist](civil/deployment-release-checklist.md) |
| Stations | The 45-product/seven-variant FreeCAD and IFC4.3 coordination geometry, BOM/traveler reconciliation and structural, passenger, drainage, thermal and fire screens are present. The failed enclosed depot baselines now have a screened separated/open compound and N+1 cooled-controls response. Supplier/site freeze, surveyed placement, project calculations, drawings, fire strategy, commissioning and approvals remain. | [Station gap register](../design/component-catalogue/catalog/buildable-stations/open-release-gaps.md), [systems evidence](../engineering/analysis/stations/screening-summary.md) and [mitigation work packages](../engineering/analysis/stations/mitigation-work-packages.md) |
| Rolling stock | The 120-product-row/26-assembly IFC and FreeCAD design-reference library, nine solver-backed structural screens, 41 manufacturer/research candidates covering all 56 bought-in rows, 16 factory packages, 29 individual drawing-definition seeds and one executable 13-gate first-article route are present. Drawing ownership and the production-data register now cover all 62 locally made rows, including bogie frames, door/window carriers, battery/HV hardware, configurable ends and trainline harnesses; 472 drawing, material, cut/form/NC, mould, harness, finish and inspection artifact slots remain fail-closed. The mass ledger maps 120/120 rows but correctly leaves 0/117 active rows mass-closed; all 16 drawing packages open and all production-data releases remain open. Supplier configuration freeze, production FEA/drawings, weld/NDT, calibrated mass/CG/axle-load evidence, thermal/HV/fire tests and first articles remain. | [Production-data register](../design/component-catalogue/catalog/buildable-trainset/production-data-release-register.md), [drawing seeds](../design/component-catalogue/catalog/buildable-trainset/factory-drawings/index.md), [factory readiness](../design/component-catalogue/catalog/buildable-trainset/factory-release-readiness.md), [mass closure](../design/component-catalogue/catalog/buildable-trainset/mass-closure-ledger.md), [finish system](../design/component-catalogue/catalog/buildable-trainset/exterior-finish-system.md), [COTS/RFQ candidates](../design/component-catalogue/catalog/buildable-trainset/cots-candidates.md), [public work packages](../design/component-catalogue/catalog/buildable-trainset/first-article-work-packages.md), [execution pack](../design/component-catalogue/catalog/buildable-trainset/first-article-execution-pack.md) and [evidence status](../design/component-catalogue/catalog/buildable-trainset/first-article-evidence-status.md) |
| Control electronics | Exact pilot SKUs, real harness/enclosure/power packs, deployable signed images, bench evidence, and KiCad fabrication data where a custom board is selected | [Control-electronics release checklist](../control-electronics/release-checklist.md) |
| Software and operations | Ops Core now has local authenticated RBAC, managed evidence/documents, server attestations and verified backup archives. Production TLS/SSO/MFA, hosted secret/backup operations, signed live train actions, production transports, HIL and operator validation remain. | [Operations Portal](operations-portal/README.md), [certification](certification/README.md) and [operations validation](operations/validation-checklist.md) |
| Approval | Supplier qualification, physical tests, independent safety assessment and national/operator authorization | [Safety case](safety-case/README.md) and [certification](certification/README.md) |

The rolling-stock packages now link to ten [manufacturing and assembly
controls](../design/component-catalogue/catalog/buildable-trainset/manufacturing-and-assembly-controls.md),
and the civil packages link to ten [fabrication and construction
controls](../design/component-catalogue/catalog/buildable-civil/fabrication-and-construction-controls.md).
These fill ordinary work-sequence, inspection, handling and handback gaps. The
linked inspection plans now expose 416 LM3 and 114 civil package characteristics
as explicit hold, witness or review points. They do not close the supplier,
drawing, calculation, site or authority evidence in the table. Blank mechanical
and civil execution records prevent planned checks
from being mistaken for performed work. The [owner–builder–operator
plan](owner-builder-operator-setup.md) and its [fail-closed mobilisation
status](owner-builder-operator-mobilisation-status.md) assign an institutional
route for closing those gaps.

Repository work that can advance without external evidence remains visible in
the analysis register and workstream table: charger duty, station analyses,
passenger assignment/pedestrian capacity, native IFC viewing, and LandXML
station/civil/cant sidecar mapping. The review closed the previously planned
CalculiX thermal-block solver benchmark with a deterministic input, analytical
acceptance check, and machine-readable result. These tasks improve screening
evidence but cannot close the external release gates above.

## v0.3 Workstream

| Workstream | Target outcome |
|---|---|
| Documentation accessibility | One root front door and source registry are enforced; local READMEs retain only discipline/city evidence, with generated inventory and link/drift checks |
| Owner–builder–operator institution | Establish the public owner, ring-fenced delivery/operator company, independent assurance, accountable executives, competence pipeline, management systems and gated move from development to revenue service |
| Rolling-stock detail package | Close the 16 factory packages and 117 active mass rows with supplier-exact envelopes, production solids/masses, weld maps, tolerance stacks, harness clamp locations, FEA-ready brackets, 2D drawings, NC/flat-pattern outputs and calibrated weight/balance evidence |
| Mechanical CAD | The candidate layer and generated FreeCAD/IFC review geometry are implemented; next closure is supplier-returned exact configurations, mass/envelopes, released drawings and production CAD/NC data |
| Control-electronics integration evidence | Pilot-ready COTS/DIY integration packs for T-ECU/S, T-ECU/A, T-OBS, W-SBC, and S-SBC: exact SKUs, wiring/harness maps, connector maps, enclosure/mounting notes, power/thermal margins, SD-card images, self-test logs, and bench records |
| Custom-board release artifacts | KiCad capture, gerbers, board BOMs, DFM review, and assembly drawings only for deployments that choose OSR-specific carrier, power, safety-I/O, or sensor-interface boards |
| DIY deployment path | Prebuilt SD-card images, checksums, role-specific self-test evidence, and first external build feedback |
| Software integration | Workbench context plus onboard, station, intrusion and T2G-to-depot CBM/historian/analytics software-in-loop are implemented; signed live actions, production transports, asset-specific points/crossing/fare-gate harnesses, HIL, and authenticated live GUI paths remain |
| City Studio | Git-backed city projects, source locks, layered offline GIS editing, complete manual line/station/alignment authoring, semantic revision comparison including BCF, OD demand, per-line IFC survey control and revision-locked field-to-structural-release gates, plus controlled engineering jobs, verified viewers and 144-check Playwright browser/restart persistence acceptance (implemented); received field data, native tessellated IFC streaming, passenger assignment and platform/interchange pedestrian capacity next |
| Certification evidence | Tool-backed/assessor-accepted consensus refinement, qualified safety-controller freeze, residual-risk narrative, independent-assessor review notes, first-article field-evidence plan, and traceability updates |
| Civil/station package | Close the six civil release packages with survey-grade alignments, ground models, supplier data, per-span checks, reinforcement/prestress, first articles and signed deployment releases; close the station packages against surveyed placement and project evidence |

Open release gates for certification, hardware, rolling stock,
civil/station, and operations are tracked in the relevant section
checklists rather than left as implicit TODOs.

## v0.3 Definition Of Done

- All top-level domains have local READMEs and current status notes.
- `python3 tools/automation/repo-health.py --quiet` passes on the release tree.
- Rolling-stock documentation links to the current FreeCAD/PNG/COTS
  package and clearly separates envelope CAD from production drawings.
- Hardware host classes have either pilot-ready COTS/DIY integration
  packs or explicit custom-board KiCad/gerber/BOM gaps where custom
  boards are actually required.
- Certification and safety-case pages identify remaining external
  evidence rather than implying it already exists.
