# Assembly and joining plan — `light-metro-3car`

This plan answers the shop-floor question: do the parts and
subassemblies actually connect, and how are they joined?

The current product tree is connected by parent/child IDs in the
generated buildable manifest:
[`design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.md`](../../../design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.md).
This document adds the missing single-page join doctrine: datum stack,
joining method, sequence, and acceptance hold point for each
subassembly and final-assembly interface.

The machine-readable parent/child join classes, torque authority, and
release state are generated in
[`joint-control-schedule.md`](../../../design/component-catalogue/catalog/buildable-trainset/joint-control-schedule.md).

It is still a v0.2/v2A planning document, not a released shop drawing.
Every structural weld, bolted joint, adhesive bond, HV connection, and
coolant joint still needs a released interface-control drawing, the
numeric torque or supplier procedure required by the joint schedule, a
weld map, surface-preparation procedure, and signed traveler before first
article build.

## Join-class rules

Use the least exotic joint that preserves structure, inspection, and
serviceability:

| Join class | Used for | Default method | Release evidence |
|---|---|---|---|
| Structural weld | Primary steel underframe, side frames, bolsters, coupler pockets, end rings, bogie frames | Fixture tack, WPS-controlled MIG/MAG weld, controlled cool/stress relief where required, post-weld machining of critical datums | Material heat trace, WPS/WPQR, welder ID, weld map, VT plus MT/UT where classed, post-weld datum survey |
| Bolted structural datum | Bogie marriage, coupler/crash absorber, articulation bearings, door cassette frames, HVAC curbs, battery trays | Classed fasteners into machined pads/weld nuts/captive inserts; shim only at released shim packs; torque stripe after final torque | Bolt grade certificate, torque record, locking method, shim map, witness marks, re-torque rule |
| Qualified adhesive/bonded interface | Glazing lands, selected non-service cowl seams, PV bonded pads, and supplier-required local seams; not LM3-BDY-160 side/roof modules | Abrade/clean/prime, controlled adhesive batch and pot life, clamped cure, witness coupon where required | Surface-prep record, adhesive batch/shelf-life, cure time/temperature, coupon/pull evidence, water/leak test |
| Gasketed removable panel | One-metre GFRP side/roof modules, cowl hatches, skirts, service covers, battery access lids, and roof fairings | Keyed hooks, captive clips, retained fasteners, or quarter-turn retainers with continuous gasket and drain path | Insert pull-out, fastener retention, gasket compression witness, clip/anti-lift witness marks, water test, service-removal check |
| Electrical / data | HV battery, inverter, charge rack, roof PV, TCN-E, CAN-FD, safety loop, door and HVAC looms | Keyed connectors, HVIL where HV, segregated clipped routing, bonding jumpers, strain relief and service loops | Continuity, insulation resistance, HVIL, bond continuity, network enumeration, bend-radius and clamp-pitch inspection |
| Fluid / thermal | Battery/inverter coolant, HVAC drains, washer tubes, fire suppression interfaces | Quick-disconnects or compression fittings on supported pipe/hose; no unsupported hose spans across moving joints | Pressure/leak test, drain-flow test, rub/chafe inspection, service isolation procedure |

## Assembly datum stack

Build from hard datums outward:

1. Track/fixture centreline.
2. Underframe centre spine and bogie-centre datums.
3. Side-frame door/window aperture datums.
4. Roof rail and HVAC/PV datum plane.
5. End-ring, coupler face, and cowl glass/sensor datums.
6. Systems routing datums: HV, LV/data, coolant, drains.
7. Passenger-facing trim and service covers.

No supplier module may force rework of an upstream structural datum.
If a supplier envelope does not fit the frozen datum, the accepted
actions are: released shim pack, adapter bracket revision, or supplier
alternate. Grinding/drilling a released primary datum in final assembly
is a nonconformance.

## Subassembly connection plan

| Node | Connects to parent by | Critical parent datum | Acceptance hold point |
|---|---|---|---|
| `LM3-BDY-SA110` underframe datum weldment | WPS-controlled welds between side sills, centre spine, cross bearers, bolsters, coupler pockets, and tray rails; post-weld machined bogie/coupler datums | Fixture centreline, bogie centres, coupler pocket centre plane | Material release, fixture tack survey, weld/NDT release, post-weld datum survey |
| `LM3-BDY-SA120` carbody spaceframe | Welded/bolted side frames and roof bows onto underframe datum pads; door/window portal reinforcement tack-welded before closure | Door aperture planes, window carrier rings, roof-rail pitch | Door/window aperture survey, roof rail survey, carbody dimensional report |
| `LM3-SHELL-A200` painted frame and body skin | Corrosion-protected steel frame plus moulded 1 m clip-on GFRP side/roof modules, glazing lands, and removable skirt/cowl interfaces | Painted steel clip rails, window apertures, end-ring cowl datum | Corrosion report, mould/cure/coupon records, sealed-edge record, clip/anti-lift witness map, eight-hour route record, water-ingress pre-test; cure record only for glazing/cowl seams |
| `LM3-WIN-SA320` side glazing cassette | Bonded or gasketed laminated-glass cassette into `LM3-BDY-P110` carrier ring; mechanical anti-drop retention where supplier requires | Window carrier ring and primer/bond land | Aperture gauge, bond/gasket procedure, water-ingress test |
| `LM3-DOOR-SA310` door cassette | Bolted COTS door cassette into `LM3-BDY-P100` portal frame with shim pack, threshold beam, drains, closed/locked loop, and emergency release | Door portal plane, sill height, lock-loop bracket | Door gauge fit, obstruction test, closed-and-locked test |
| `LM3-INT-SA330` interior fit-out | FRP/phenolic liners and battery strake covers on potted inserts, clip grids, retained fasteners, and limited non-service adhesive/sealant; lighting/PIS/CCTV plugs into LV looms | Saloon floor datum, ceiling rail, window reveal datum, PRM aisle gauge | Egress check, fire-material pack, liner/trim fit survey, lighting/PIS/CCTV static test |
| `LM3-ROOF-SA410` roof systems | HVAC bolted to gasketed roof curb; PV modules either bonded to prepared pads or clamped to raised rails; antennas/lights through sealed glands; bonding jumpers to roof earth studs | Roof rail pitch, HVAC curb plane, PV keep-out zones, cable-gland locations | Roof leak test, HVAC drain test, PV isolation/bonding check |
| `LM3-HV-SA510` traction/HV/cooling | Battery packs bolted into under-seat trays with isolation mounts; inverter/charge rack bolted to underframe rails; HV cables in covered trays; coolant quick-disconnects and supported pipes | Battery tray rail, HV segregated route, side-pin charger datum, coolant manifold support | HVIL test, insulation resistance, coolant pressure test, first-energisation release |
| `LM3-BOG-SA610` powered bogie | Welded H-frame plus bolted wheelsets, bearings, primary suspension, brake hardware, traction motors, gearbox, torque links, and earth straps | Bogie frame pivot, axle centres, motor-cradle datums | Frame NDT, wheelset/bearing certificate, motor/gearbox alignment, static brake test |
| `LM3-BOG-SA620` trailer bogie | Welded H-frame plus bolted wheelsets, bearings, suspension, brake package, wear plates, and height-setting shims | Bogie frame pivot, axle centres, air-spring pad plane | Frame NDT, wheelset/bearing certificate, ride-height setup, static brake test |
| `LM3-CWL-SA710` fiberglass cowl cast kit | FRP cowl shell dry-built on cowl fixture; potted/captive inserts; bolted removable hatches; adhesive/sealant only at non-service sealing surfaces | Backing-ring flange, glass carrier land, lamp/sensor hatch datum | Laminate coupon release, insert pull-out, trim/drill survey, A/B-end dry-build water test |
| `LM3-END-SA700` train-end assembly | Coupler/crash absorber bolted into steel pocket; end ring/anti-climber bolted/welded to carbody datum; cowl kit bolted/gasketed to backing ring; sensors/lights bolted to datum brackets | Coupler face, anti-climber datum, cowl backing ring, sensor optical/radar datum | A/B end interchange, coupler datum survey, sensor calibration, recovery interface check |
| `LM3-ART-SA800` articulation/gangway | Lower spherical bearing and drawbar pinned/bolted to underframe anchor castings; upper links bolted to end frames; bellows clamp frames bolted/gasketed; service bundles through drag-chain | Inter-car joint centre, yaw/pitch/roll envelope, trainline bend-radius route | Motion-envelope proof, trainline continuity, water-ingress/drain test |
| `LM3-SYS-SA900` train control/electronics | T-ECU/A and cabinets bolted to DIN/cabinet rails; TCN-E/CAN/safety-loop connectors plugged and labelled; firmware/configuration loaded after harness continuity | LV cabinet rail, trainline backbone, event-recorder access | Network enumeration, firmware record, self-test, event-recorder write/read test |
| `LM3-CAR-A900` complete car | Shell receives doors, windows, roof, interior, HV, powered bogie, and trailer bogie; bogies married through centre pivot/air springs/yaw dampers; all earth bonds closed before energisation | Carbody bogie centres, ride-height datum, door/platform datum, HV isolation boundary | Car weigh, door/HVAC/static systems test, bogie marriage report, low-speed yard movement |
| `LM3-TRAINSET-A000` trainset | Three complete cars joined with two semi-permanent articulations; A/B end assemblies installed at outer ends; train-control network configured across the consist | Train centreline, articulation centres, coupler faces, trainline continuity | Trainset weigh, static brake/door/HVAC/HV tests, FEM screening accepted, dynamic-test release |

## Final assembly route

### 1. Release child subassemblies

- Confirm every child assembly has a signed traveler, accepted material
  pack, and matching revision in the manifest.
- Quarantine any COTS module whose supplier envelope, mass, connector,
  or evidence pack does not match the interface-control drawing.
- Stage A-car, B-car, C-car kits separately. The cars are repeated, but
  the outer-end fit-out is only installed on the two trainset ends.

### 2. Build and release each car module

1. Put `LM3-SHELL-A200` on leveled stands using the underframe datum.
2. Install `LM3-DOOR-SA310` and `LM3-WIN-SA320`; complete water and
   door-loop tests before interior trim blocks access.
3. Install `LM3-ROOF-SA410`; close roof leak, drain, PV isolation, and
   roof-bonding checks.
4. Install `LM3-HV-SA510`; leave HV locked out until bond continuity,
   coolant pressure, and insulation tests pass.
5. Install `LM3-INT-SA330`; prove PRM aisle, hatch access, fire-label,
   rattle, and egress checks.
6. Marry `LM3-BOG-SA610` and `LM3-BOG-SA620` to the carbody. Set ride
   height and record shim packs.
7. Weigh the car and complete low-speed yard movement before it enters
   trainset assembly.

Each one-metre side/roof body module is already moulded, cured, demoulded,
CNC-trimmed, edge-sealed, fitted with inserts/clips/gaskets, labelled, and
dry-fitted to a master frame before the car reaches final assembly. Installation
then follows the LM3-BDY-160 dry cycle: clean and inspect the datum rail, fit
the EPDM seal, engage the asymmetric hook, close captive clips, engage the
independent anti-lift retainer, and record the visible witness marks. Six
two-person crews install the 144 modules across three released frames in one
eight-hour shift. Glazing and end-cowl non-service seams retain their separate
qualified adhesive cycles. No clip or fastener may pull an out-of-tolerance
frame or panel into position.

### 3. Join the three-car consist

1. Place Car A, Car B, and Car C on level track with coupler/articulation
   centres on the train centreline.
2. Confirm the end-interface configuration record for each end position:
   the reference three-car trainset selects panoramic glass at the two
   outer ends and open mid connections only at internal or train-to-train
   joints.
3. Install `LM3-ART-SA800` between A-B and B-C:
   - pin/bolt lower drawbar and spherical bearing;
   - install anti-lift keeper;
   - install upper roll/yaw/pitch links;
   - fit bellows clamp frames and turntable floor;
   - route HV, LV/data, coolant, HVAC sleeve, and drains through the
     released drag-chain path.
4. Perform articulation yaw/pitch/roll sweep before connecting final
   trim covers.
5. Complete trainline continuity, safety-loop, Ethernet ring, coolant
   pressure, and water/drain tests across both joints.

### 4. Select and install end assemblies

1. Survey `LM3-EIF-SA650`, the common configurable end-interface set,
   before fitting any end dress-out.
2. For a panoramic outer end, install `LM3-END-SA700`.
3. Bolt coupler/crash absorber into the steel pocket and torque stripe.
4. Fit fiberglass cowl kit to the backing ring with gasketed retained
   fasteners; seal only at released non-serviceable seams.
5. Install panoramic glass, lamps, T-OBS sensors, washer/heater lines,
   rescue cabinet, and electrical jumper.
6. Survey coupler face and sensor datum. Do not use cowl shimming to
   compensate for coupler-pocket error.
7. For a train-to-train open mid connection, do not install the panoramic
   cowl/glass/sensor stack. Install `LM3-TTART-SA850` only after the two
   train modules are aligned on the final assembly track, then fit the
   open portal clamp frame, bellows, threshold bridge, turntable,
   service-jumper cassette, drain trays, and blanking/transition covers.
8. Complete the train-to-train motion sweep, threshold level check,
   trainline continuity, service segregation, and water/drain test before
   closing passenger trim.

### 5. Configure train control and perform static tests

- Install `LM3-SYS-SA900` cabinets and train-control equipment.
- Enumerate TCN-E devices car by car, then end to end.
- Load firmware/configuration and record hashes.
- Run static brake, door, HVAC, charger, roof-PV isolation, HVIL,
  event-recorder, passenger information, CCTV/intercom, and emergency
  release tests.

### 6. FEM/static proof gates before running

Before dynamic running, release the FEM/static screens for:

- underframe supported at bogie interfaces;
- coupler pocket and crash-load path;
- bogie frame and motor cradle;
- battery tray/service-lid rails;
- door portal and threshold;
- roof equipment rails/PV mounts;
- articulation anchor brackets;
- train-to-train open joint vertical and lateral/racking loads if
  `LM3-TTART-SA850` is selected.

Any screen above the service-stress threshold or with local joint
stress concentration requires a detailed local model and drawing
revision before the trainset leaves the commissioning cell.

### 7. Dynamic running release

Run in this order:

1. Low-speed yard movement: 0-10 km/h propulsion, brake apply/release,
   door inhibit, and emergency-stop checks.
2. Articulation sweep on curves and vertical transitions.
3. Brake bedding and static-to-dynamic brake correlation.
4. Charger docking at the standard side-pin interface, including two-train
   shared-cabinet arbitration and emergency isolation.
5. Roof PV charge acceptance and isolation under motion/dwell states.
6. Passenger-systems shake/rattle check.
7. Fault-injection run: door interlock fault, HVIL open, TCN device missing,
   charger abort, battery off-gas, failed mist pump/flow, and obstacle-
   detection degraded state.

Release to trial running only after the signed trainset traveler,
FEM/static proof pack, NCR closure list, and as-built interface-control
drawings agree.

## Open release gaps

- Join class, torque authority, and release state are emitted for every
  product-tree integration joint; numerical torques still require the
  named supplier instruction or released joint calculation.
- Weld symbols/classes exist as process intent, but not as released
  dimensioned drawings.
- Adhesive bead dimensions, open time, clamp plan, and cure fixtures
  need supplier-specific procedures.
- Electrical harness clamp coordinates and coolant support coordinates
  need a released routing drawing.
