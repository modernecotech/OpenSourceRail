# Baghdad construction and train assembly

The two films use metre-based CAD to show parts in assembly order, from the ground and frame through fitout and inspection. The pace helps the viewer follow the assembly. Production hours and shift estimates are in the workplan.

| Film | Duration | Scope |
|---|---:|---|
| [Viaduct construction](https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/assets/assembly-animations/viaduct.mp4) | 2:36 | Two precast yards and two launch fronts. Excavation, footings, piers, crosshead reinforcement, bearings, girder casting, deck haul, both launches, service installation and closure. |
| [Train fabrication and fitout](https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/assets/assembly-animations/train.mp4) | 3:08 | Named carbody and powered-bogie frame parts, wheelsets and drives, floor and saloon, doors and roof services, front and rear ends, draw gear, electrical and air connections, floor bridge and gangway bellows. |

[Finished train](train-exterior.jpg) · [Passenger end assembly](train-144.png) · [Passenger view through the end glazing](train-terminal.jpg) · [Saloon at eye level](train-saloon.jpg) · [Saloon cutaway](train-interior.jpg) · [Inter-car assembly](train-connector.jpg) · [Bearing stack](viaduct-43.png) · [Girder casting](viaduct-57.png) · [Gantry placement](viaduct-placement.jpg) · [Finished viaduct bay](viaduct-completed.jpg)

## Follow the work

| Time | Viaduct | Time | Train |
|---:|---|---:|---|
| 0:00 | Two yards dispatch to inward workfronts | 0:00 | Cut and kit steel |
| 0:08 | Excavate and cast the footing | 0:10 | Assemble underframe, side frames, roof and portals |
| 0:23 | Cast the column and crosshead | 0:48 | Assemble bogie frames |
| 0:39 | Fit bearing plinths, plates and bearings | 1:12 | Fit wheelsets, suspension, drives and brakes |
| 0:48 | Set mould, strands and cage, cast and release girder | 1:30 | Fit saloon floor, seats, wheelchair places and rails |
| 1:09 | Complete starter bays and transfer girder to flatbed | 1:48 | Fit ducts, doors, glazing, roof and HVAC |
| 1:24 | Assemble flatbed, gantry, hoist and lifting gear | 2:06 | Install glazed passenger ends and underfloor rescue interfaces |
| 1:42 | Feed both girders and land them on the bearings | 2:25 | Bring the two inner ends together and connect the services |
| 2:07 | Extend the construction path and fit permanent systems | 2:46 | Fit the floor bridge and seal the gangway |
| 2:22 | Complete closure and recover plant | 2:58 | Inspect the six-car formation |

The civil film follows the 20 m paired U-girder concept. The regular bay uses concrete foundation, column and shared crosshead envelopes, four bearing assemblies per girder and two separately landed girders. The modeled foundation is a shallow option. The actual ground treatment, cage details, bearings, temporary deck loads and lifting equipment require design evidence. [Rail-fed geometry and dimensions](../../../cities/Baghdad/engineering/mechanical/civil/rail-fed/CONCEPT-GEOMETRY.md) · [Rail-fed method, time and price comparison](../../../cities/Baghdad/engineering/mechanical/civil/RAIL-FED-ERECTION.md) · [FHWA precast erection and stability reference](https://www.fhwa.dot.gov/bridge/pubs/nhi15047.pdf)

The train uses the source-bound lined-jamb revision, with 120 body pieces and 24 pieces across both bogie frames per 17 m car. The fitted scene adds 20 seats, two wheelchair places and eight door openings per car. Unattended GoA4 operation uses two glazed passenger ends, two outboard rescue couplings below the floor and five inner junctions per six-car set. The coupler, hoses, harnesses, floor bridge and bellows show their relative interfaces for quotation and inspection. Side clearance under yaw and suspension travel, coupler forces, door sweep, fire performance and measured fitout mass remain open. [First-article model](../../../cities/Baghdad/engineering/prototype/airport-prototype.zip) · [Installed general arrangement](../../../cities/Baghdad/engineering/prototype/vehicle-factory/INSTALLED-GA.md) · [Coupler function reference](https://www.voith.com/corp-en/connection-components-couplings/railway-couplers.html)

## Parts, cost and shifts

[Assembly parts and cost CSV](assembly-bom.csv) · [Assembly ledger with quantities and input evidence](assembly-ledger.json) · [Train parts OBJ in metres](train-parts.obj.gz) · [Civil parts OBJ in metres](viaduct-parts.obj.gz)

The CSV names each component group and links it to the OBJ objects. Each OBJ contains one representative geometric unit per row. Use the row's quantities to extend unit mass, price and work. The register distinguishes purchased stock, installed parts, temporary works, interfaces, plant and blended allowances. A blank value identifies a covered or unresolved estimate. The row's basis gives the reason.

| Scope | Modeled mass | Low / base / high price allowance in USD |
|---|---:|---:|
| Six-car set, gross cut frame and bogie stock | 31.636 t | $95,710 / $180,942 / $346,727 |
| Six-car set, modeled fitout and running systems | 34.9 / 54.9 / 87.6 t | $1.051m / $1.910m / $3.557m |
| One paired civil bay and its attributed shared support, known subtotal | 274.5 / 279.5 / 284.6 t | $26,440 / $34,910 / $52,054 |
| Illustrative 12 km study, priced moulds and two-front dry plant | 50 t known from two trial flatbed tares | $6.412m / $13.267m / $29.016m |
| Two terminal hardstands, two transfer/enabling packages and one support-work allocation | Open | $0.931m / $1.983m / $3.997m |

The train allowances cover the listed parts and frame fabrication comparison. Use them to test or replace parts of the matched fleet allowances. The gross stock and additional fitted equipment subtotals have different mass bases. Complete installed tare, passenger load, axle reactions and vehicle qualification require their own reconciliation. [Fabrication comparison and scope](../../../cities/Baghdad/engineering/prototype/rapid-production/README.md)

The civil bay material price includes its share of the common support stock and a separate bearing supply allowance. Duct, access, final track, combined works and operated hire have their own parent accounts. The facility and plant rows have study-wide scopes and recur at line or programme level according to the construction schedule. Use the programme study to compare total delivery costs. [Network delivery quantities, cost and cash](../../../cities/Baghdad/engineering/mechanical/civil/rail-fed/network-delivery.md)

[Costed workplan](workplan/summary.md) · [Shift and trade rows](workplan/workforce.csv) · [Arrow-compatible Parquet](workplan/workforce.parquet) · [Input plan](assembly-plan.json)

| Workplan scope | Packages | Required person-hours | Booked person-hours | Low / base / high payroll allowance | Uncovered hours at 90% availability |
|---|---:|---:|---:|---:|---:|
| One six-car set | 45 | 3,530 | 4,768 | $30,181 / $33,042 / $38,812 | 120 |
| Civil bay and separately counted two-front plant preparation | 35 | 2,521 | 3,264 | $23,827 / $26,112 / $30,649 | 138 |

The workplan gives each package a responsible trade, indicative task minutes, a booked eight-hour slot, a crew size and low/base/high wage assumptions from the existing Baghdad workplan. The Rust simulator applies a 90% availability stress to the proposed staffing. Dependencies are recorded in the assembly ledger. Shared equipment, simultaneous teams, inspection and curing calendars affect actual duration. Where material prices or supplier offers already include an operation, credit the matching labour before changing the programme budget.

## Reproduce the films and records

Run from the repository root with Python, NumPy, Pillow, DejaVu Sans, FFmpeg with libx264, Blender, and the existing Rust workplan dependencies. Each downloadable film is below 20 MB.

```sh
python3 docs/assets/assembly-animations/render.py --output build/assembly-animations --workers 4
python3 docs/assets/assembly-animations/render.py --clip train --still 144 --output build/assembly-animations
python3 docs/assets/assembly-animations/render.py --clip viaduct --still 43 --still 57 --output build/assembly-animations
python3 docs/assets/assembly-animations/render_views.py --blender flatpak --samples 12 --output build/assembly-animations
python3 docs/assets/assembly-animations/ledger.py --output build/assembly-animations
./osr workplan --plan build/assembly-animations/assembly-plan.json --output build/assembly-animations/workplan --availability-bps 9000
python3 docs/assets/assembly-animations/verify.py --path build/assembly-animations --decode
```

The [film receipt](receipt.json), [render receipt](views-receipt.json) and [workplan receipt](workplan/run-receipt.json) identify the inputs, render settings and resulting bytes. The Blender views use the assembly meshes with illustrative streets and finishes.
