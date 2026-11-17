# Baghdad 700-place train

**Selected Baghdad digital planning candidate:** `osr-baghdad-zero-tunnel-offwire-20261117`, protected conductor rail, ten-metre separate-support viaduct. This is a distinct high-capacity train from the 276-place [comfort reference](../../docs/reference-v07/vehicle/README.md); its mass, power and price are recalculated in the [integrated model](system.toml).

![Six-car train planning layout and door positions](vehicle-layout.svg)

| Interface or duty | Planning control |
|---|---:|
| Formation | Six 17 m cars, approximately 104.5 m coupled; 125 m clear platform |
| Body and doors | 2.7 m outside width; four 1.3 m clear double-leaf doors each side per car |
| Accessible passenger layout | 20 seats, two wheelchair places and up to 95 standees per car; 700 places/train service cap |
| Running gear | Two two-axle bogies/car, 24 driven axles/train, steel wheel on 60E1 rail design control |
| Selected crowd train mass | **201.092 t**, including protected contact equipment; 33.515 t/car average |
| Crowd axle load | **8.379 t/axle** before dynamic and unequal-load factors |
| Traction | Protected conductor shoes, sectionalised DC supply, 5 MW overhead-comparator input request; motor rating from the same 2% grade and 0.6 m/s² duty |
| Independent stop | Twelve protected rail-brake modules/train; one-out case requires at least 14.6 kN effective force per remaining module at the comparator crowd load |
| Cooling | 45 kW/car installed envelope, 25 kW/car average summer budget |
| Service | 150 s peak interval; 35 s dwell; 38 km/h commercial speed; 72 km/h planning speed cap |

The protected conductor candidate removes roof collectors and has **no traction battery**. Service batteries independently supply braking, controls, lighting and rescue functions; their mass and maintenance remain part of the train design. The four-way power comparison changes contact equipment, battery mass, cooling and civil load in one evaluation. Station-charged battery operation requires roughly 467 kWh/train and 128 simultaneous charging ports at about 5.97 MW/port in the first programme, which is why it is not the selected cost candidate.

## Assembly and repair

The car is divided into a corrosion-protected underframe and roof, two removable powered bogies, replaceable sidewall/door modules, two roof HVAC modules, underfloor traction cabinets, protected contact shoes and independently supplied brakes. Bogie mounts, door/platform datums, axle load, equipment envelopes, cable isolation and lift points are controlled interfaces for the first car quotation. Numbered harnesses and modular doors allow replacement without dismantling the shell. Wheel, motor, bearing, brake and contact-shoe removal paths must remain accessible in the depot layout.

The cost model allocates **$8.48m/trainset** to the selected contact configuration and **$2.052bn** to 242 first-programme sets. Iraqi fabrication and assembly opportunities are body structures, door frames, interior panels, seats, cable looms and maintenance; traction modules, certified safety components, bearings and contact materials are procured packages. Suppliers should quote mass, repeated thermal rating, adhesion, powered-off braking, door cycles, cooling duty, assembly hours, spares and replacement routes against this configuration. The digital model supplies a quotation basis; its schematic car layout and source-bound mass estimate are not fabrication approval.
