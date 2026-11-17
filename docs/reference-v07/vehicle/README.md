# v0.7 representative vehicle — powered wheel concept

**Digital design basis, 17 November 2026.** This is the unchanged vehicle
component in the [selected 30 km digital railway](../digital/selected.toml),
with component candidate `ac550fe8ff23f20cb1ae5b142f4ef6160afc9de6efe7850754bac96a7789327d`
from the [prototype bundle](../../design-engine/v07-prototype-bundle/packet/result.json).
The [joined digital mass and CAD screen](../digital/vehicle/README.md) carries
its placement bounds to the selected thirteen-strand civil child. The retained
passive-wheel v0.6 reference has a different physical identity and price.

## Formation and service

| Design input | Concept value |
| --- | ---: |
| Formation | Six 17.0 m cars, 104.5 m full train including ends |
| Body width, track gauge | 2.65 m, 1.435 m |
| Passenger layout | 44 fixed seats and two wheelchair places per car; 276 normal places/train |
| Doors | Two 1.4 m clear openings on the +y side of each car, at x = −4.5 and +4.5 m |
| Floor top | 1.00 m above rail running surface |
| Bogies and axles | Two bogies/car at x = ±6.4 m; four axles/car at x = ±5.35 and ±7.45 m |
| Traction | One motor/gear cartridge per axle, 24 driven axles/train; six 1C4M drive groups |
| Collection | One roof collector/car from a protected 1.5 kV DC overhead conductor |
| Speed and command | 72 km/h cap; 0.4 m/s² acceleration; 0.6 m/s² service stop design demand |
| Auxiliary store | Existing 82.8 kWh/car service battery, isolated from traction; independent brake supply is separate |

This layout selects **continuous grid-fed wheel traction** for the concept, because the equal-service screen reaches a 2.727 km leg with a sustained 2% climb at the defined 72 km/h cap. Station-only launch and a single short booster do not reach that leg under the same demand. No traction battery or supercapacitor is included in this vehicle or its cost. In a future battery variant, storage, charging, cooling, replacement and mass would create a different candidate.

The analytical normal design load is **25.072 t/car**, or **150.432 t/train**; the 160-person crowd structural control is **33.622 t/car**. These numbers include a conservative 2.400 t/car powered-equipment allowance on the inherited incomplete normal account. They are sizing loads for motor, brake, civil and cost estimates, not a weighed installed mass or axle-load certificate. The conditional tare arithmetic is 20.292–21.617 t/car; use the **21.617 t/car upper allowance** for workshop handling. The source account still contains 10.090 t/car of parts without approved placements, so complete centre of gravity and axle reactions require an assembled weighing.

On the 2.727 km, +2% duty leg, the selected analytical load asks for 102.23 kN peak tractive force, 2.045 MW peak mechanical power, and 33.79 kWh mechanical energy per train. With 25% peak margin, 85% drive efficiency and 30 kW auxiliaries, request at least **3.037 MW train DC input rating** and **506 kW for each 1C4M group**. Six groups share the train power; each of the four motor/gear cartridges in a group must be rated for its actual torque, speed and thermal cycle. These are procurement ratings, not claims about a selected catalogue motor. The 30 km planning fleet is **44 active plus seven reserve trainsets** under a 120 s headway, 35 s dwell and 180 s terminal turnback control.

## Critical coordinate and service interfaces

Use a car frame with x forward from the car centre, y left, z upward from rail head. Nominal rigid transforms from car to bogie are translations (−6.4, 0, 0) and (+6.4, 0, 0) m, each at identity rotation on straight level track. The motor boxes are 0.64 × 0.52 × 0.52 m, centred at each axle x, y = 0, z = 0.52 m. Reserve ±0.05 m translation in all axes for a first interference screen. This leaves only 52 mm nominal lateral room to retained disc inner faces and 106 mm to the floor underside. A full bogie yaw, roll, heave, wheel-wear, curve, switch and tool sweep is required before these are mounting drawings.

Each bogie carries one independent rail-contact brake module with two nominal 1.0 m shoes at y = ±0.7175 m. Stowed pair bottom is z = 0.12 m; deployed contact is z = 0. The module needs a supported downward removal path over a pit. Keep shoe sliding guides, end stops, retention pins, flexible power/earth loops and local brake-force path clear of the axle drive. Place each inverter/cooling rack underfloor near x = ±2.2 m and the collector/isolator on the roof. Roof top is nominal z = 3.8069 m; the proposed collector envelope reaches z = 4.8 m, subject to the actual conductor and civil electrical clearances. No roof or rail clearance is issued from these nominal boxes alone.

For the independent stop, do not count regeneration or wheel friction when checking a common-mode wheel-brake failure. At the 150.432 t normal design load on a 2% downgrade, 20 m/s to zero at net 0.6 m/s² asks for 119.77 kN longitudinal rail force. With one of twelve bogie brake modules unavailable, each remaining module must deliver **10.89 kN** and absorb an ideal **3.63 MJ** at its rail interface. The ideal stop is 333 m before command, build-up, uncertainty and hot-fade allowances. Select a protected brake energy source and a separately rated power-free parking arrangement, with verified rail and turnout compatibility, before a running prototype uses this demand. The [independent brake package](../../design-engine/v07-independent-brake/README.md) is the supplier test specification.

## Quotation bill and workshop route

The following is the minimum **per-car interface count**, not a supplier-approved manufacturing BOM. The seven powered equipment groups carry one upper allowance of 2,670 kg/car; retiring only 275 kg/car of counted passive secondary stock gives the 2,400 kg/car normal-load addition above.

| Assembly/group | Quantity per car | Upper mass allowance | Make/buy and service route |
| --- | ---: | ---: | --- |
| Motor/gear cartridge with torque arm | 4 | 720 kg | Buy rated drive; local torque arms/mounts after fatigue design; remove laterally with car supported |
| Cooled inverter racks | 2 | 560 kg | Buy power/control core; fabricate enclosure and coolant rack locally; remove from underfloor access bay |
| Roof collector | 1 | 220 kg | Buy collector; local roof reinforcement/mount; isolate and lift from roof walkway |
| Roof HV isolation/protection | 1 | 160 kg | Buy rated breaker/surge parts; local enclosure; roof access |
| Two-shoe rail-brake module | 2 | 630 kg | Buy qualified shoe/coil; local guides/brackets after force test; remove shoes downward over pit |
| Rated HV/earth/cooling flexible runs | 1 set | 200 kg | Cut/terminate locally from certified stock; bogie movement loops and dry breaks |
| Structural mounts, fasteners, guards | 1 set | 180 kg | Local fabrication with torque and retention records |
| **Gross powered equipment** | | **2,670 kg** | Includes budget, not a weighed installed assembly |

The bill includes at least four axle-coupling kits, four torque arms, eight compliant motor-mount bushes, 32 motor mounting bolts, 16 rack bolts, eight collector bolts, eight isolation bolts, two bogie earth loops, four bogie HV loops and four coolant supply/return hoses per car. The two brake modules add four shoes, four lifting actuators, four guide slides, eight end stops, eight retention pins and 16 shoe bolts. Vendor motor, gearbox and axle bearings, seals, wear liners, cable supports, connectors, sensors and the protected brake energy system must appear in the ordered BOM with actual quantities; they are **unresolved items**, not zero-cost omissions.

The preliminary workshop route is: fixture and measure bogie/axle/body datums; fabricate or procure structural body and roof hardpoints; install axle cartridges and torque paths; fit supported brake modules; install underfloor inverter/cooling racks and flexible loops; fit roof collection/protection; assemble doors, HVAC, interior and service battery; marry both bogies; weigh each car and check each axle; then perform low-speed drive, door, brake, isolation and thermal tests. Allow **720 direct labour-hours per first complete car** as a planning allowance: 260 body and structural fit, 120 bogie/drive, 80 doors/interior, 80 HVAC and auxiliary, 100 wiring/cooling, 80 final assembly and test. Ten technicians working one eight-hour shift need about **nine working days of direct assembly time** once bought components, jigs and fabricated parts are available. This excludes component manufacture, engineering, rework, supplier lead time and qualification testing; use recorded shop hours to replace the allowance.

Record each drive, brake, battery, door and collector by serial/lot in the manufacturing BOM. Keep overhead, traction DC, service battery, brake energy and coolant isolation separate during repair. A removed motor cartridge or shoe gets a torque/retention, insulation, leakage and functional test record before the train is returned to service. The complete [mechanical research handoff](../../design-engine/v07-powered-vehicle/plan.json) provides the underlying source hashes and interface counts; supplier drawings and measured fit replace its nominal boxes for production.
