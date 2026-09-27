# Topography redesign, BIM and mechanical detail register

This generated register says what the new terrain/water evidence changes, what remains
provisional, and what information must be closed before design or fabrication release.

> Design-reference coordination data only. Open DEM and water data are screening evidence, not survey, geotechnical, hydraulic or navigation evidence. Candidate dimensions, loads and tolerances are not fabrication or construction release values until their stated closure evidence is accepted by the competent design authority.

## Redesign decision

Changed now: alignment/civil disposition; bridge/viaduct need; station siting/configuration; route compatibility evidence; BIM information requirements.

Not automatically changed: LM3 three-car architecture; car length/width concept; battery/traction topology; bogie and articulation concept.

A vehicle parameter changes only after a route-compatibility gate fails and a controlled whole-system trade study accepts that change.

## Delivery plan and completed implementation

1. Classify terrain/water evidence and trace each trigger to affected design domains.
2. Define BIM objects, information, relations and acceptance checks for each asset type.
3. Establish the LM3 datum hierarchy, mechanical ICDs, load cases and route gates.
4. Publish the register into IFC property sets and the model-coverage report.
5. Enforce ID integrity, source traceability, deterministic output and IFC round-trip tests.

All five steps are implemented in the repository; engineering evidence remains open where
the status below says supplier, survey, calculation, test or authority acceptance is required.

## Design impacts

| ID | Disposition | Trigger | Domains |
|---|---|---|---|
| `OSR-IMP-TOPO-001` | `redesign-required` | terrain elevation or slope changes the feasible vertical alignment | alignment, earthworks, drainage, structures, traction-energy |
| `OSR-IMP-WATER-002` | `bridge-or-reroute-required` | route intersects mapped water or its hydraulic/flood influence zone | alignment, bridge, hydrology, environment, operations |
| `OSR-IMP-STRUCT-003` | `asset-family-and-site-design-required` | planner selects viaduct, bridge, retained or transition civil class | substructure, superstructure, track, egress, maintenance |
| `OSR-IMP-STN-004` | `station-configuration-redesign-required` | terrain, water, structure or access evidence moves or elevates a station | platform, accessibility, fire-life-safety, MEP, urban-interface |
| `OSR-IMP-LM3-005` | `compatibility-requalification-before-vehicle-redesign` | released route profile, structures or platforms differ from the vehicle design basis | rolling-stock, wheel-rail, traction, braking, energy, evacuation |
| `OSR-IMP-DEPOT-006` | `site-layout-revalidation-required` | topography or alignment changes depot access, stabling or recovery routes | depot, maintenance, logistics, energy, recovery |

## BIM information requirements

### corridor-and-alignment

- Objects: alignment, profile, terrain, water, civil-class segment, exclusion volume
- Information: CRS and vertical datum, chainage, source/license/date/resolution, confidence, civil disposition, design status
- Relations: segment-to-source-cell, segment-to-structure, station-to-exclusion, alignment-to-revision
- Acceptance: georeference round-trip; no station intersects exclusion volume; every route segment has exactly one civil disposition

### bridge-and-viaduct

- Objects: foundation, pier/abutment, bearing, deck/span, trackform, walkway, parapet, drainage, movement joint
- Information: span/skew/curvature, datum and reactions, load model, movement range, exposure, inspection zone, calculation/evidence IDs
- Relations: foundation-to-ground-model, bearing-to-movement-unit, track-to-deck, asset-to-work-package
- Acceptance: reaction and movement closure; kinematic/egress clash check; constructability and access review

### station

- Objects: platform edge, track, access route, lift/stair, canopy, MEP/fire/charging equipment, drainage, foundation
- Information: platform gap/step basis, accessible route, occupancy/egress, asset tags, maintainer, inspection and replacement clearances
- Relations: platform-to-track, equipment-to-system, space-to-egress route, station-to-catchment
- Acceptance: gap/step analysis; inclusive-access and flow check; MEP/structure clash review; no unresolved terrain/water exclusion

### rolling-stock

- Objects: carbody, bogie, wheelset, door, articulation, coupler, battery, traction, brake, HVAC, service/removal envelope
- Information: product ID, configuration, mass/CG status, datum, interface/load/tolerance status, material/process, verification evidence
- Relations: product-to-parent assembly, product-to-interface, interface-to-datum, product-to-analysis/evidence
- Acceptance: complete controlled product graph; interface and datum coverage; route compatibility closure; configuration-specific release boundary

### manufacturing-resource

- Objects: fixture, gauge, mould, tool, work centre, inspection zone
- Information: tool ID, controlled product/interface, calibration, capacity, revision, release status
- Relations: tool-to-process, gauge-to-datum/interface, process-to-product, record-to-built serial
- Acceptance: tooling coverage; calibration evidence; first-article correlation; as-built record linkage

## LM3 datum hierarchy

| ID | Datum | Parent | Origin and axes |
|---|---|---|---|
| `LM3-DAT-000` | trainset track datum | `ROOT` | lead-end car centreline at top-of-rail reference plane; +X forward, +Y left, +Z up |
| `LM3-DAT-100` | carbody primary datum | `LM3-DAT-000` | car longitudinal centre at nominal low-floor structural plane; parallel to trainset axes |
| `LM3-DAT-110` | body-to-bogie interface datum | `LM3-DAT-100` | secondary-suspension centre at nominal ride height; X longitudinal, Y axle direction, Z suspension reaction |
| `LM3-DAT-120` | door and platform datum | `LM3-DAT-100` | door opening centre at finished threshold; X along car, Y outboard, Z up |
| `LM3-DAT-130` | roof equipment rail datum | `LM3-DAT-100` | roof rail grid intersection at car centre; X rail pitch, Y cross-car, Z mounting normal |
| `LM3-DAT-140` | under-seat battery cassette datum | `LM3-DAT-100` | battery tray locating-pin centre; X withdrawal, Y cassette row, Z support reaction |
| `LM3-DAT-200` | wheelset and rail datum | `LM3-DAT-110` | axle centre at nominal wheel/rail contact geometry; X travel, Y axle, Z radial/up |
| `LM3-DAT-300` | articulation interface datum | `LM3-DAT-100` | articulation yaw-axis centre at nominal ride height; X connection chord, Y left, Z yaw axis |
| `LM3-DAT-400` | train-end and coupler datum | `LM3-DAT-100` | coupler centreline at nominal ride height; X coupling axis, Y left, Z up |

## Mechanical interface control

### LM3-ICD-001 — wheel to rail and route geometry

- Datums: `LM3-DAT-000` → `LM3-DAT-200`
- Products: `LM3-BOG-SA611`, `LM3-BOG-SA621`, `LM3-BOG-P040`, `LM3-BOG-P041`
- Geometry: 1435 mm standard-gauge planning basis; profile, back-to-back, wear and contact tolerances require supplier and track-system freeze
- Loads: static/dynamic axle, curving, traction, braking and derailment cases from accepted vehicle/track dynamics
- Services: none
- Verification: wheelset dimensional report; gauging and dynamics analysis; instrumented route acceptance
- Route gate: gradient, curvature, cant, vertical curve, rail profile or track tolerance changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-002 — carbody to powered bogie

- Datums: `LM3-DAT-100` → `LM3-DAT-110`
- Products: `LM3-BDY-P030`, `LM3-BOG-SA610`, `LM3-BOG-P046`
- Geometry: pivot, air-spring, yaw-link and damper datums controlled as one replaceable interface set
- Loads: AW0/AW2/AW3 vertical, lateral, yaw, traction, braking, anti-lift and jacking cases
- Services: pneumatic suspension, height sensing, earth bond
- Verification: datum survey; load calculation; ride-height and full-motion test
- Route gate: curve/cant/gradient, axle-load, crosswind or structure-deflection envelope changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-003 — carbody to trailer bogie

- Datums: `LM3-DAT-100` → `LM3-DAT-110`
- Products: `LM3-BDY-P030`, `LM3-BOG-SA620`, `LM3-BOG-P061`
- Geometry: common body connection with configuration-controlled trailer-bogie adapter details
- Loads: AW0/AW2/AW3 vertical, lateral, yaw, braking, anti-lift and jacking cases
- Services: pneumatic suspension, height sensing, earth bond
- Verification: A/B interchange gauge; load calculation; ride-height and full-motion test
- Route gate: curve/cant/gradient, axle-load, crosswind or structure-deflection envelope changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-004 — door cassette, body portal and platform

- Datums: `LM3-DAT-100` → `LM3-DAT-120`
- Products: `LM3-DOOR-SA310`, `LM3-BDY-P100`, `LM3-DOOR-P010`, `LM3-EXT-P010`
- Geometry: 1500 x 2050 mm design-reference carrier gauge; final aperture, threshold, seal compression, leaf sweep and platform gap/step by frozen door and route ICD
- Loads: door equipment, passenger crowd, abuse, aerodynamic pressure and emergency-operation cases
- Services: LV power, safety loop, communications, drainage
- Verification: carrier proof; gap/step analysis; obstruction/closed-and-locked/water/replacement tests
- Route gate: platform offset/height, cant, curvature or suspension-deflection changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-005 — articulation structure and passenger gangway

- Datums: `LM3-DAT-100` → `LM3-DAT-300`
- Products: `LM3-ART-SA800`, `LM3-ART-SA810`, `LM3-ART-SA820`, `LM3-ART-SA830`
- Geometry: yaw/pitch/roll axes, anti-lift path, bellows, bridge, turntable and pinch keep-outs controlled through full motion
- Loads: buff/draft, vertical shear, torsion, curving, emergency braking, derailment and recovery cases
- Services: HV trainline, LV/data, pneumatic, earth bond, drainage
- Verification: structural proof; full-motion sweep; gap/pinch gauge; water and passenger bridge load tests
- Route gate: minimum curve, reverse curve, vertical curve, cant transition or recovery regime changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-006 — train end, coupler and rescue vehicle

- Datums: `LM3-DAT-100` → `LM3-DAT-400`
- Products: `LM3-END-SA700`, `LM3-EIF-SA650`, `LM3-END-P050`, `LM3-END-P060`
- Geometry: coupler axis, anti-climber, energy absorber, carrier ring and rescue adapter share a surveyed end datum
- Loads: buff/draft, coupling impact, crash, rescue tow, lifting and asymmetric recovery cases
- Services: pneumatic brake, LV/data jumper, earth bond
- Verification: end survey; coupler/adapter proof; rescue compatibility and recovery trial
- Route gate: maximum gradient, minimum curve, disabled-train mass or rescue fleet changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-007 — battery cassette, tray and carbody

- Datums: `LM3-DAT-100` → `LM3-DAT-140`
- Products: `LM3-HV-SA510`, `LM3-BDY-P050`, `LM3-HV-P010`
- Geometry: locating pins, retention, withdrawal path, lid/gasket, vent, drain and fire barrier controlled as a replaceable cassette
- Loads: mass/CG, longitudinal/lateral acceleration, shock/vibration, crash, thermal-runaway pressure and lifting cases
- Services: traction HV, HVIL, LV/data, cooling/fire connection, vent/drain
- Verification: tray proof; retention and withdrawal tests; isolation/HVIL; thermal propagation and drainage tests
- Route gate: route energy, gradient, ambient/flood exposure or duty-cycle changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-008 — traction motor, gearbox, axle and bogie frame

- Datums: `LM3-DAT-110` → `LM3-DAT-200`
- Products: `LM3-TRC-SA615`, `LM3-TRC-P010`, `LM3-TRC-P020`, `LM3-BOG-P050`
- Geometry: shaft, foot, torque-link, coupling, oil-port and removal envelopes frozen by supplier RFQ and bogie ICD
- Loads: peak/continuous torque, gear mesh, axle motion, torque reaction, shock, thermal and overspeed cases
- Services: traction HV, temperature/speed sensing, earth bond, lubricant service
- Verification: alignment and runout; mount/torque-link proof; thermal map; rotation and removal trial
- Route gate: gradient, adhesion, braking blend, speed or thermal duty changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-009 — roof HVAC and equipment rail

- Datums: `LM3-DAT-100` → `LM3-DAT-130`
- Products: `LM3-ROOF-SA410`, `LM3-ROOF-P010`, `LM3-HV-P020`, `LM3-EXT-P040`
- Geometry: rail pitch, curb flatness, drop duct, condensate, keep-out and removal lift envelope controlled together
- Loads: equipment mass/CG, acceleration, crosswind, roof snow/maintenance, lifting and fatigue cases
- Services: HV/LV power, controls/data, supply/return air, condensate drain, earth bond
- Verification: rail/curb survey; attachment proof; air/leak/drain tests; removal trial
- Route gate: crosswind, ambient temperature, dust/rain or tunnel/structure clearance changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-010 — brake, WSP and wheelset

- Datums: `LM3-DAT-110` → `LM3-DAT-200`
- Products: `LM3-BOG-SA611`, `LM3-BOG-SA621`, `LM3-BOG-P060`, `LM3-BOG-P061`
- Geometry: disc/caliper, sensor target, cable sweep and wear/removal clearances controlled over suspension travel
- Loads: service/emergency/parking braking, low adhesion, thermal fade, wheel-slide and failed-channel cases
- Services: pneumatic brake, LV power, WSP/speed data, earth bond
- Verification: static brake/WSP test; thermal capacity; stopping-distance and low-adhesion route tests
- Route gate: gradient, line speed, adhesion, station spacing or stopping-margin changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-011 — vehicle envelope to structure and evacuation walkway

- Datums: `LM3-DAT-000` → `LM3-DAT-100`
- Products: `LM3-TRAINSET-A000`, `LM3-CAR-A900`, `LM3-SHELL-A200`
- Geometry: 2850 mm body-width concept envelope plus dynamic movement, throw, wear, construction and maintenance allowances; released swept envelope is open
- Loads: crosswind, cant deficiency, suspension failure, passenger load and structure movement combinations
- Services: emergency lighting/communications interaction
- Verification: static/dynamic gauging; BIM swept-volume clash; evacuation and detraining demonstration
- Route gate: all alignment, platform, parapet, tunnel, bridge movement or crosswind changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

### LM3-ICD-012 — lifting, jacking and field rerailing

- Datums: `LM3-DAT-000` → `LM3-DAT-100`
- Products: `LM3-CAR-A900`, `LM3-BDY-P010`, `LM3-END-P050`
- Geometry: four-point lifting/jacking, transverse bridge and equipment keep-outs tied to measured car mass/CG
- Loads: normal/asymmetric lift, one-point pressure loss, rerailing side load, tiedown and damaged-vehicle cases
- Services: hydraulic/mechanical equipment, bonding and communications
- Verification: point survey; structural calculation; proof load; trained-crew recovery demonstration
- Route gate: route access, viaduct parapet/walkway, depot equipment or final mass/CG changes
- Status: `design-reference-definition-complete; release-evidence-open`; tolerance `allocation-open-until-stack-and-supplier-freeze`.

## Load cases

| ID | Case | Closure status |
|---|---|---|
| `LM3-LC-001` | AW0/AW2/AW3 static mass, axle load and CG | `measured-mass-and-loading-definition-required` |
| `LM3-LC-002` | traction, service/emergency braking and low adhesion | `released-route-and-brake-supplier-model-required` |
| `LM3-LC-003` | curve, cant, vertical curve and full suspension motion | `vehicle-dynamics-model-and-route-profile-required` |
| `LM3-LC-004` | crosswind, aerodynamic pressure and exposed structures | `site-wind-and-vehicle-aerodynamic-evidence-required` |
| `LM3-LC-005` | buff/draft, coupling, rescue tow and crash energy | `structural-and-crash-authority-definition-required` |
| `LM3-LC-006` | fatigue and vibration duty spectrum | `route-spectrum-and-joint-classification-required` |
| `LM3-LC-007` | battery/HV thermal, fault, fire and environmental exposure | `supplier-data-and-hazard-analysis-required` |
| `LM3-LC-008` | lifting, jacking, rerailing and damaged-vehicle recovery | `measured-mass-cg-and-recovery-method-required` |
| `LM3-LC-009` | passenger, accessibility, door and evacuation operation | `loading-and-operational-rules-required` |
| `LM3-LC-010` | thermal, dust, rain, flood splash and water ingress | `route-environment-and-ingress-classification-required` |

## Route compatibility gates

### LM3-RCG-001

Does the released static/dynamic swept envelope clear track, platforms and structures?

Decision rule: redesign geometry only if gauging cannot be closed by infrastructure tolerance or operational control.

Evidence: surveyed alignment; structure/platform as-built model; vehicle gauging model.

### LM3-RCG-002

Do gradient, curvature, cant and vertical curves remain within vehicle capability?

Decision rule: change route first where reasonable; otherwise requalify bogie, articulation, traction or braking.

Evidence: released profile; vehicle dynamics; traction/braking results.

### LM3-RCG-003

Does the timetable duty fit usable battery energy and thermal limits with reserve?

Decision rule: adjust timetable/charging before changing battery capacity; redesign only after whole-life comparison.

Evidence: route simulation; supplier battery/motor/inverter/HVAC maps; degraded-mode cases.

### LM3-RCG-004

Are axle/load spectra accepted by track, bridge and viaduct designs?

Decision rule: iterate vehicle mass and civil structures through one controlled load model.

Evidence: measured mass/CG; dynamic augmentation; structural calculations.

### LM3-RCG-005

Are crosswind and exposed-water/viaduct operations acceptable?

Decision rule: define wind monitoring/operating limits or vehicle aerodynamic changes through hazard assessment.

Evidence: site wind study; vehicle characteristic wind curve; operating rules.

### LM3-RCG-006

Can passengers evacuate and responders recover a failed train everywhere?

Decision rule: coordinate walkway, detraining and access provision; change vehicle emergency interfaces only where necessary.

Evidence: evacuation model/drill; BIM access review; recovery demonstration.

### LM3-RCG-007

Do station platform gap, step and door-zone flows meet the accessibility basis?

Decision rule: coordinate platform and suspension control; modify threshold/door system only after system trade study.

Evidence: platform survey; suspension cases; gap/step and passenger-flow assessment.

## Verification matrix

| ID | Scope | Method | Interfaces | Load cases | Evidence |
|---|---|---|---|---|---|
| `LM3-VER-001` | product graph and configuration | `inspection` | — | — | manifest/IFC ID reconciliation and configuration record |
| `LM3-VER-002` | datum and tolerance-chain closure | `analysis+inspection` | LM3-ICD-001, LM3-ICD-002, LM3-ICD-003, LM3-ICD-004, LM3-ICD-005, LM3-ICD-006, LM3-ICD-007, LM3-ICD-008, LM3-ICD-009, LM3-ICD-010, LM3-ICD-011, LM3-ICD-012 | — | released ICDs, stack calculations, calibrated surveys and NCR disposition |
| `LM3-VER-003` | vehicle/route dynamic compatibility | `analysis+test` | LM3-ICD-001, LM3-ICD-002, LM3-ICD-003, LM3-ICD-005, LM3-ICD-011 | LM3-LC-001, LM3-LC-002, LM3-LC-003, LM3-LC-004 | independently checked simulations and instrumented route acceptance |
| `LM3-VER-004` | carbody, bogie, articulation and end structure | `analysis+test` | LM3-ICD-002, LM3-ICD-003, LM3-ICD-005, LM3-ICD-006, LM3-ICD-012 | LM3-LC-001, LM3-LC-005, LM3-LC-006, LM3-LC-008 | calculations, material/process qualification, NDT, proof and fatigue evidence |
| `LM3-VER-005` | door/platform/accessibility | `analysis+demonstration` | LM3-ICD-004 | LM3-LC-003, LM3-LC-009 | gap/step, obstruction, emergency release, water and passenger-flow evidence |
| `LM3-VER-006` | traction, braking and energy | `analysis+test` | LM3-ICD-001, LM3-ICD-008, LM3-ICD-010 | LM3-LC-002, LM3-LC-003, LM3-LC-007, LM3-LC-010 | supplier maps, HIL, dynamometer and route test results |
| `LM3-VER-007` | battery/HV fire and environmental | `analysis+test` | LM3-ICD-007 | LM3-LC-006, LM3-LC-007, LM3-LC-010 | hazard analysis, propagation/containment, ingress, isolation and emergency-response evidence |
| `LM3-VER-008` | HVAC/roof equipment | `analysis+test` | LM3-ICD-009 | LM3-LC-004, LM3-LC-006, LM3-LC-010 | attachment, airflow, thermal, EMC, ingress and removal evidence |
| `LM3-VER-009` | gauging, bridge/viaduct evacuation and recovery | `analysis+demonstration` | LM3-ICD-006, LM3-ICD-011, LM3-ICD-012 | LM3-LC-004, LM3-LC-008, LM3-LC-009 | swept-volume BIM review plus representative evacuation/recovery drills |

The complete machine-readable record is [`design-detail-register.json`](design-detail-register.json).
