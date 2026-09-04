# Drawing and evidence register — `light-metro-3car`

This register is the bridge between the v1 Markdown specification and
the v2 CAD/shop-drawing release. It lists the controlled drawings,
supplier documents, and test evidence a fabricator must produce before
the first article can be released for static and dynamic testing.

Document IDs use `LM3` for the `light-metro-3car` family. Revision
`A` is the first v2 release candidate.

The generated [`factory-drawings` seed index](../../../design/component-catalogue/catalog/buildable-trainset/factory-drawings/index.md)
now provides an individual drafting/checking brief for each of the 18 drawing
IDs controlled by the ten factory packages. Those seeds organize scope; they
remain non-dimensioned and unissued until this register's release gates close.

## Controlled drawing set

| ID | Title | Owner | v1 source | v2 release content |
|---|---|---|---|---|
| LM3-GA-000 | Trainset general arrangement | OSR/mechanical | `general-arrangement.md` | 2D GA, clearance envelope, platform interface, mass table |
| LM3-MASS-010 | Controlled trainset mass budget and product closure ledger | OSR/mechanical + suppliers | generated `mass-budget.md`, generated `mass-closure-ledger.md` | Modeled category subtotal, explicit engineering reserve, all 120 product responsibility assignments, supplier/production-CAD/weigh evidence state, lightweighting comparison, individual-car/axle/CG closure |
| LM3-JNT-020 | Joint and fastener control schedule | OSR/mechanical + integrator | generated `joint-control-schedule.md` | Parent/child joint IDs, joining classes, torque authority, locking/re-torque release requirement, numeric values, inspection record |
| LM3-BDY-100 | Carbody primary steel assembly | Fabricator | `body.md` | FreeCAD/neutral CAD package, 2D assembly, weld map, datum scheme |
| LM3-BDY-110 | Underframe ladder assembly | Fabricator | `body.md` | Tube cut list, plate flat patterns, fixture drawing |
| LM3-BDY-120 | Side/roof spaceframe assembly | Fabricator | `body.md` | RHS cut list, door/window aperture datums |
| LM3-BDY-130 | Coupler pocket and crash-can interface | Fabricator + coupler supplier | `body.md`, `interfaces.md` | Machined inserts, bolted energy absorber interface |
| LM3-BDY-140 | Battery tray and under-seat enclosure | Fabricator + battery supplier | `body.md`, `traction.md` | Service hatches, vent path, HV isolation clearances |
| LM3-BDY-150 | Exterior glass-fibre material, mould, and trim-envelope control | Composite supplier + fabricator | `body.md`, `modular-fiberglass-body.md` | Laminate schedule, reusable mould drawings, core/insert maps, CNC trim envelopes, edge radii, fire evidence, repair zones |
| LM3-BDY-155 | Identical A/B-end fiberglass cowl cast kit | Composite supplier + OSR/mechanical | `end-cowl.md`, `sensor_cowl.py` | Surface-modelled exterior A-surface and derived B-surface/flange/trim/mould neutral CAD, CWL-FRP-01 through CWL-FRP-06 mould/trim drawings, laminate schedule, insert map, steel backing-ring datum, glass/lamp/sensor hatch service access |
| LM3-BDY-160 | One-metre clip-on glass-fibre body module system | Composite supplier + fabricator | `modular-fiberglass-body.md`, `modular_fiberglass_body.py` | Common 1,000 mm side/roof moulds, mould release and cure records, solid/window/door/roof trim variants, clip rail and insert map, anti-lift retainer, EPDM joint/drain, module numbering, master-frame dry fit, timed one-shift installation route |
| LM3-BDY-165 | Exterior module variant trim and configuration map | Composite supplier + fabricator | generated `factory-release-work-packages.md` | Solid/window/door/roof CNC trim and drill definitions, serialized bay map, clip/seal datums, replacement and repair zones |
| LM3-FAS-180 | Panoramic glass carrier, seal and drainage interface | OSR/mechanical + glazing supplier | `end-cowl.md`, generated `factory-release-work-packages.md` | Steel-backed carrier segments, setting blocks, secondary retention, pane-edge clearances, compression map, drain/washer/heater routes and removal path |
| LM3-FAS-185 | Reversible front-lamp cassette and aiming interface | OSR/mechanical + lamp supplier | `end-cowl.md`, generated `factory-release-work-packages.md` | Common A/B tray, retained adjusters, optical-axis datums, harness/earth/drip loops, thermal/service clearances and interchange record |
| LM3-END-650 | Configurable train-end interface | Fabricator + integrator | `articulation.md`, generated `train-end-interface.md` | Common end carrier ring, option bolt grid, seal/drain datums, panoramic closeout option, open mid-connection portal option, configuration record |
| LM3-SYS-160 | End coupler and crash-energy assembly | Coupler supplier + integrator | `interfaces.md`, BOM | Scharfenberg head, electric-head carrier, crash absorber envelope, recovery/tow interface |
| LM3-SYS-170 | Inter-car articulation and trainline assembly | Integrator + articulation supplier | `articulation.md`, `body.md`, `interfaces.md` | Lower spherical pivot, anti-lift keeper, upper roll-yaw-pitch links, bellows, turntable floor, drag-chain, TCN-E/CAN-FD/HV/coolant/HVAC interfaces |
| LM3-SYS-175 | Train-to-train open-end articulation | Integrator + articulation supplier | `articulation.md`, generated `train-end-interface.md` | Open-end gangway cassette, semi-permanent drawbar, lower/upper articulation, turntable threshold bridge, service-jumper transition, blanking covers, motion sweep |
| LM3-DOOR-200 | Door cassette installation | Door supplier | COTS catalogue | Mounting datums, threshold, drainage, lock-loop wiring |
| LM3-WIN-210 | Window cassette installation | Glazing supplier | COTS catalogue | Bond/gasket land, drain path, replacement method |
| LM3-HVAC-220 | Roof HVAC installation | HVAC supplier | COTS catalogue | Roof rails, ducting, condensate, service clearance |
| LM3-ROOF-225 | Roof fairing, penetration, equipment and service-zone coordination | OSR/mechanical + integrator | `roof-fitout.md`, generated `factory-release-work-packages.md` | Curb/fairing/rail/pad/gland/bond drawings, penetration schedule, HVAC/PV/antenna removal paths, finish/anti-slip/heat/electrical keep-outs |
| LM3-INT-230 | Interior fit-out installation | Integrator | COTS catalogue | Seats, rails, floor boards, hatches, panels, signage |
| LM3-INT-231 | Interior moulded-panel, trim and service-access family | Interior fabricator + integrator | `dedicated-parts-and-moulds.md`, generated `factory-release-work-packages.md` | Ceiling/light/HVAC, sidewall/reveal/cable, battery/seat, threshold/PRM/door-pocket part drawings, moulds, trim nests and removal sequence |
| LM3-FIX-235 | Common rail, fastener and fixture-adapter family | OSR/mechanical + integrator | generated `small-component-standard.md`, generated `factory-release-work-packages.md` | Rail/foot definition, seat/handrail/equipment adapter variants, grip/locking/torque schedule, installed coordinate map and fixture-specific proof route |
| LM3-FIN-240 | Pre-cut livery film artwork, application and repair pack | Operator + finish supplier + integrator | `exterior-finish-process.md`, generated `factory-release-work-packages.md` | Bay-numbered cut files, substrate/application records, seam/edge/keep-out map, batch/coupon trace and local repair/removal instructions |
| LM3-FIN-245 | Radiative roof coating qualification and one-car trial pack | Materials/test authority + integrator | `exterior-finish-process.md`, generated `factory-release-work-packages.md` | Controlled formulation/application, coupon ageing/optical plan, paired roof-zone thermal trial, maintenance/repair procedure and baseline-finish fallback |
| LM3-REC-270 | Vehicle jacking, lifting, towing and field-rerailing interface | OSR/mechanical + recovery engineer | `field-rerailing-concept.md`, generated `factory-release-work-packages.md` | J1--J4 and adapter drawings, support combinations/reactions, stop conditions, isolation/brake/bogie-retention diagrams and proof/maintenance schedule |
| LM3-ELC-300 | Low-voltage harness routing | Integrator | `interfaces.md` | Harness schedule, connector list, segregation, labels |
| LM3-HV-310 | HV battery/traction routing | Integrator | `traction.md` | HVIL loop, busbars/cables, insulation clearances |
| LM3-HV-320 | Per-car battery pack and charging assembly | Battery + traction suppliers | `traction.md`, BOM | LFP module envelope, HV contactor/BMS cabinet, direct-DC PV/station charge interface, side-pin charge connector, coolant/vent/mist paths |
| LM3-HV-325 | Rooftop PV and charge-input assembly | Solar + traction suppliers | `traction.md`, `interfaces.md`, BOM | Bonded flexible laminates, raised rigid panels, roof rails, edge clamps, MPPT combiner, fire isolators, downlink gland, air-cleaner pump/nozzle manifold, bonding/earthing details |
| LM3-OBS-330 | T-OBS nose sensor-pack installation | T-OBS supplier + integrator | RFC 0015, BOM | LIDAR, radar, stereo camera, ultrasonic transducers, heated sensor windows, cleaning access |
| LM3-BOG-400 | Powered bogie assembly | Bogie fabricator | `bogie.md` | Frame drawing, motor/gearbox/brake interfaces |
| LM3-BOG-410 | Trailer bogie assembly | Bogie fabricator | `bogie.md` | Frame drawing, brake/suspension interfaces |
| LM3-TRC-500 | Traction package installation | Traction supplier | `traction.md` | Motor, gearbox, inverter, cooling, EMC bonding |
| LM3-COM-600 | Train communication and antenna install | Integrator | `interfaces.md` | TCN-E, radios, GNSS, CCTV, PIS, intercom |

## Manufacturing evidence

| ID | Evidence | Required before | Notes |
|---|---|---|---|
| LM3-EV-CFG-000 | Configuration baseline sheet | v2A design freeze | Confirms 3 repeated 16.5 m cars, 3 powered bogies, 3 trailer bogies, 540 kWh usable battery, 78.75 t controlled planning tare (75.308 t modeled subtotal + 3.442 t engineering reserve), and no city-specific train variant |
| LM3-EV-MAT-001 | Steel mill certificates and heat traceability | G0 material release | Covers RHS, plate, machined inserts |
| LM3-EV-REC-005 | Recovered axle/axlebox acceptance pack | G0B recovered-component release | Quarantine, cleaning, dimensional survey, UT/MT/NDT, bearing replacement or supplier re-certification |
| LM3-EV-WLD-010 | WPS/PQR register and welder qualifications | First production weld | EN 15085 / EN ISO 9606 basis |
| LM3-EV-WLD-020 | Weld inspection and NDT report | G1 frame complete | VT + MT/UT per weld class |
| LM3-EV-DIM-030 | Frame dimensional survey | G1 frame complete | Bogie centres, door/window apertures, coupler height |
| LM3-EV-COR-040 | Blast, primer, topcoat, cavity-wax report | G2 corrosion complete | Includes DFT readings |
| LM3-EV-CMP-050 | Composite material and mould-process certificate pack | G3 shell complete | EN 45545 evidence, resin/fibre/core/gelcoat batch trace, mould release record, cure record, coupon trace, and repair method |
| LM3-EV-CMP-055 | Fiberglass cowl cast first-article report | G3 shell complete | Laminate coupons, insert pull-out, split-line fit, glass-carrier land survey, and A/B-end interchange check |
| LM3-EV-CMP-057 | One-metre body module first-article report | G3 shell complete | Mould inspection, cure and demould record, laminate coupons, CNC trim report, edge-seal record, master-frame dry fit, clip/anti-lift proof, insert pull-out, water/vibration test, and timed removal/refit |
| LM3-EV-DIM-058 | Dedicated factory drawing/interface package review | v2A design freeze | Use the generated factory-release readiness record to show all ten packages have approved drawings, frozen inputs, product revisions, released tooling, characteristic lists and named verification owners; generation alone does not constitute approval |
| LM3-EV-BND-060 | Adhesive batch, surface-prep, cure records | G3 shell complete | Includes witness coupons |
| LM3-EV-GLZ-065 | Front glass carrier, seal and service trial | G4 COTS systems fitted | Retention proof, edge/compression survey, drainage/water result, heater isolation and timed pane replacement |
| LM3-EV-LMP-067 | Reversible front-lamp fit and aim report | G4 COTS systems fitted | A/B interchange, optical-axis/aim range, lock/vibration retention, harness access and supplier photometric evidence |
| LM3-EV-WTR-070 | Water ingress test | G4 COTS systems fitted | Doors, windows, roof equipment |
| LM3-EV-FIN-075 | Livery film first-car application and repair report | G4 COTS systems fitted | Actual-substrate coupon, batch/application record, edge/seam map, wash compatibility, patch and one-metre module removal trial |
| LM3-EV-RCF-077 | Radiative roof-coating qualification disposition | Optional coating production release | Fire/material acceptance, new/aged optical results, durability/cleaning evidence, one-car trial and accepted baseline-finish fallback |
| LM3-EV-ELC-080 | Bonding/earthing and insulation resistance | G5 electrical safe | Includes HV and LV separation checks |
| LM3-EV-HV-090 | HVIL and battery isolation report | G5 electrical safe | Battery supplier + integrator sign-off |
| LM3-EV-DOOR-100 | Door obstruction, release, lock-loop test | G6 static complete | Per door cassette serial number |
| LM3-EV-HVAC-110 | HVAC cooling and drain test | G6 static complete | +50 C performance evidence may be supplier lab data |
| LM3-EV-INT-115 | Interior moulding, fitout and service-access report | G6 static complete | Fire trace, dry-fit/gap/rattle/sharp-edge results, floor/PRM evidence and sequential service-removal demonstrations |
| LM3-EV-BRK-120 | Static brake and park-brake test | G6 static complete | Links to bogie/brake supplier records |
| LM3-EV-MASS-130 | Weighing and axle-load report | G7 dynamic ready | Empty and simulated AW2/AW3 cases |
| LM3-EV-RIDE-140 | Bogie alignment and ride-height report | G7 dynamic ready | Before dynamic testing |
| LM3-EV-REC-150 | Jacking, lifting and field-rerailing interface report | Recovery release | Individual-car mass/CG cases, structural proof, equipment freeze, four-point gauge, asymmetric/loss-of-pressure trials and trained-crew demonstration |
| LM3-EV-FEM-175 | Train-to-train joint FEM screening pack | Optional open-end release | Train-to-train joint vertical and train-to-train joint lateral/racking beam-model screens |

## Supplier document index

| Package | Supplier document required | Acceptance rule |
|---|---|---|
| Doors | Installation manual, maintenance manual, lifecycle test, EN 14752 evidence | Fits LM3-DOOR-200 without primary steel change |
| Windows | Glazing certificate, adhesive/gasket procedure, replacement manual | Fits LM3-WIN-210 and passes water test |
| HVAC | Datasheet, +50 C derating curve, wiring manual, refrigerant record | Fits LM3-HVAC-220 and aux-power budget |
| One-metre GFRP body modules | Mould split/datum drawings, laminate schedule, fire test, cure record, CNC trim report, repair manual, insert pull-out data, seal/gasket procedure | Modules remain non-structural, clipped and gasketed to LM3-BDY-160 without side/roof production adhesive |
| Fiberglass end cowls | Mould split/trim drawings, laminate coupons, fire test, insert pull-out data, gasket/seal procedure, repair manual | Same cast kit fits both A-end and B-end without steel-frame change |
| Rail livery film | Rail-use statement, film/ink/overlaminate/edge-system data, substrate/application/cleaning limits and fire evidence | Fits LM3-FIN-240 seams and keep-outs, adheres to the actual cured base finish, and passes repair/removal trial |
| Radiative roof coating | Controlled formulation, fire/chemical/material compatibility, application limits, new/aged optical and durability evidence | May be used only within LM3-FIN-245 trial zones after accepted one-car disposition; qualified light base finish is the fallback |
| Configurable train-end interface | End carrier ring drawing, option bolt-grid gauge, panoramic/open-mid configuration procedure, seal/drain test, selected-option record | Each end position selects exactly one of the panoramic glass end or the mid open train-to-train connection |
| Seats/rails | Fire certificate, pull-load certificate, cleaning/repair manual | Fits LM3-INT-230 insert grid |
| Lighting/PIS/CCTV/intercom | EMC/vibration evidence, firmware version, wiring manual | Enumerates on car network and passes static test |
| Battery | Cell/module certificate, BMS manual, vent/fire containment data | Fits LM3-BDY-140 and LM3-HV-310 |
| Traction and charging | Motor/controller/gearbox datasheets, station DC-charge interface data, onboard HV protection/IMD data, PV MPPT data, cooling and EMC instructions | Fits LM3-TRC-500, LM3-HV-320, and LM3-HV-325 |
| Rooftop solar and air cleaner | PV module datasheets, adhesive/bond process, rail/clamp vibration evidence, fire-isolation switch data, blower/nozzle IP and vibration evidence, filter-service access, soiling-recovery test | Fits LM3-HV-325 without roof-spaceframe redesign |
| Bogie parts | Wheelset, bearing, spring, damper, brake supplier certificates | Fits LM3-BOG-400/410 |
| Articulation/gangway | Bearing rating, motion-envelope proof, bellows/turntable fire evidence, maintenance manual | Fits LM3-SYS-170 and optional LM3-SYS-175 without carbody adapter redesign |

## Release gates

| Gate | Minimum drawing/evidence state |
|---|---|
| v2A design freeze | LM3-EV-CFG-000 and LM3-EV-DIM-058 complete; all controlled drawings issued at rev A; supplier envelopes frozen |
| First steel cut | LM3-BDY-100/110/120, LM3-EV-MAT-001, LM3-EV-WLD-010 complete |
| First carbody shell complete | LM3-EV-WLD-020, LM3-EV-DIM-030, LM3-EV-COR-040 complete |
| First COTS fit-out complete | Door/window/HVAC/interior/film supplier docs accepted; LM3-EV-GLZ-065, LM3-EV-LMP-067, LM3-EV-WTR-070, LM3-EV-FIN-075 and LM3-EV-INT-115 complete |
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
