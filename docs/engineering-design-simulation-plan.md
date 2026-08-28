# Engineering Design And Simulation Plan

Status: implementation plan  
Reviewed: 2026-08-26
Scope: remaining repository audit items COMP-014 and COMP-016 through
COMP-019

This plan selects an open-source engineering toolchain and turns the
remaining mechanical, station, civil, energy, and system-validation gaps
into evidence-producing work packages. It does not treat a solver result as
design approval: survey data, supplier data, applicable-code checks, and
competent local engineering review remain release inputs.

## Decision

No single application should own the whole design. The repository keeps the
following authority boundaries:

| Design information | Authority | Review or analysis handoff |
|---|---|---|
| Parametric rolling-stock, component, station, and civil-kit geometry | `mechanical-py/src/osr_mech/` | Native FreeCAD `.FCStd`, STEP, drawings, solver meshes |
| Surveyed route, levels, control, parcels, utilities, and terrain | Deployment GeoPackage in QGIS; approved OSR-ALN for railway alignment | LandXML, GeoJSON, GeoTIFF, LAS/LAZ/E57 |
| Product structure, quantities, and assembly sequence | Generated repository BOMs, travelers, and assembly documents | IFC property sets and drawing schedules reference stable OSR part IDs |
| Operational behavior and measured duty cycle | OSR Rust simulator and logged field evidence | CSV/Parquet or versioned JSON input decks for specialist tools |
| Federated station/civil coordination model | IFC4.3 export checked with IfcOpenShell and reviewed in Bonsai | BCF/IDS findings, quantities, drawings, and 4D task-product links |
| Analysis evidence | Versioned input deck, assumptions, solver/version, convergence log, and reviewed summary | Results are evidence, never a replacement for canonical geometry or requirements |

FreeCAD therefore remains the primary CAD and first-pass FEA environment.
QGIS remains the primary geospatial and alignment-review environment. The
FreeCAD Road/Trails family may be evaluated for visual coordination, but it
must not become the surveyed alignment authority until an OSR-ALN round-trip
benchmark passes without station, curve, level, cant, or CRS loss.
Bonsai is the civil federation, detail-review, quantity, and 4D construction
environment, not the route-design authority. The implemented
[Bonsai/IFC4.3 workflow](civil/bonsai-ifc-workflow.md) carries stable OSR IDs,
checked review geometry, an `IfcAlignment` reference, and construction tasks
without duplicating alignment or structural design rules inside Blender.

## Selected Open-Source Toolchain

The “baseline” tools should receive reproducible runners and benchmark cases.
“Conditional” tools are introduced only when their listed question cannot be
answered adequately by the baseline. “Evaluation” tools must pass a small
interchange trial before project data is committed to them.

| Work area | Selection | Class | Intended use and boundary |
|---|---|---:|---|
| Parametric CAD, assemblies, drawings | [FreeCAD](https://www.freecad.org/) | Baseline | Mechanical and station geometry, Assembly/Part Design/TechDraw, IFC/STEP handoff; the installed Flatpak is currently 1.1.3 |
| First-pass structural and thermal FEA | [FreeCAD FEM](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FEM_Workbench.md), CalculiX, and Gmsh | Baseline | Repeatable component, frame, bracket, platform, and catalogue-structure screening; FreeCAD calls external meshers/solvers, so each evidence pack records all three versions |
| Survey/GIS/alignment review | [QGIS](https://docs.qgis.org/latest/en/docs/user_manual/) and GDAL | Baseline | Control, terrain, parcels, utilities, flood layers, station siting, CRS control, and LandXML/OSR-ALN review |
| GNSS processing | [RTKLIB](https://github.com/tomojitakasu/RTKLIB) | Baseline when field data arrives | Static/kinematic GNSS processing and reproducible control reports; a licensed surveyor owns control acceptance |
| Photogrammetry and point clouds | [OpenDroneMap](https://opendronemap.org/docs/) and [CloudCompare](https://www.cloudcompare.org/doc/) | Baseline when field data arrives | Orthophoto/DEM generation, registration, cleaning, cross-sections, and clearance comparison; raw captures stay outside Git |
| IFC federation and checking | [IfcOpenShell/Bonsai](https://docs.ifcopenshell.org/) | Baseline | IFC4.3 rail hierarchy, deterministic civil geometry, stable OSR IDs, quantities, BCF/IDS coordination and 4D sequencing; IFC is a coordination artifact rather than a second geometry or alignment authority |
| Drainage and station runoff | [EPA SWMM](https://www.epa.gov/water-research/storm-water-management-model-swmm) | Baseline | Design-storm runoff, inlet/channel/pipe/storage routing, surcharge, and station/depot drainage scenarios |
| Global structures and soil-structure response | [OpenSees](https://opensees.github.io/OpenSeesDocumentation/) | Baseline for COMP-017 structures | Per-span frame response, bearings, pier families, nonlinear/seismic cases, and soil springs using local design inputs |
| Detailed nonlinear structural cross-check | [Code_Aster](https://code-aster.org/doc/default/en/index.php) | Conditional | Concrete, contact, fatigue, or thermomechanical cases that exceed the verified CalculiX template; use on a benchmark before project models |
| Groundwater and coupled ground response | [OpenGeoSys](https://www.opengeosys.org/stable/) | Conditional | Settlement/groundwater/thermal-hydraulic questions supported by boreholes and laboratory parameters; it does not replace a ground investigation |
| Passenger movement and egress | [JuPedSim](https://github.com/PedestrianDynamics/jupedsim) | Baseline | Normal, degraded, interchange, and evacuation pedestrian scenarios using demand ranges and measured/calibrated flow assumptions |
| Fire and smoke | [NIST FDS and Smokeview](https://pages.nist.gov/fds-smv/) | Baseline for enclosed/high-risk spaces | Smoke, heat, tenability, battery-room and station fire scenarios; use JuPedSim separately for egress because FDS+Evac is no longer the selected workflow |
| Building energy and HVAC | [EnergyPlus](https://energyplus.net/) | Baseline | Station/depot loads, envelope, ventilation and HVAC energy; detailed CFD is added only when a lumped model cannot answer the design question |
| Battery electrochemistry, heat, and degradation | [PyBaMM](https://docs.pybamm.org/en/stable/) | Baseline after supplier data | Reproduce the selected LFP cell against supplier/lab curves, then apply measured OSR duty and high-ambient cases; a generic lithium-ion parameter set must not stand in for the selected cell |
| Solar yield | [pvlib-python](https://github.com/pvlib/pvlib-python) | Baseline | Site-specific plane-of-array yield, temperature derating, inverter clipping, and uncertainty cases |
| Site/depot electrical network | [pandapower](https://www.pandapower.org/) | Baseline | Load flow, voltage drop, transformer/cable loading, fault-level screening, charger coincidence, PV and storage scenarios |
| Rail operations and multimodal interaction | [Eclipse SUMO](https://eclipse.dev/sumo/) | Baseline independent check | Timetable, junction, road interaction, feeder and pedestrian-demand sensitivity; OSR simulator remains authoritative for OSR control behavior |
| Railway timetable/capacity design | [OSRD](https://osrd.fr/en/) | Evaluation | Trial import of one Samawah line for running-time, conflict, capacity, and timetable comparison; adopt only after data round-trip and maintainability review |
| Commercial railway timetable/capacity cross-check | [OpenTrack](https://www.opentrack.ch/opentrack/opentrack_e/opentrack_e.html) | Optional licensed evaluation | Do not replace SUMO or `osr-sim`; after lawful procurement, trial Samawah Line 1 for running time, block occupation, minimum headway and seeded robustness per the [OpenTrack evaluation](opentrack-evaluation.md) |
| Vehicle multibody dynamics | [Project Chrono](https://projectchrono.org/) | Evaluation/conditional | Suspension, articulation and component motion studies; rail wheel/contact behavior requires an OSR benchmark and is not available merely by importing the CAD model |

The current workstation has the adopted baseline installed through isolated
Flatpaks, a pinned Python environment, and versioned user-local native
releases. Exact commits, versions, licenses, source URLs and checksums are in
[`engineering/toolchain/tool-manifest.toml`](../engineering/toolchain/tool-manifest.toml).
OpenDroneMap remains gated on survey mobilisation; the conditional/evaluation
solvers remain uninstalled until their adoption gate identifies a concrete
design question.

## Common Evidence Contract

Every analysis package must contain, either directly or through a generated
manifest:

1. the requirement, hazard, drawing, assembly, BOM, and OSR part IDs being
   checked;
2. canonical source revision and input checksums;
3. tool, solver, mesher, plug-in, and operating-environment versions;
4. units, coordinate reference system, material/supplier data, loads,
   boundary conditions, uncertainties, and exclusions;
5. mesh/time-step/sensitivity study appropriate to the model;
6. convergence and warning logs, plus a hand calculation or published
   benchmark before a new solver family is trusted;
7. acceptance criterion, result, margin, reviewer, date, and disposition;
8. a compact tracked summary and input deck. Large raw captures, caches, and
   disposable result fields follow `repository-artifact-policy.md` and stay
   out of Git unless explicitly accepted as evidence.

Neutral interchange is limited deliberately:

| Exchange | Required content |
|---|---|
| OSR-ALN/LandXML | horizontal and vertical geometry, cant, station IDs, CRS/vertical datum, source hash |
| GeoPackage | control, alignment, stations, utilities, property, flood, boreholes, issues, provenance |
| IFC 4.x | stable OSR part/assembly IDs, placement, classification, status, material, drawing/BOM references |
| STEP | geometry handoff only; never trusted for requirements, material, fastener, or revision metadata |
| Analysis input deck | human-reviewable parameters and stable references back to canonical source |
| Results summary | machine-readable values plus a concise reviewed Markdown report |

## Execution Plan

### Wave 0 — Reproducible tool and interchange baseline

- [x] **ENG-TOOL-001 — Create the environment manifest.** Pin FreeCAD,
  CalculiX, Gmsh, QGIS/GDAL, Python libraries, and each adopted solver. Add
  license, download source, checksum/container or package reference, and a
  command that prints the installed version.
- [ ] **ENG-TOOL-002 — Add repository runners.** Provide scripts that place
  generated work under `build/engineering/`, refuse missing inputs, capture
  versions/logs, and write atomic summaries. Do not require GUI state for a
  reproducible analysis.
- [ ] **ENG-TOOL-003 — Add solver benchmarks.** Start with a cantilever,
  thermal block, simple drainage network, one-zone energy model, four-bus
  electrical network, corridor evacuation, and one-line timetable. Compare
  analytical or published answers and set tolerances.
- [ ] **ENG-TOOL-004 — Add interchange drift tests.** Check OSR-ALN ↔
  LandXML/QGIS, OSR part IDs ↔ IFC, CAD geometry ↔ analysis mesh, and
  measured-duty export ↔ PyBaMM/pandapower/SUMO inputs.
- [x] **ENG-TOOL-005 — Add an analysis register.** Record model status as
  planned, screening, calibrated, independently checked, or accepted. Reject
  unlabelled screenshots and unconverged output as closure evidence.

Implementation status on 2026-08-11: ENG-TOOL-001 and ENG-TOOL-005 are
closed. The repository runner captures exact versions/hashes and exercises
IFC creation, an analytical OpenSees case, pandapower, pvlib, PyBaMM, SWMM,
EnergyPlus and FDS. It also runs a deterministic JuPedSim station corridor and
a 12-service SUMO timetable generated from all three canonical Samawah lines.
The generalized batch runner has now generated decks and
station/product mappings for all 266 catalogue cities: 1,022 lines and 14,636
station occurrences, backed by seven shared station-archetype IFC skeletons.
The full live SUMO batch completed all 4,052 scheduled screening services with
zero simulation failures. Its execution gate passes; its input-quality gate
remains open for the endpoint findings below. ENG-TOOL-002/003 remain open for
the thermal block, the remaining analytical benchmark forms, atomic manifests
for every solver and second-machine reproduction. ENG-TOOL-004 now passes station manifest ID,
property-set and assembly-hierarchy round trips for standard and
interchange-elevated IFC coordination skeletons; geometry/mesh and alignment
drift tests remain open.

The civil federation now generates a byte-deterministic IFC4.3 model with 95
stable assets, 17 source-recipe component types, three source-backed material
families covering 46 occurrences, one native 60E1 profile driving 32 rail
extrusions, 15 hash-locked native source documents associated to all assets,
one internal classification with 11 references covering all 95 assets, four `IfcRailwayPart`
disciplines, five native coordination groups and four native presentation
layers covering all assets exactly once,
an `IfcAlignment` with native horizontal/vertical planning segments,
gradient-curve representation and stationing, 18 construction tasks, task-product
links, native quantities, provenance, and nine passing checks exposed as native
qualitative interface constraints. Thirteen project-declared property/quantity
dictionaries expose 77 typed fields without misusing the reserved `Pset_`
prefix. Its thirteen-specification IDS 1.0 contract passes 1,602/1,602 checks;
deterministic BCF
3.0 topics retain object links and Git-reviewed decisions. Bonsai 0.8.5 imports
the model headlessly and saves the review/animation scene. Survey-grade
alignment design and engineer-released structural detail remain open.

The city package now also converts canonical catalogue inputs into QGIS/GDAL
GeoPackages, shapes SUMO edges from the corridor GeoJSON, and runs per-city
pandapower/pvlib electrical and PV screens. Samawah is the acceptance case and
Songea is the second-city portability check. Samawah's mapped chainage differs
from corridor geometry by roughly 2–4% on Lines 1–2 and has a maximum
station-to-corridor offset of about 92 m; these remain explicit coordination
findings pending survey-grade alignment. Its peak grid-only case overloads 14
planning transformers, while the coordinated daylight case converges without
loading or voltage-band findings. Neither the mapping nor the energy result is
survey, utility, or measured-weather acceptance evidence.
The Samawah scenario ambient is also 16 °C above the selected
`temperate-continental` preset average; this is now a structured climate-input
review finding rather than an implicit override.

The compact catalogue still contains inherited layouts emitted by older
generator revisions. Catalogue-wide ring/interchange and station-cluster
reports keep that migration backlog explicit. The current generator itself
now fails closed on sub-600 m same-line spacing, ungrouped cross-line near
misses, incomplete interchange complexes, and ring/radial approaches without
a shared transfer before emitting a design. Batch regeneration therefore
cannot create a new package with those layout defects; the retained compact
snapshots must be migrated progressively and the reports refreshed after each
batch. The catalogue-wide result cannot be marked input-quality-passed until
their canonical alignments or station extents are
corrected.

Exit: one deterministic benchmark per adopted baseline tool, a clean
re-run on a second machine, and no loss of units, CRS, stable IDs, or source
revision through the interchange tests.

### Wave 1 — COMP-016 station variants and assembly reconciliation

- [ ] **COMP-016-01 — Freeze the station variation matrix.** Compare standard,
  halt, major, interchange, interchange-elevated, terminal, and depot
  interfaces. Mark every envelope, service, access, compliance, structure,
  equipment, and assembly field as shared, parameterized, or unique.
- [ ] **COMP-016-02 — Generate all FreeCAD envelopes.** Add assembled and
  exploded review states, interfaces to track/train/PSD/edge protection,
  maintainability clearances, lifting/installation zones, and controlled
  datums for every unique variant.
- [ ] **COMP-016-03 — Complete variant documentation.** Produce the missing
  envelope, services, accessibility, compliance, drawing-register, and
  assembly pages. A parameter-only variant must identify the governing
  standard artifact and its complete parameter delta.
- [ ] **COMP-016-04 — Reconcile product structure.** Make each FreeCAD object,
  BOM row, drawing-register item, traveler step, fastener set, and assembly
  instruction resolve to the same stable part or assembly ID. Add a CI
  orphan check in both directions.
- [ ] **COMP-016-05 — Federate and check IFC.** Export one standard and one
  interchange-elevated station, validate OSR IDs/property sets with
  IfcOpenShell, and issue BCF findings for geometry or ownership conflicts.
  Product-structure skeletons now round-trip every manifest part/assembly ID,
  OSR property set and assembly relationship; geometry placement, IDS rules
  and BCF conflict issue generation remain open, so this task is not closed.
- [ ] **COMP-016-06 — Run station analyses.** Use FreeCAD/CalculiX or OpenSees
  for selected structures, JuPedSim for normal/degraded/egress flows,
  EnergyPlus for heat/ventilation/load, SWMM for drainage, and FDS for
  enclosed or battery/charger fire scenarios.
- [ ] **COMP-016-07 — Release the package.** Close interface clashes, drawing
  and BOM drift, unmet accessibility/egress criteria, and open structural
  checks; record local-code items awaiting deployment evidence.

Exit: every station variant is either a controlled parameter delta or has a
complete unique package, with zero orphan CAD/BOM/drawing/assembly IDs.

### Wave 2 — COMP-017 surveyed Samawah pilot and civil checks

- [ ] **COMP-017-01 — Issue the field evidence brief.** Define control,
  accuracy, CRS/vertical datum, utility classes, property checks, flood
  evidence, boreholes/tests, workshop/fleet audit, photography/scan coverage,
  data ownership, and acceptance before mobilization.
- [ ] **COMP-017-02 — Process and accept control.** Process GNSS observations
  with RTKLIB, retain raw and processing reports in controlled project
  storage, and have the deployment survey authority accept the network.
- [ ] **COMP-017-03 — Build the surveyed ground model.** Use QGIS, ODM and
  CloudCompare to register terrain/point clouds and create the master
  GeoPackage. Record residuals, voids, epochs, vertical datum, and uncertainty.
- [ ] **COMP-017-04 — Confirm or replace all three alignments.** Fit survey-
  grade horizontal/vertical geometry and cant, verify platform/yard/turnout
  interfaces, export OSR-ALN, and pass hard gates plus a LandXML round trip.
- [ ] **COMP-017-05 — Confirm route and station fit.** Resolve utilities,
  property, flood level, access, intercity-station/yard integration, road
  interaction, construction compounds, lifting paths, and possession/staging.
- [ ] **COMP-017-06 — Complete drainage and ground design.** Run SWMM with
  accepted storms and levels; size ground/foundation variants from borehole
  evidence. Use OpenGeoSys only where groundwater/coupled behavior warrants it.
- [ ] **COMP-017-07 — Complete per-span structural checks.** Instantiate the
  actual span/pier/abutment/foundation schedule. Use OpenSees for global,
  seismic and soil-spring cases and verified FreeCAD/CalculiX templates for
  component checks; use Code_Aster only for identified nonlinear/detail cases.
- [ ] **COMP-017-08 — Cross-check operations.** Compare OSR running times and
  junction occupancy with SUMO. Trial one-line OSRD import separately. An
  OpenTrack comparison is optional and licensed, following
  [`opentrack-evaluation.md`](opentrack-evaluation.md); neither evaluated tool
  can become a release dependency until interchange and repeatability pass.
  The first screening SUMO deck now derives Line 1 length and all 13 station
  IDs/chainages from `design.toml` and completes four opposed services. The OSR
  simulator comparison, surveyed geometry, calibrated dwell, junction/road
  interactions and OSRD evaluation remain open.
- [ ] **COMP-017-09 — Obtain deployment sign-off.** Close the civil checklist
  for survey alignment, ground, structures, station fit, energy site, permits,
  stakeholders, and constructability. Keep every unreceived external item open.

Exit: signed survey and ground inputs, approved three-line OSR-ALN package,
site-fitted station/yard schedule, drainage model, per-span calculation
register, constructability plan, and named external approvals.

### Wave 3 — COMP-018 battery, charging, and site energy

RFC 0021 fixes the planning architecture for this wave: 675/540 kWh gross/
usable LFP split into three 225 kWh car packs, a 650–700 V nominal DC link,
six PMSM/controller sets, one shared 500 kW station cabinet, and stationary
storage in repeated 500 kWh LFP modules. “Freeze” below means qualify the
supplier implementation and close the provisional limits; it does not reopen
the selected architecture or introduce a second voltage or charger tier.

- [ ] **COMP-018-01 — Freeze chemistry and supplier evidence.** Select actual
  cells/modules/BMS/charger and obtain dimensions, mass, electrical limits,
  temperature limits, cycle/calendar data, propagation evidence, warranties,
  communication details, and change control.
- [ ] **COMP-018-02 — Export measured duty.** Define a versioned duty-cycle
  schema and collect representative traction, auxiliary, dwell/charge,
  ambient, passenger-load, degraded-operation, and ageing cases. Planning
  defaults remain sensitivity inputs, not the acceptance case.
- [ ] **COMP-018-03 — Calibrate the battery model.** Reproduce supplier/lab
  curves in PyBaMM, document whether the chosen chemistry is supported, fit
  parameters without hiding uncertainty, and validate against independent
  test data before applying line duty.
- [ ] **COMP-018-04 — Close pack and charger thermal design.** Use the
  FreeCAD geometry plus verified thermal models for normal, hot-soak,
  fast-charge, cooling fault and degraded cases. Confirm temperatures,
  derating, ventilation, enclosure clearances, sensing and maintainability.
- [ ] **COMP-018-05 — Complete fire/venting evidence.** Define cell-to-pack
  test evidence and use FDS for site enclosure smoke/heat/ventilation and
  separation questions. Obtain fire-authority review; simulation alone does
  not establish propagation safety.
- [ ] **COMP-018-06 — Size solar and grid connection.** Use pvlib with accepted
  weather/soiling/temperature data and pandapower for charger coincidence,
  transformer/cable loading, voltage, faults, storage and degraded-grid cases.
  Use EnergyPlus for station/depot building loads and ventilation energy.
- [ ] **COMP-018-07 — Release the connector package.** Complete the mating
  geometry, tolerance stack, keying, touch protection, earthing, interlock,
  communications, thermal/current tests, insertion-cycle test, inspection,
  replacement and assembly instructions; reconcile all BOM and ICD IDs.
- [ ] **COMP-018-08 — Obtain utility and authority evidence.** Record the
  accepted grid study, metering/protection settings, solar permissions,
  emergency isolation, fire/ventilation approval, and operating constraints.
- [ ] **COMP-018-09 — Close traction and DC-link compatibility.** Select the
  cell/string count, normal top voltage and transient margin; prove contactor,
  precharge, HVIL, IMD, creepage/clearance and fault interruption; then derive
  gearbox ratio and validate AW0–AW3 acceleration, grade, wet adhesion,
  overspeed, regen and repeated-stop duty at 50 °C. Retain the 1.8 MW control
  cap until this closes.
- [ ] **COMP-018-10 — Close shared-cabinet service scenarios.** Verify two-
  contact arbitration, 825 A and 500 kW limits, conversion/contact losses,
  high-ambient derating, 60-second stops, longer terminal dwell, low-solar,
  weak-grid, charger outage and minimum route SOC. Promote station storage
  only in integer 500 kWh modules when the model demonstrates need.
- [ ] **COMP-018-11 — Close staged fire response.** Qualify temperature/off-
  gas detection, string/pack isolation topology, outward vents, propagation
  barriers and per-car mist flow/pressure. Exercise failed reservoir/pump/
  nozzle/sensor cases and prove the controlled-safe-platform versus emergency-
  brake decision with evacuation and fire-service review.

Exit: supplier-frozen pack and charger, calibrated duty/thermal/degradation
evidence, site-specific yield and network studies, released connector/assembly
package, and external utility/fire decisions.

### Wave 4 — COMP-019 component RFC implementation packages

- [ ] **COMP-019-01 — RFC 0023 doors.** Create shall-requirements, body/door
  ICD, hazard links, tolerance and kinematic model, FreeCAD assembly,
  actuator/sensor/edge BOM, manual release, obstruction/degraded tests,
  endurance plan, assembly traveler, and acceptance matrix. Use Project
  Chrono only if the simple kinematic/contact model cannot answer a named risk.
- [ ] **COMP-019-02 — RFC 0024 battery thermal.** Reference the frozen
  COMP-018 configuration; add thermal-control requirements, sensor/duct/
  enclosure ICDs, limits, fault response, test fixtures and pass/fail matrix.
- [ ] **COMP-019-03 — RFC 0025 points.** Complete rail/blade/stock-rail,
  stretcher, actuator, locking/detection, drainage and maintainability ICDs;
  reconcile the FreeCAD kit, BOM and assembly traveler; add force, wear,
  obstruction, water/dust, manual-operation and endurance tests.
- [ ] **COMP-019-04 — RFC 0026 charging connector.** Promote the released
  COMP-018 connector configuration into normative requirements, electrical/
  mechanical/control ICDs, manufacturing package and traceable acceptance.
- [ ] **COMP-019-05 — RFC 0027 brownfield recovery.** Define the survey and
  condition-grading schema, QGIS/point-cloud workflow, material/test coupons,
  reuse/rework/reject decision rules, chain of custody, resulting BOM status,
  and verification after recovery.
- [ ] **COMP-019-06 — Enforce RFC completeness.** Add a repository check that
  each promoted RFC names its requirements, ICDs, hazards, part/BOM IDs,
  drawings, assembly steps, analysis/test evidence, unresolved assumptions,
  owner and acceptance status.

Exit: RFCs 0023–0027 are traceable implementation or procurement packages,
not architecture/cost sketches.

### Parallel software-assurance track — COMP-014

- [ ] **COMP-014-01 — Build a deterministic fault harness.** Reuse the Rust
  integration stack and add controllable process kill/restart, node loss,
  network delay/loss/partition/heal, clock offset, disk-full, corrupt config,
  and telemetry-loss adapters. Prefer Linux `tc netem`, constrained filesystems
  and in-process fault points over a new orchestration platform initially.
- [ ] **COMP-014-02 — Specify recovery invariants.** Define safe state,
  consensus non-overlap, durable state, event continuity, bounded recovery,
  alarm visibility, configuration rejection, and rollback criteria before
  running long tests.
- [ ] **COMP-014-03 — Add restart and corruption tests.** Cover clean and
  unclean restart at each persistence boundary, partial writes, stale state,
  incompatible/corrupted configuration and upgrade/rollback.
- [ ] **COMP-014-04 — Add partition and clock tests.** Exercise minority/
  majority isolation, asymmetric loss, healing, jitter, clock step/slew and
  loss of time source while checking the invariants.
- [ ] **COMP-014-05 — Add multi-day soak profiles.** Run normal, peak,
  degraded and recovery cycles with bounded resource-growth assertions and
  deterministic seeds. Keep a short CI profile and schedule the full profile.
- [ ] **COMP-014-06 — Publish safety evidence.** Store scenario manifests,
  exact revisions/seeds, summarized timelines, invariant results and failure
  triage; link accepted evidence into the safety-case register.

Exit: every requested fault has a repeatable scenario, all recovery invariants
are machine-checked, the full-duration run meets resource/recovery limits, and
the safety case points to reviewable evidence.

## Priority And Dependencies

| Priority | Work that can start now | Dependency that prevents closure |
|---:|---|---|
| 1 | ENG-TOOL-001 through 005; COMP-016 variation/product-structure work; COMP-014 harness | Second-machine reproduction for tool baseline |
| 2 | Field brief, data schemas, QGIS project template, SWMM/OpenSees benchmarks | Samawah survey partner, permissions, control and geotechnical campaign |
| 3 | Station analysis templates and preliminary energy schemas | Accepted passenger demand, local code, fire scenarios, utility and weather data |
| 4 | Supplier-neutral connector/door/points ICD and test templates | Selected cells, charger, actuators, connectors and supplier evidence |
| 5 | Site-calibrated civil and energy analysis, final assembly/BOM release | Survey, measured duty, supplier freeze, local authority and independent review |

The immediate critical path is therefore Wave 0 plus the COMP-017 field brief.
Station variants and the COMP-014 fault harness can proceed in parallel while
external survey and supplier data are being obtained. Final geometry, BOM,
assembly instructions, and acceptance evidence are reconciled only after the
relevant surveyed or supplier configuration is frozen.

## Software Adoption Gates

A tool moves from evaluation to baseline only when all of the following pass:

- open-source license and redistributable dependencies are recorded;
- a maintained release/source and a reproducible installation path exist;
- command-line or scripted execution can capture the full configuration;
- the OSR benchmark meets a documented tolerance;
- input/output can be reviewed without a proprietary application;
- stable OSR part, station, alignment, requirement, and evidence IDs survive;
- failure, warning, convergence, and unit/CRS errors cause a non-zero check;
- a named maintainer owns updates and replacement/migration.

These gates deliberately leave FreeCAD Road/Trails, OSRD, Project Chrono,
Code_Aster, and OpenGeoSys conditional until they answer a concrete design
question and pass an OSR benchmark. This keeps the core toolchain small while
preserving open routes for advanced analysis.
