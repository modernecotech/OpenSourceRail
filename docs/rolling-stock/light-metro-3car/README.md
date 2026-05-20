# `light-metro-3car` trainset package

This directory holds the dimensioned specification for the
**light-metro-3car** trainset — the Samawah reference family per
[RFC 0003](../../rfcs/0003-samawah-reference-deployment.md) and the
default for populations 300 k – 1 M per [RFC 0008 §5](../../rfcs/0008-rolling-stock-reference-design.md#5-family-selection-policy).

This package started as the v1 RFC 0008 bid specification and now
also links the current envelope-level CAD/PNG/STEP outputs. A domestic
rolling-stock fabricator can read the dimensions, masses, interfaces,
sub-assembly tree, fabrication sequence, procurement BOM skeleton, and
design-review CAD. The design deliberately favours a modern low-capex
factory: COTS rail subsystems wherever possible, simple cut/bend/weld
fabrication for the primary frame, and composite non-structural panels
for sides, roof fairings, cabless cowls, and interior liners.

## Contents

| File | Scope |
|---|---|
| [`general-arrangement.md`](general-arrangement.md) | Overall envelope, gauge clearance, consist diagram, floor heights, door positions |
| [`fabrication-plan.md`](fabrication-plan.md) | Cut-bend-weld primary structure, composite cladding, COTS module installation sequence |
| [`bogie.md`](bogie.md) | 2-axle articulated bogie spec, wheel profile, suspension, brake mount |
| [`body.md`](body.md) | Welded steel underframe/spaceframe, composite side panels, end bulkheads, articulation joint |
| [`traction.md`](traction.md) | PMSM motor + SiC inverter + reduction gear, adhesion budget |
| [`interfaces.md`](interfaces.md) | Coupler, pantograph, platform gap, TCN-E connector, aux power |
| [`bom-skeleton.md`](bom-skeleton.md) | Procurement BOM lines (source-identified parts vs TBD) |
| [`compliance.md`](compliance.md) | Standards matrix: EN 15227, EN 45545, EN 14363, EN 50155, ISO 3095, EN 12299 |
| [`drawing-register.md`](drawing-register.md) | v2 drawing IDs, supplier documents, inspection evidence, release gates |

The governing visual/layout reference is
[`solar-metro-trainset.png`](../../../docs/assets/solar-metro-trainset.png):
white/silver body, green waist band, dark skirts, large glass ends,
roof PV, low-floor centre doors, powered end cars, trailer middle car,
and batteries under longitudinal seats.

COTS passenger-facing modules are controlled by the supplier-neutral
envelope catalogue at
[`hardware/trainset-interiors/cots-catalogue.md`](../../../hardware/trainset-interiors/cots-catalogue.md).

## Canonical Parametric Source

The build123d source files are the design basis. STEP files and PNGs
are generated handoff artifacts.

| Source | Controls |
|---|---|
| [`trainset.py`](../../../mechanical-py/src/osr_mech/rolling_stock/trainset.py) | Family length, car count, motorisation, cowl/body/bogie assembly |
| [`car_body.py`](../../../mechanical-py/src/osr_mech/rolling_stock/car_body.py) | 17 m body module, 2.85 m width, 3.45 m height, livery, doors, windows, roof PV/HVAC |
| [`sensor_cowl.py`](../../../mechanical-py/src/osr_mech/rolling_stock/sensor_cowl.py) | Large glass end cowl and T-OBS visual envelope |
| [`systems.py`](../../../mechanical-py/src/osr_mech/rolling_stock/systems.py) | Couplers, articulations, batteries, doors, electronics, charging, T-OBS packs |
| [`bogie/`](../../../mechanical-py/src/osr_mech/rolling_stock/bogie/) | Powered and converted-trailer bogie assemblies |
| [`cad_templates/rolling_stock.py`](../../../mechanical-py/src/osr_mech/cad_templates/rolling_stock.py) | Sheet-metal/chassis manufacturing templates |

## Current CAD / PNG Design Outputs

The present train design now has envelope-level definitions for the
major train assemblies, sub-assemblies, and repeated components. The
models are supplier-neutral `build123d` geometry in
[`mechanical-py/src/osr_mech/rolling_stock`](../../../mechanical-py/src/osr_mech/rolling_stock)
and render to these design-review PNGs:

| Output | Scope |
|---|---|
| [`trainset-light-metro-3car.png`](../../../docs/screenshots/trainset-light-metro-3car.png) | Final 3-car trainset assembly with car bodies, bogies, cowls, couplers, inter-car articulation, and train systems |
| [`trainset-car-detail.png`](../../../docs/screenshots/trainset-car-detail.png) | 17 m car body, door/window openings, glazing, skirt, livery, and roof equipment |
| [`trainset-interior-fit-out.png`](../../../docs/screenshots/trainset-interior-fit-out.png) | COTS passenger fit-out envelopes inside the car body |
| [`trainset-body-sheet-metal-kit.png`](../../../docs/screenshots/trainset-body-sheet-metal-kit.png) | Sheet-metal/chassis manufacturing kit: underframe, bolsters, coupler pockets, side posts, rails, roof bows, end rings |
| [`trainset-car-systems.png`](../../../docs/screenshots/trainset-car-systems.png) | One self-contained car systems package: doors, batteries, traction power rack, charging connector, and accessibility/safety reservations |
| [`trainset-battery-pack.png`](../../../docs/screenshots/trainset-battery-pack.png) | Eight sodium-ion module envelopes plus HV contactor, fuse, and BMS cabinet per car |
| [`trainset-door-system.png`](../../../docs/screenshots/trainset-door-system.png) | Door cassette pair with sill gap fillers, locks, and external emergency releases |
| [`trainset-electronics-cabinet.png`](../../../docs/screenshots/trainset-electronics-cabinet.png) | Per-end T-ECU/S, T-ECU/A, and crashworthy event recorder, two sets per trainset |
| [`trainset-end-coupler.png`](../../../docs/screenshots/trainset-end-coupler.png) | Scharfenberg Type 10 coupler, electric-head carrier, and EN 15227 crash absorber envelope |
| [`trainset-inter-car-articulation.png`](../../../docs/screenshots/trainset-inter-car-articulation.png) | Inter-car bellows, semi-permanent drawbar, and trainline drag-chain envelope |
| [`trainset-tobs-sensor-pack.png`](../../../docs/screenshots/trainset-tobs-sensor-pack.png) | T-OBS LIDAR, mmWave radar, stereo camera, and ultrasonic sensor envelopes |
| [`bogie-motor.png`](../../../docs/screenshots/bogie-motor.png) | Powered bogie assembly with frame, wheelsets, motors, gearboxes, suspension, and brakes |
| [`bogie-trailer.png`](../../../docs/screenshots/bogie-trailer.png) | Trailer bogie assembly using the common frame and suspension envelope |

The matching generated STEP handoff artifacts are regenerated under
[`mechanical-py/catalog/rolling_stock`](../../../mechanical-py/catalog/rolling_stock):
[`trainset-light-metro-3car.step`](../../../mechanical-py/catalog/rolling_stock/trainset-light-metro-3car.step),
[`body-sheet-metal-kit.step`](../../../mechanical-py/catalog/rolling_stock/templates/body-sheet-metal-kit.step),
[`car-systems.step`](../../../mechanical-py/catalog/rolling_stock/car-systems.step),
[`battery-pack-set.step`](../../../mechanical-py/catalog/rolling_stock/battery-pack-set.step),
[`door-system-pair.step`](../../../mechanical-py/catalog/rolling_stock/door-system-pair.step),
[`electronics-cabinet.step`](../../../mechanical-py/catalog/rolling_stock/electronics-cabinet.step),
[`end-coupler.step`](../../../mechanical-py/catalog/rolling_stock/end-coupler.step),
[`inter-car-articulation.step`](../../../mechanical-py/catalog/rolling_stock/inter-car-articulation.step), and
[`tobs-sensor-pack.step`](../../../mechanical-py/catalog/rolling_stock/tobs-sensor-pack.step).
The matching electronics host-class quantities are mirrored in
[`hardware/rolling-stock-integration.md`](../../../hardware/rolling-stock-integration.md).

The remaining gaps are not missing assemblies in the train envelope;
they are v0.2/v2 detail-design tasks: supplier exact envelopes, weld
maps, FEA-ready brackets, harness clamp locations, manufacturing
tolerances, and release drawings listed in
[`drawing-register.md`](drawing-register.md).

## Reference envelope (from RFC 0008 §1)

| Parameter | Value |
|---|---|
| Cars | 3 (articulated) |
| Overall length (over couplers) | 51.0 m |
| Tare mass target | 98 t |
| Axle load (AW3 crush) | ≤ 14 t |
| Max speed | 25 m/s (90 km/h) |
| Seats | 60 longitudinal seats |
| Passenger capacity (AW2) | 330 (seated + standing) |
| Passenger capacity (AW3 crush) | 420 short-duration crush load |
| Onboard battery | 450 kWh Na-ion (150 kWh per car, under seats) |
| Peak onboard motor output | 600 kW |
| Floor height (above ToR) | Low-floor centre door zone; raised floor over standard bogies |
| Gauge | 1 435 mm (default) or 1 000 mm (variant) |

## What v1 does NOT include

- Production-detail KiCad / MCAD / STEP files with selected supplier
  internals, tolerance stacks, and manufacturing drawings (v2).
- Detailed finite-element analysis (v3 — homologation phase).
- Paint-and-livery guidance (operator scope).
- Fire-load and smoke-extraction analysis for the battery bay
  (v2, paired with EN 45545-2 test campaign).

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
6. The current STEP/PNG package supports design review. The v2
   production CAD pack adds cut-lists, NC code, flat patterns,
   tolerance-controlled drawings, and welding-robot path artifacts for
   the shop floor.

## Licensing

v1 specification: CC-BY-SA 4.0.
v2 CAD + drawings: CERN-OHL-S v2, matching the hardware licensing
from [ARCHITECTURE.md §9](../../ARCHITECTURE.md#9-roadmap).
