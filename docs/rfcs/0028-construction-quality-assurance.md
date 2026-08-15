# RFC 0028 — Construction Quality Assurance System

**Status:** Draft — proposed
**Date:** 2026-06-12
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0009 Track Design Standard](0009-track-design-standard.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md), [RFC 0011 Civil Infrastructure Design Standard](0011-civil-infrastructure-design-standard.md), [RFC 0013 Operations Rulebook](0013-operations-rulebook.md), [RFC 0014 Depot Design Standard](0014-depot-design-standard.md), [RFC 0015 Driverless Operation](0015-driverless-operation.md), [RFC 0021 Battery Traction](0021-battery-traction.md), [RFC 0022 Bogie + Traction Drive](0022-bogie-traction-drive.md), [RFC 0023 Door System Reference Design](0023-door-system-reference-design.md), [RFC 0029 Maintenance Schedule System](0029-maintenance-schedule-system.md)

## 1. Summary

OpenSourceRail commits to an **owner-controlled construction QA
system** for both locally built rolling stock and fixed infrastructure.
The system is gate-based: a package cannot move to the next stage until
the relevant hold point is released by the owner, owner engineer, or
named acceptance board.

The machine-readable gate register is
[`lib/templates/construction-qa.toml`](../../lib/templates/construction-qa.toml).
Generated city READMEs render the same register so every deployment
shows the required evidence before passenger opening.

This is deliberately not a vendor warranty model. OSR assumes local
production, local ownership, and local maintenance. The quality system
therefore makes the owner the evidence holder from day one.

## 2. Non-goals

- **Not a replacement for local law or regulator approval.** Local
  building, railway, labour, fire, and electrical approvals still apply.
- **Not a standards rewrite.** Welding, civil, electrical, fire,
  accessibility, and software standards are referenced by the component
  RFCs and local authority requirements.
- **Not a paperwork-only system.** A hold point is only released when
  physical inspection, test evidence, and open-defect disposition agree.
- **Not a reason to inflate train CAPEX.** Per-train QA/acceptance is a
  small nominal production cost; fixtures, tooling, calibration systems,
  and commissioning bays sit in the railway production plant or OPEX.

## 3. Quality Record Structure

Every QA record uses the same minimum fields:

| Field | Requirement |
|---|---|
| Asset id | Trainset, car, bogie, station, span, switch, charger, W-SBC, or package id |
| Drawing/config version | Released drawing, firmware hash, test procedure, template id |
| Inspector | Named person and organisation |
| Result | Pass, pass with minor defects, hold, reject |
| Evidence link | Test sheet, photo, measurement file, certificate, log export |
| Defect id | Required when result is not clean pass |
| Release authority | Named role that accepted the hold point |
| Handover target | Operations, maintenance, safety case, or asset register |

The evidence register in
[`docs/certification/evidence-register.md`](../certification/evidence-register.md)
is the safety-case view. The construction QA register is the production
view. The two must cross-reference each other but do not duplicate every
line item.

## 4. Gate Register

The mandatory gate ids are:

| Gate | Scope | Release condition |
|---|---|---|
| `qa-00-design-freeze` | Whole railway | Drawings, interfaces, hazards, inspection/test plans, and supplier/material registers baselined |
| `qa-10-carbody-structure` | Carbody, underframe, crash structure, coupler pockets | Weld/material traceability, dimensional survey, NDT, coating, and load evidence accepted |
| `qa-11-bogie-wheelset` | Bogies, wheelsets, suspension, brake rigging | Bogie NDT, wheel/axle inspection, bearing certificate, brake static test, and torque logs accepted |
| `qa-12-traction-brake-battery` | Motors, inverters, brake blending, onboard battery, thermal system | Bench and trainset functional tests accepted before dynamic movement |
| `qa-13-passenger-systems` | Doors, HVAC, lighting, interiors, accessibility, passenger information | Door cycles, HVAC performance, PRM check, emergency equipment, and saloon inspection accepted |
| `qa-14-onboard-control` | TCN-E, ATP/ATO, odometry, radios, sensors | Hardware identity, firmware hashes, authentication, simulator replay, and trainline tests accepted |
| `qa-15-first-article-trainset` | Complete trainset | Static, dynamic, endurance, braking, charging, evacuation, rescue, and maintainability acceptance complete |
| `qa-20-survey-geotech` | Alignment, ROW, utilities, geotechnical | Survey, utility, borehole/test-pit, drainage/flood, and ROW constraints accepted |
| `qa-21-earthworks-drainage` | Earthworks, subgrade, drainage, fencing | Compaction, material, drainage, culvert, and fence/gate evidence accepted |
| `qa-22-trackform-rail` | Slab track, rail, welds, fasteners, turnouts, crossings | Geometry, weld NDT, fastener torque, turnout detection, and crossing tests accepted |
| `qa-23-structures` | Viaducts, bridges, bearings, expansion joints, parapets, walkways | Concrete/rebar, bearings, joints, drainage, access, and structural inspection accepted |
| `qa-24-stations-depots-plant` | Stations, depots, production plant, public realm | Platform gauge, canopy, fire/life safety, accessibility, depot bay, and tool calibration accepted |
| `qa-25-power-energy` | PV, stationary storage, chargers, grid/PPA tie, earthing | PV string, BESS, charger, relay, earthing, isolation, and islanding tests accepted |
| `qa-26-wayside-comms-safety` | W-SBCs, switches, intrusion sensors, comms, fare/PIS/CCTV | Identity register, coverage, switch proof, sensor calibration, passenger-system, and cyber tests accepted |
| `qa-30-integrated-trial-running` | Whole railway | Trial running, degraded modes, emergency exercise, maintenance handback, and safety release accepted |

## 5. Rolling-Stock QA

Rolling-stock QA is organised by trainset, car, and replaceable module.
The owner must be able to trace a defect from service all the way back
to the production record that released the affected component.

### 5.1 Carbody and Crash Structure

Required records:

- Material certificates for underframe, side frame, roof, end cowl
  support, crash-energy components, coupler pocket, and door posts.
- Weld map and welder qualification record.
- Dimensional survey after welding and after bogie marriage.
- NDT sampling plan and results.
- Corrosion protection, paint, and sealant record.
- Static proof or calculation pack for AW3 loading, jacking, lifting,
  and recovery tow cases.

### 5.2 Bogie, Wheelset, Suspension, and Brake

Required records:

- Bogie frame weld and NDT pack.
- Wheel, axle, bearing, and axlebox certificates.
- Wheel profile and back-to-back measurement.
- Torque records for suspension, brake, axlebox, and motor mounts.
- Brake static and dynamic test records.
- Post-run inspection after the first dynamic movement.

### 5.3 Traction, Battery, and Thermal System

Required records:

- Motor and inverter factory acceptance or bench-test result.
- Insulation resistance and protective bonding result.
- BMS cell map, serial numbers, initial capacity sample, and contactor
  test.
- Thermal soak result for high-ambient operation.
- Charging interface test with station/depot chargers.
- Brake blending and regenerative-friction transition curves.

### 5.4 Passenger and Accessibility Systems

Required records:

- Door-cycle counter test and obstacle detection.
- HVAC cooling/heating result for the deployment climate preset.
- Emergency lighting, PA, passenger information, CCTV, and call-point
  test.
- PRM bay, tactile, grab-pole, wheelchair, and boarding-gap checklist.
- Fire-load and interior-material compliance evidence.

### 5.5 Onboard Control and Software

Required records:

- Hardware serial register.
- Firmware hash and signing record.
- Message-authentication configuration.
- TCN-E continuity and latency test.
- Odometry, sensor, and degraded-mode simulation replay.
- Cybersecurity checklist before line testing.

### 5.6 First Article and Batch Release

The first trainset of each local production run must complete:

- Full static acceptance.
- Full dynamic acceptance.
- Braking curves in dry and reduced-adhesion proxy conditions.
- Charging at representative station and depot chargers.
- Rescue/coupling drill.
- Passenger evacuation drill.
- Maintainability demonstration for battery module, door actuator,
  brake pad, HVAC filter, and W-SBC/onboard computer replacement.
- At least 1,000 km fault-free trial running before series release.

Series trainsets may use a reduced evidence pack only after the first
article is accepted and the production process is unchanged.

## 6. Infrastructure QA

Infrastructure QA is organised by physical work package and asset id.
Every station, line section, switch, structure, energy site, and
systems cabinet must enter the asset register before handover.

### 6.1 Survey, Geotechnical, and ROW

Required records:

- Survey control and alignment setout.
- Utility scan and clash register.
- Borehole or test-pit log by geotechnical zone.
- Flood path, drainage, and culvert basis.
- Cadastral and ROW constraint register.

### 6.2 Earthworks, Drainage, and Fencing

Required records:

- Subgrade and capping-layer compaction tests.
- Material gradation and source record.
- Drainage as-built and flow direction.
- Culvert inspection and cover level.
- Fence, gate, and intrusion-risk punch list.

### 6.3 Trackform, Rail, Turnouts, and Crossings

Required records:

- Slab/plinth pour records.
- Fastener torque logs.
- Weld NDT and rail-stress record.
- Track geometry run before trial service.
- Turnout detection and point-machine proof.
- Level-crossing barrier, warning, and obstacle-detection test where
  fitted.

### 6.4 Structures

Required records:

- Concrete, reinforcement, precast, and post-tensioning records.
- Bearing installation and survey.
- Expansion-joint record.
- Drainage, parapet, walkway, and access inspection.
- Bridge scour check for water crossings.

### 6.5 Stations, Depots, and Production Plant

Required records:

- Platform gauge and boarding-gap survey.
- Canopy, roof PV, drainage, and fixings inspection.
- Fire/life-safety signoff.
- Accessibility audit.
- Depot pit, stinger, wash, lathe, lifting, and isolation checks.
- Production plant fixture and tool calibration.

### 6.6 Energy, Signalling, Comms, and Passenger Systems

Required records:

- PV string test, BESS commissioning, charger load test, relay settings,
  earthing, and emergency isolation drill.
- W-SBC identity register and switch proof test.
- Radio coverage and backup-link test.
- Intrusion sensor calibration.
- OCC, passenger information, fare, CCTV, and public-address tests.
- Cybersecurity closeout and firmware baseline.

## 7. Nonconformance Control

Defects are classified:

| Class | Meaning | Rule |
|---|---|---|
| NCR-A | Minor quality note | May be accepted with owner engineer approval and logged for future maintenance |
| NCR-B | Correct-before-next-stage | The package cannot pass its current gate until reworked and re-inspected |
| NCR-C | Safety or configuration blocker | The asset is rejected or isolated until root cause, corrective action, and re-test are complete |

Repeated NCR-B or any NCR-C triggers a production pause for the affected
process. The pause is local to the process, not necessarily the whole
programme, unless the defect indicates a shared design or supplier
failure.

## 8. Trial Running and Opening

Passenger service is not allowed until `qa-30-integrated-trial-running`
is released. Minimum evidence:

- Timetable trial running over representative service hours.
- Emergency exercise with local responders.
- Degraded-mode drill for OCC, station staff, and maintenance.
- Possession and handback demonstration.
- Maintenance defect response demonstration.
- Open-defect register showing no safety blockers.
- Safety-case release note referencing the accepted evidence.

## 9. Samawah Application

For Samawah, the QA system applies to:

- 96 locally built 3-car trainsets.
- 58.4 km of generated route.
- 31 unique stations.
- Station/depot charging microgrids and the dedicated solar plant/PPA
  interface.
- The brownfield yard/workshop conversion if RFC 0027 Phase 1 confirms
  usable assets.

The first-article trainset and first completed station should be treated
as programme learning gates: they set the acceptance standard for the
remaining batch.
