# Drawing and evidence register — `light-metro-3car`

This register is the bridge between the v1 Markdown specification and
the v2 CAD/shop-drawing release. It lists the controlled drawings,
supplier documents, and test evidence a fabricator must produce before
the first article can be released for static and dynamic testing.

Document IDs use `LM3` for the `light-metro-3car` family. Revision
`A` is the first v2 release candidate.

## Controlled drawing set

| ID | Title | Owner | v1 source | v2 release content |
|---|---|---|---|---|
| LM3-GA-000 | Trainset general arrangement | OSR/mechanical | `general-arrangement.md` | 2D GA, clearance envelope, platform interface, mass table |
| LM3-BDY-100 | Carbody primary steel assembly | Fabricator | `body.md` | FreeCAD/neutral CAD package, 2D assembly, weld map, datum scheme |
| LM3-BDY-110 | Underframe ladder assembly | Fabricator | `body.md` | Tube cut list, plate flat patterns, fixture drawing |
| LM3-BDY-120 | Side/roof spaceframe assembly | Fabricator | `body.md` | RHS cut list, door/window aperture datums |
| LM3-BDY-130 | Coupler pocket and crash-can interface | Fabricator + coupler supplier | `body.md`, `interfaces.md` | Machined inserts, bolted energy absorber interface |
| LM3-BDY-140 | Battery tray and under-seat enclosure | Fabricator + battery supplier | `body.md`, `traction.md` | Service hatches, vent path, HV isolation clearances |
| LM3-BDY-150 | Composite side/roof panel envelopes | Composite supplier | `body.md` | Panel mould drawings, inserts, edge radii, repair zones |
| LM3-BDY-155 | Identical A/B-end fiberglass cowl cast kit | Composite supplier + OSR/mechanical | `end-cowl.md`, `sensor_cowl.py` | Surface-modelled exterior A-surface and derived B-surface/flange/trim/mould neutral CAD, CWL-FRP-01 through CWL-FRP-06 mould/trim drawings, laminate schedule, insert map, steel backing-ring datum, glass/lamp/sensor hatch service access |
| LM3-SYS-160 | End coupler and crash-energy assembly | Coupler supplier + integrator | `interfaces.md`, BOM | Scharfenberg head, electric-head carrier, crash absorber envelope, recovery/tow interface |
| LM3-SYS-170 | Inter-car articulation and trainline assembly | Integrator + articulation supplier | `articulation.md`, `body.md`, `interfaces.md` | Lower spherical pivot, anti-lift keeper, upper roll-yaw-pitch links, bellows, turntable floor, drag-chain, TCN-E/CAN-FD/HV/coolant/HVAC interfaces |
| LM3-DOOR-200 | Door cassette installation | Door supplier | COTS catalogue | Mounting datums, threshold, drainage, lock-loop wiring |
| LM3-WIN-210 | Window cassette installation | Glazing supplier | COTS catalogue | Bond/gasket land, drain path, replacement method |
| LM3-HVAC-220 | Roof HVAC installation | HVAC supplier | COTS catalogue | Roof rails, ducting, condensate, service clearance |
| LM3-INT-230 | Interior fit-out installation | Integrator | COTS catalogue | Seats, rails, floor boards, hatches, panels, signage |
| LM3-ELC-300 | Low-voltage harness routing | Integrator | `interfaces.md` | Harness schedule, connector list, segregation, labels |
| LM3-HV-310 | HV battery/traction routing | Integrator | `traction.md` | HVIL loop, busbars/cables, insulation clearances |
| LM3-HV-320 | Per-car battery pack and charging assembly | Battery + traction suppliers | `traction.md`, BOM | Na-ion module envelope, HV contactor/BMS cabinet, multi-input PV/station charge inverter, side-pin charge connector, coolant/vent paths |
| LM3-HV-325 | Rooftop PV and charge-input assembly | Solar + traction suppliers | `traction.md`, `interfaces.md`, BOM | Bonded flexible laminates, raised rigid panels, roof rails, edge clamps, MPPT combiner, fire isolators, downlink gland, bonding/earthing details |
| LM3-OBS-330 | T-OBS nose sensor-pack installation | T-OBS supplier + integrator | RFC 0015, BOM | LIDAR, radar, stereo camera, ultrasonic transducers, heated sensor windows, cleaning access |
| LM3-BOG-400 | Powered bogie assembly | Bogie fabricator | `bogie.md` | Frame drawing, motor/gearbox/brake interfaces |
| LM3-BOG-410 | Trailer bogie assembly | Bogie fabricator | `bogie.md` | Frame drawing, brake/suspension interfaces |
| LM3-TRC-500 | Traction package installation | Traction supplier | `traction.md` | Motor, gearbox, inverter, cooling, EMC bonding |
| LM3-COM-600 | Train communication and antenna install | Integrator | `interfaces.md` | TCN-E, radios, GNSS, CCTV, PIS, intercom |

## Manufacturing evidence

| ID | Evidence | Required before | Notes |
|---|---|---|---|
| LM3-EV-MAT-001 | Steel mill certificates and heat traceability | G0 material release | Covers RHS, plate, machined inserts |
| LM3-EV-WLD-010 | WPS/PQR register and welder qualifications | First production weld | EN 15085 / EN ISO 9606 basis |
| LM3-EV-WLD-020 | Weld inspection and NDT report | G1 frame complete | VT + MT/UT per weld class |
| LM3-EV-DIM-030 | Frame dimensional survey | G1 frame complete | Bogie centres, door/window apertures, coupler height |
| LM3-EV-COR-040 | Blast, primer, topcoat, cavity-wax report | G2 corrosion complete | Includes DFT readings |
| LM3-EV-CMP-050 | Composite material certificate pack | G3 shell complete | EN 45545 evidence and repair method |
| LM3-EV-CMP-055 | Fiberglass cowl cast first-article report | G3 shell complete | Laminate coupons, insert pull-out, split-line fit, glass-carrier land survey, and A/B-end interchange check |
| LM3-EV-BND-060 | Adhesive batch, surface-prep, cure records | G3 shell complete | Includes witness coupons |
| LM3-EV-WTR-070 | Water ingress test | G4 COTS systems fitted | Doors, windows, roof equipment |
| LM3-EV-ELC-080 | Bonding/earthing and insulation resistance | G5 electrical safe | Includes HV and LV separation checks |
| LM3-EV-HV-090 | HVIL and battery isolation report | G5 electrical safe | Battery supplier + integrator sign-off |
| LM3-EV-DOOR-100 | Door obstruction, release, lock-loop test | G6 static complete | Per door cassette serial number |
| LM3-EV-HVAC-110 | HVAC cooling and drain test | G6 static complete | +50 C performance evidence may be supplier lab data |
| LM3-EV-BRK-120 | Static brake and park-brake test | G6 static complete | Links to bogie/brake supplier records |
| LM3-EV-MASS-130 | Weighing and axle-load report | G7 dynamic ready | Empty and simulated AW2/AW3 cases |
| LM3-EV-RIDE-140 | Bogie alignment and ride-height report | G7 dynamic ready | Before dynamic testing |

## Supplier document index

| Package | Supplier document required | Acceptance rule |
|---|---|---|
| Doors | Installation manual, maintenance manual, lifecycle test, EN 14752 evidence | Fits LM3-DOOR-200 without primary steel change |
| Windows | Glazing certificate, adhesive/gasket procedure, replacement manual | Fits LM3-WIN-210 and passes water test |
| HVAC | Datasheet, +50 C derating curve, wiring manual, refrigerant record | Fits LM3-HVAC-220 and aux-power budget |
| Composite panels | Laminate schedule, fire test, repair manual, insert pull-out data | Panels remain non-structural |
| Fiberglass end cowls | Mould split/trim drawings, laminate coupons, fire test, insert pull-out data, gasket/seal procedure, repair manual | Same cast kit fits both A-end and B-end without steel-frame change |
| Seats/rails | Fire certificate, pull-load certificate, cleaning/repair manual | Fits LM3-INT-230 insert grid |
| Lighting/PIS/CCTV/intercom | EMC/vibration evidence, firmware version, wiring manual | Enumerates on car network and passes static test |
| Battery | Cell/module certificate, BMS manual, vent/fire containment data | Fits LM3-BDY-140 and LM3-HV-310 |
| Traction and charging | Motor/inverter/gearbox datasheets, multi-input charge inverter datasheet, cooling and EMC instructions | Fits LM3-TRC-500, LM3-HV-320, and LM3-HV-325 |
| Rooftop solar | PV module datasheets, adhesive/bond process, rail/clamp vibration evidence, fire-isolation switch data | Fits LM3-HV-325 without roof-spaceframe redesign |
| Bogie parts | Wheelset, bearing, spring, damper, brake supplier certificates | Fits LM3-BOG-400/410 |
| Articulation/gangway | Bearing rating, motion-envelope proof, bellows/turntable fire evidence, maintenance manual | Fits LM3-SYS-170 without carbody adapter redesign |

## Release gates

| Gate | Minimum drawing/evidence state |
|---|---|
| v2A design freeze | All controlled drawings issued at rev A; supplier envelopes frozen |
| First steel cut | LM3-BDY-100/110/120, LM3-EV-MAT-001, LM3-EV-WLD-010 complete |
| First carbody shell complete | LM3-EV-WLD-020, LM3-EV-DIM-030, LM3-EV-COR-040 complete |
| First COTS fit-out complete | Door/window/HVAC/interior supplier docs accepted; LM3-EV-WTR-070 complete |
| First energisation | LM3-EV-ELC-080 and LM3-EV-HV-090 complete |
| Static test release | LM3-EV-DOOR-100, LM3-EV-HVAC-110, LM3-EV-BRK-120 complete |
| Dynamic test release | LM3-EV-MASS-130 and LM3-EV-RIDE-140 complete |

## Change control

- Any supplier swap that fits the reserved envelope is a document
  revision, not a structural redesign.
- Any change to side sills, bolsters, coupler pockets, door posts,
  or crash-can interfaces reopens FEA and static proof evidence.
- Any mass increase above a module row limit requires a new axle-load
  report before dynamic testing.
- Any power increase above a module row budget requires an aux-power
  and cooling-capacity review.
