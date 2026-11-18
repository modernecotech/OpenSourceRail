# Baghdad 700-place train

**Selected Baghdad digital planning candidate:** `osr-baghdad-zero-tunnel-offwire-20261117`, protected conductor rail, ten-metre separate-support viaduct. This is a distinct high-capacity train from the 276-place [powered 30 km digital train](../../docs/reference-v07/vehicle/README.md) and the retained [passive comfort reference](../../engineering/development-baseline.toml). Its mass, power and price are recalculated in the [integrated model](system.toml).

![Six-car train planning layout and door positions](vehicle-layout.svg)

![Straight island platform, trains and outboard protected conductor planning section](station-interface.svg)

The train and straight-station dimensions in these drawings are controlled by
the [Baghdad system input](system.toml); the station section is generated from
it and the vehicle drawing is checked against its door and body dimensions.

| Interface or duty | Planning control |
|---|---:|
| Formation | Six 17 m cars, approximately 104.5 m coupled; 125 m clear platform |
| Body and doors | 2.7 m outside width; four 1.3 m clear double-leaf doors each side per car |
| Accessible passenger layout | 20 seats, two wheelchair places and up to 95 standees per car; 700 places/train service cap |
| Running gear | Two two-axle bogies/car, 24 driven axles/train, steel wheel on 60E1 rail design control |
| Selected crowd train mass | **201.092 t**, including protected contact equipment; 33.515 t/car average |
| Crowd axle load | **8.379 t/axle** before dynamic and unequal-load factors |
| Traction | Protected conductor shoes, sectionalised DC supply, **5.004 MW** per-train DC input sizing request at 2% grade and 0.6 m/s² net acceleration |
| Independent stop | Twelve protected rail-brake modules/train; one-out case requires at least 14.6 kN effective force per remaining module at the comparator crowd load |
| Cooling | 45 kW/car installed envelope, 25 kW/car average summer budget |
| Service | 150 s peak interval; 35 s dwell; 38 km/h commercial speed; 72 km/h planning speed cap |

## Train, platform and conductor interface

Use rail head as z = 0 and track centre as y = 0. For straight, level
stations, the nominal car floor is z = 1,000 mm; the platform edge is
|y| = 1,425 mm from its track centre. A 2,700 mm wide car then has a 75 mm
static edge gap. The platform has 125 m clear length against the 104.5 m
train, leaving 10.25 m nominal margin at each end when centred. An 8 m
island gives 10.85 m nominal spacing between the two straight track centres.
Curves, cant, suspension movement, wheel wear and stopping error enter the
site-specific swept and accessible boarding gap calculation.

Each 17 m car has door centres at x = -6.3, -2.1, +2.1 and +6.3 m from the
car centre on **each** side, with 1.3 m clear width. The outer opening edge
is 1.55 m from the nominal car end. Car end, coupler and articulation spaces
are outside the opening. The train controller releases only the side
confirmed by station identity, stopping position and platform detection;
door locked feedback is a departure condition. The conductor and contact
shoes remain outside the passenger reach and evacuation path, with section
isolation before track access. These nominal datums are the digital
coordination geometry for car, platform, screen and electrical design.

The [control equipment schedule](../../control-electronics/README.md) assigns
two train protection channels, two radio links, one control node per car,
one controller per opening, one brake controller per bogie and two protected
service-power units per train. Their **0.35 t** and **6 kW** per-train planning
allowances sit inside the published base mass and auxiliary-energy budgets;
their **$0.234m/train** equipment allocation sits inside the train price.
There are four contact-shoe sets per protected-conductor train. Shoe position,
rail clearance, insulation distance, section transition and evacuation
protection are separate electrical/track interfaces and must be demonstrated
in the same vehicle and station drawing before installation.

The protected conductor candidate removes roof collectors and has **no traction battery**. The independent **65 kWh nominal service battery** supplies 18 kW continuous essential duty for two hours, plus a 4 kWh brake event, 2 kWh door and egress event and 20% reserve. Its 52 kWh usable allowance exceeds the calculated 50.4 kWh request. The 0.50 t and $0.10m/train battery allocations are included within the base vehicle mass and price. The model requests 36.1 kW/train for two-hour recharge. The four-way power comparison changes contact equipment, battery mass, cooling and civil load in one evaluation. Station-charged battery operation requires roughly 467 kWh/train and 128 installed charging ports at about 5.97 MW/port in the first programme, which is why it is not the selected cost candidate. Timetable mean charging concurrency is calculated separately.

## Assembly and repair

The car is divided into a corrosion-protected underframe and roof, two removable powered bogies, replaceable sidewall/door modules, two roof HVAC modules, underfloor traction cabinets, protected contact shoes and independently supplied brakes. Bogie mounts, door/platform datums, axle load, equipment envelopes, cable isolation and lift points are controlled interfaces for the first car quotation. Numbered harnesses and modular doors allow replacement without dismantling the shell. Wheel, motor, bearing, brake and contact-shoe removal paths must remain accessible in the depot layout.

The cost model allocates **$8.48m/trainset** to the selected contact configuration and **$2.052bn** to 242 first-programme sets. Iraqi fabrication and assembly opportunities are body structures, door frames, interior panels, seats, cable looms and maintenance; traction modules, certified safety components, bearings and contact materials are procured packages. Suppliers should quote mass, repeated thermal rating, adhesion, powered-off braking, door cycles, cooling duty, assembly hours, spares and replacement routes against this configuration. The digital model supplies a quotation basis; its schematic car layout and source-bound mass estimate are not fabrication approval.
