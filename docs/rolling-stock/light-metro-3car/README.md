# `light-metro-3car` trainset package

This directory holds the dimensioned specification for the
**light-metro-3car** trainset — the Samawah reference family per
[RFC 0003](../../rfcs/0003-samawah-reference-deployment.md) and the
default for populations 300 k – 1 M per [RFC 0008 §5](../../rfcs/0008-rolling-stock-reference-design.md#5-family-selection-policy).

This package started as the v1 RFC 0008 bid specification and now
also links the current envelope-level FreeCAD/PNG outputs. A domestic
rolling-stock fabricator can read the dimensions, masses, interfaces,
sub-assembly tree, fabrication sequence, procurement BOM skeleton, and
design-review CAD. The design deliberately favours a modern low-capex
factory: COTS rail subsystems wherever possible, simple cut/bend/weld
fabrication for the primary frame, and composite non-structural panels
for sides, roof fairings, multi-part fiberglass cabless cowls, and
interior liners.

## Contents

| File | Scope |
|---|---|
| [`general-arrangement.md`](general-arrangement.md) | Overall envelope, gauge clearance, consist diagram, floor heights, door positions |
| [`fabrication-plan.md`](fabrication-plan.md) | Cut-bend-weld primary structure, composite cladding, COTS module installation sequence |
| [`bogie.md`](bogie.md) | 2-axle standard bogie spec, wheel profile, suspension, brake mount |
| [`body.md`](body.md) | Welded steel underframe/spaceframe, composite side panels, end bulkheads, articulation interface frames |
| [`end-cowl.md`](end-cowl.md) | Identical A/B-end fiberglass cowl kit, cast split, laminate/tooling rules, glazing/sensor interfaces |
| [`articulation.md`](articulation.md) | Inter-car articulation/gangway module: lower spherical pivot, upper links, bellows, turntable, trainline routing |
| [`cots-integration.md`](cots-integration.md) | COTS/fabricated interface diagrams, part delineation, and assembly sequence |
| [`traction.md`](traction.md) | PMSM motor + SiC inverter + reduction gear, rooftop PV, dual-input battery charge inverter, adhesion budget |
| [`interfaces.md`](interfaces.md) | Coupler, station charging, articulation, platform gap, TCN-E connector, aux power |
| [`bom-skeleton.md`](bom-skeleton.md) | Procurement BOM lines and marketplace listed-price consist totals |
| [`marketplace-price-anchors.md`](marketplace-price-anchors.md) | Alibaba/AliExpress line-by-line price anchors and qualification caveats |
| [`compliance.md`](compliance.md) | Standards matrix: EN 15227, EN 45545, EN 14363, EN 50155, ISO 3095, EN 12299 |
| [`drawing-register.md`](drawing-register.md) | v2 drawing IDs, supplier documents, inspection evidence, release gates |
| [`v2-release-checklist.md`](v2-release-checklist.md) | Fabrication-release gates: supplier envelopes, FEA, weld maps, drawings, NC data, harness routing, first-article evidence |

The governing visual/layout reference is
[`solar-metro-trainset.png`](../../../docs/assets/solar-metro-trainset.png):
white/silver body, green waist band, dark skirts, single dark panoramic-glass ends,
mixed bonded/rail-mounted roof PV, two low-floor door pairs per side per car, powered end cars, unpowered middle car,
and batteries under longitudinal seats. The end glazing is an open
driverless passenger view through heated RF-transparent laminated
glass with LED headlamp and marker-light clusters below it.
Because the cars use
standard bogies, each car has ~3 m high-floor end decks over the bogies
and a 350 mm, ~10 m low-floor centre door/PRM zone.
The front and rear passenger ends are not walled off by cab bulkheads;
the end saloon looks through the single panoramic glass pane at both ends
of the driverless train. The front/back exterior module is the same
multi-part fiberglass cast kit at both ends; its controlled design is
in [`end-cowl.md`](end-cowl.md).

The companion production graphic is
[`solar-metro-production-assembly.png`](../../../docs/assets/solar-metro-production-assembly.png).
It shows the intended manufacturing story: a welded 17 m datum frame,
bolt/bond COTS side, roof, door, glazing, battery-seat, and HVAC
modules, then lower the car onto standard bogies and repeat the module
to make the consist.

COTS passenger-facing modules are controlled by the supplier-neutral
envelope catalogue at
[`hardware/trainset-interiors/cots-catalogue.md`](../../../hardware/trainset-interiors/cots-catalogue.md).
The current vendor-fit shortlist is captured in
[`bom-skeleton.md`](bom-skeleton.md#vendor-fit-in-references) and names
rail product families for doors, windows, HVAC, flooring, seats,
lighting, PIS/audio, batteries, traction motors, brakes, couplers, and
front/back sensing while keeping the CAD envelope swap-friendly.

## Canonical Parametric Source

The parametric Python source files are the design basis for envelopes,
interfaces, and generated review views. The styled fiberglass end-cowl
A-surfaces are controlled by the surface-modelled LM3-BDY-155 release
CAD described in [`end-cowl.md`](end-cowl.md); those surfaces are
exported back into the drawing pack as neutral CAD.

| Source | Controls |
|---|---|
| [`trainset.py`](../../../mechanical-py/src/osr_mech/rolling_stock/trainset.py) | Family length, car count, motorisation, cowl/body/bogie assembly |
| [`car_body.py`](../../../mechanical-py/src/osr_mech/rolling_stock/car_body.py) | 17 m body module as layered CAD subassemblies: primary structure, exterior/glazing/doors, interior, HVAC ducts, LV/data routing, HV/PV/thermal/fire paths |
| [`sensor_cowl.py`](../../../mechanical-py/src/osr_mech/rolling_stock/sensor_cowl.py) | Identical A/B-end multi-part fiberglass cowl kit envelope with one dark panoramic glass pane, LED headlamps, marker lights, and T-OBS visual interface |
| [`systems.py`](../../../mechanical-py/src/osr_mech/rolling_stock/systems.py) | Couplers, detailed articulations/gangways, batteries, rooftop solar package, charge inverters, doors, electronics, charging, T-OBS packs |
| [`bogie/`](../../../mechanical-py/src/osr_mech/rolling_stock/bogie/) | Powered and converted-trailer bogie assemblies |
| [`cad_templates/rolling_stock.py`](../../../mechanical-py/src/osr_mech/cad_templates/rolling_stock.py) | Sheet-metal/chassis manufacturing templates |

## Current CAD / PNG Design Outputs

The whole-train part map and COTS interface diagrams are in
[`cots-integration.md`](cots-integration.md).

The present train design now has envelope-level definitions for the
major train assemblies, sub-assemblies, repeated components, and
body service layers. The `car_body()` assembly is deliberately nested
as components -> subassemblies -> final car body, so CAD review can
hide/show the primary steel shell, exterior solar-train skin, passenger
interior, HVAC ducting, LV/data harnesses, high-voltage traction/PV
routing, thermal-management pipes, and battery fire vent paths. The
models are supplier-neutral CAD geometry in
[`mechanical-py/src/osr_mech/rolling_stock`](../../../mechanical-py/src/osr_mech/rolling_stock)
and render to these design-review PNGs:

| Output | Scope |
|---|---|
| [`trainset-light-metro-3car.png`](../../../docs/screenshots/trainset-light-metro-3car.png) | Final 3-car trainset assembly with car bodies, bogies, single panoramic-glass cowls, couplers, inter-car articulation, and train systems |
| [`end-glass-cowl.png`](../../../docs/screenshots/end-glass-cowl.png) | Cabless trainset end close-up with multi-part fiberglass cowl casts, one heated laminated panoramic glass pane, bonded edge frame, demist busbars, and washer/service hardware |
| [`trainset-car-detail.png`](../../../docs/screenshots/trainset-car-detail.png) | 17 m layered car body: structure, door/window openings, glazing, livery, roof PV/HVAC, interior, ducts, LV/data and HV/thermal routes |
| [`trainset-car-body-structure.png`](../../../docs/screenshots/trainset-car-body-structure.png) | Primary fabricated structure: shell, 10 m low-floor pan, side sills, crossmembers, roof cantrails, door portals, window posts, end rings, and bogie clearance envelopes |
| [`trainset-car-body-bogie-subassembly.png`](../../../docs/screenshots/trainset-car-body-bogie-subassembly.png) | Single-car structure with standard motor/trailer bogies under the ~3 m raised high-floor end zones |
| [`trainset-car-body-exterior.png`](../../../docs/screenshots/trainset-car-body-exterior.png) | Solar-train exterior layer: glazing, door leaves, livery band, mixed bonded/rail-mounted roof PV/HVAC, and service skirts |
| [`trainset-roof-solar-system.png`](../../../docs/screenshots/trainset-roof-solar-system.png) | Per-car rooftop solar package with bonded flexible laminates, raised rigid panels, rails, clamps, junction boxes, fire isolators, MPPT combiner, and downlink gland |
| [`trainset-car-body-interior.png`](../../../docs/screenshots/trainset-car-body-interior.png) | Passenger interior layer: under-seat battery strakes, benches, PRM bays, grab poles, handrails, and PIS |
| [`trainset-car-body-services.png`](../../../docs/screenshots/trainset-car-body-services.png) | Service layers: HVAC ducts, LV/data trays, lighting, CCTV/intercoms, HV/PV routing, coolant, and battery fire vents |
| [`trainset-interior-fit-out.png`](../../../docs/screenshots/trainset-interior-fit-out.png) | COTS passenger fit-out envelopes inside the car body |
| [`trainset-body-sheet-metal-kit.png`](../../../docs/screenshots/trainset-body-sheet-metal-kit.png) | Sheet-metal/chassis manufacturing kit: underframe, bolsters, coupler pockets, side posts, rails, roof bows, end rings |
| [`trainset-car-systems.png`](../../../docs/screenshots/trainset-car-systems.png) | One self-contained car systems package: four door cassettes, platform interlocks, batteries, rooftop PV package, traction/charge power rack, charging connector, and accessibility/safety reservations |
| [`trainset-battery-pack.png`](../../../docs/screenshots/trainset-battery-pack.png) | Eight sodium-ion module envelopes plus HV contactor, fuse, and BMS cabinet per car |
| [`trainset-door-system.png`](../../../docs/screenshots/trainset-door-system.png) | Door cassette pair with sill gap fillers, locks, and external emergency releases |
| [`trainset-electronics-cabinet.png`](../../../docs/screenshots/trainset-electronics-cabinet.png) | Per-end T-ECU/S, T-ECU/A, and crashworthy event recorder, two sets per trainset |
| [`trainset-end-coupler.png`](../../../docs/screenshots/trainset-end-coupler.png) | Scharfenberg Type 10 coupler, electric-head carrier, and EN 15227 crash absorber envelope |
| [`trainset-inter-car-articulation.png`](../../../docs/screenshots/trainset-inter-car-articulation.png) | Detailed inter-car articulation: lower spherical joint, anti-lift keeper, upper links, double-wall bellows, turntable floor, trainline routing, and kinematic envelopes |
| [`trainset-tobs-sensor-pack.png`](../../../docs/screenshots/trainset-tobs-sensor-pack.png) | T-OBS LIDAR, mmWave radar, stereo camera, and ultrasonic sensor envelopes |
| [`bogie-motor.png`](../../../docs/screenshots/bogie-motor.png) | Powered bogie assembly with frame, wheelsets, motors, gearboxes, suspension, and brakes |
| [`bogie-trailer.png`](../../../docs/screenshots/bogie-trailer.png) | Trailer bogie assembly using the common frame and suspension envelope |

## FreeCAD Assembly And FEA Screenshot Review

These screenshots are generated from the FreeCAD `.FCStd` review
documents and the FreeCAD/CalculiX screening-output document. The
assembled and exploded states are view groups in the FreeCAD files, not
separate hand-positioned drawings.

| Trainset FreeCAD review |
|---|
| ![FreeCAD trainset light metro 3-car](../../../docs/screenshots/freecad/freecad-trainset-light-metro-3car.png) |

| Chassis + bogie assembled | Chassis + bogie exploded |
|---|---|
| ![Chassis bogie assembled](../../../docs/screenshots/freecad/freecad-chassis-bogie-assembled.png) | ![Chassis bogie exploded](../../../docs/screenshots/freecad/freecad-chassis-bogie-exploded.png) |

| Full body assembled | Full body exploded |
|---|---|
| ![Full body assembled](../../../docs/screenshots/freecad/freecad-full-body-assembled.png) | ![Full body exploded](../../../docs/screenshots/freecad/freecad-full-body-exploded.png) |

| FEA screening models | Chassis FEA | Bogie FEA | Body FEA |
|---|---|---|---|
| ![FEA screening models](../../../docs/screenshots/freecad/freecad-fea-screening-models.png) | ![Chassis FEA](../../../docs/screenshots/freecad/freecad-fea-chassis-bogie-screen.png) | ![Bogie FEA](../../../docs/screenshots/freecad/freecad-fea-bogie-frame-screen.png) | ![Body FEA](../../../docs/screenshots/freecad/freecad-fea-full-body-frame-screen.png) |

The actual solver-result PNGs below are generated from CalculiX
`.dat` fields: deformed beam shape, support/load markers, and von Mises
stress colour scale.

| Chassis service gravity | Chassis AW3 proof | Chassis track twist |
|---|---|---|
| ![Chassis service FEA result](../../../docs/screenshots/freecad/freecad-fea-chassis-bogie-screen-result.png) | ![Chassis AW3 proof FEA result](../../../docs/screenshots/freecad/freecad-fea-chassis-aw3-proof-screen-result.png) | ![Chassis track twist FEA result](../../../docs/screenshots/freecad/freecad-fea-chassis-track-twist-screen-result.png) |

| Bogie vertical | Bogie brake/traction | Full body vertical | Full body lateral sway |
|---|---|---|---|
| ![Bogie vertical FEA result](../../../docs/screenshots/freecad/freecad-fea-bogie-frame-screen-result.png) | ![Bogie brake traction FEA result](../../../docs/screenshots/freecad/freecad-fea-bogie-brake-traction-screen-result.png) | ![Full body vertical FEA result](../../../docs/screenshots/freecad/freecad-fea-full-body-frame-screen-result.png) | ![Full body lateral sway FEA result](../../../docs/screenshots/freecad/freecad-fea-full-body-lateral-sway-screen-result.png) |

The latest screening summary is
[`mechanical-py/catalog/fea/screening-summary.md`](../../../mechanical-py/catalog/fea/screening-summary.md).
The source FreeCAD review documents are catalogued in
[`mechanical-py/catalog/freecad/README.md`](../../../mechanical-py/catalog/freecad/README.md),
and raw CalculiX output folders are catalogued in
[`mechanical-py/catalog/fea/README.md`](../../../mechanical-py/catalog/fea/README.md).
After the low-floor chassis rework, the chassis screen is inside the
25 mm deflection target: 11.3 mm maximum displacement under the 360 kN
service-load screen. The broadened lateral body sway screen currently
flags review: 21.8 mm displacement against the 20 mm screening target,
with stress still low at 38.3 MPa.

## Mechanical Interface Component Gallery

These component images are generated from
[`mechanical_interfaces.py`](../../../mechanical-py/src/osr_mech/rolling_stock/mechanical_interfaces.py)
and match the tracked FreeCAD assembly-review documents under
[`mechanical-py/catalog/freecad/`](../../../mechanical-py/catalog/freecad/).

| Bogie to chassis | Bogie to motor | Low-floor chassis |
|---|---|---|
| ![Bogie to chassis connector](../../../docs/screenshots/rolling-stock/interfaces/bogie-to-chassis-connector.png) | ![Bogie to motor connector](../../../docs/screenshots/rolling-stock/interfaces/bogie-to-motor-connector.png) | ![Low-floor chassis](../../../docs/screenshots/rolling-stock/interfaces/low-floor-chassis.png) |

| Side body frame | Composite body and roof | Window installations |
|---|---|---|
| ![Side body frame attachments](../../../docs/screenshots/rolling-stock/interfaces/side-body-frame-attachments.png) | ![Composite body roof attachments](../../../docs/screenshots/rolling-stock/interfaces/composite-body-roof-attachments.png) | ![Window installations](../../../docs/screenshots/rolling-stock/interfaces/window-installations.png) |

| Door mounts | Door design | Door installations |
|---|---|---|
| ![Door mounts](../../../docs/screenshots/rolling-stock/interfaces/door-mounts.png) | ![Door design](../../../docs/screenshots/rolling-stock/interfaces/door-design.png) | ![Door installations](../../../docs/screenshots/rolling-stock/interfaces/door-installations.png) |

| Door to body | Cabin flooring | Battery installations |
|---|---|---|
| ![Door to body installations](../../../docs/screenshots/rolling-stock/interfaces/door-to-body-installations.png) | ![Cabin flooring](../../../docs/screenshots/rolling-stock/interfaces/cabin-flooring.png) | ![Battery installations](../../../docs/screenshots/rolling-stock/interfaces/battery-installations.png) |

| Benches over batteries | Internal lighting | HVAC roof and ducting |
|---|---|---|
| ![Bench on battery installations](../../../docs/screenshots/rolling-stock/interfaces/bench-on-battery-installations.png) | ![Internal lighting installation](../../../docs/screenshots/rolling-stock/interfaces/internal-lighting-installation.png) | ![HVAC roof ducting installation](../../../docs/screenshots/rolling-stock/interfaces/hvac-roof-ducting-installation.png) |

| Screens and speakers | External lighting and LIDAR | Train connector mounts |
|---|---|---|
| ![Screen speaker mountings](../../../docs/screenshots/rolling-stock/interfaces/screen-speaker-mountings.png) | ![External lighting and LIDAR](../../../docs/screenshots/rolling-stock/interfaces/external-lighting-lidar-system.png) | ![Train connector mounts](../../../docs/screenshots/rolling-stock/interfaces/train-connector-mount-pair.png) |

| Complete mechanical interface package |
|---|
| ![Complete mechanical interface package](../../../docs/screenshots/rolling-stock/interfaces/mechanical-interface-package.png) |

The tracked generated CAD review artifacts are:
[`trainset-light-metro-3car.FCStd`](../../../mechanical-py/catalog/freecad/trainset-light-metro-3car.FCStd),
[`chassis-bogie-assembly-states.FCStd`](../../../mechanical-py/catalog/freecad/chassis-bogie-assembly-states.FCStd),
[`full-body-assembly-states.FCStd`](../../../mechanical-py/catalog/freecad/full-body-assembly-states.FCStd), and
[`fea-screening-models.FCStd`](../../../mechanical-py/catalog/freecad/fea-screening-models.FCStd).
The matching electronics host-class quantities are mirrored in
[`hardware/rolling-stock-integration.md`](../../../hardware/rolling-stock-integration.md).

The remaining gaps are not missing assemblies in the train envelope;
they are v0.2/v2 detail-design tasks: supplier exact envelopes, weld
maps, FEA-ready brackets, harness clamp locations, manufacturing
tolerances, and release drawings listed in
[`drawing-register.md`](drawing-register.md) and
[`v2-release-checklist.md`](v2-release-checklist.md).

## Reference envelope (from RFC 0008 §1)

| Parameter | Value |
|---|---|
| Cars | 3 (articulated) |
| Overall length (over couplers) | 51.0 m |
| Tare mass target | 98 t |
| Axle load (AW3 crush) | ≤ 14 t |
| Max speed | 25 m/s (90 km/h) |
| Seats | 60 longitudinal seats |
| Passenger capacity (AW2) | 360 (seated + standing) |
| Passenger capacity (AW3 crush) | 480 short-duration crush load |
| Onboard battery | 450 kWh Na-ion (150 kWh per car, under seats) |
| Peak onboard motor output | 600 kW |
| Floor height (above ToR) | 350 mm, ~10 m low-floor centre door/PRM zone; 760 mm, ~3 m high-floor end decks over standard bogies |
| Gauge | 1 435 mm standard gauge |

## What v1 does NOT include

- Production-detail MCAD files, selected supplier internals, tolerance
  stacks, manufacturing drawings, and custom-board KiCad files only
  where a deployment chooses custom electronics (v2).
- Detailed finite-element analysis (v3 — homologation phase).
- Paint-and-livery guidance (operator scope).

## How to execute this package

1. A fabricator reads [`general-arrangement.md`](general-arrangement.md)
   + [`interfaces.md`](interfaces.md) to size their production
   line tooling.
2. [`fabrication-plan.md`](fabrication-plan.md) defines the shop
   route: tube/plate cutting, press-brake bends, welding fixtures,
   composite bonding, and COTS module installation.
3. [`bom-skeleton.md`](bom-skeleton.md) gives the procurement team
   the source-identified parts (off-the-shelf commodity) and the
   TBD parts (where the fabricator bids on make-or-buy).
4. [`drawing-register.md`](drawing-register.md) turns the current CAD
   package and v2 detail work into controlled drawing IDs, supplier
   document requirements, and release gates.
5. [`compliance.md`](compliance.md) lists the test campaigns the
   type-approval needs; each is a separately-tendered scope with
   an accredited test house.
6. The current FreeCAD/PNG package supports design review. The v2
   production CAD pack adds cut-lists, NC code, flat patterns,
   tolerance-controlled drawings, and welding-robot path artifacts for
   the shop floor.

## Licensing

v1 specification: CC-BY-SA 4.0.
v2 CAD + drawings: CERN-OHL-S v2, matching the hardware licensing
from [ARCHITECTURE.md §9](../../ARCHITECTURE.md#9-roadmap).
