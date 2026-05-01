# Trainset interiors and closures — COTS equipment catalogue

The `light-metro-3car` body is a welded steel primary frame with
composite non-structural side/roof/nose panels. Passenger-facing
equipment is not bespoke OSR hardware: doors, windows, HVAC,
lighting, seats, grab rails, PIS, CCTV, and intercom are COTS rail
or heavy-duty bus modules installed into reserved envelopes.

This file is the supplier-neutral catalogue promised by
[RFC 0008](../../docs/rfcs/0008-rolling-stock-reference-design.md).
The envelope is the contract; named SKU classes are examples only.
Any replacement is acceptable if it fits the envelope, stays inside
the mass/power budget, exposes the required interface, and arrives
with usable certification evidence.

Related rolling-stock package:

- [`body.md`](../../docs/rolling-stock/light-metro-3car/body.md)
- [`fabrication-plan.md`](../../docs/rolling-stock/light-metro-3car/fabrication-plan.md)
- [`bom-skeleton.md`](../../docs/rolling-stock/light-metro-3car/bom-skeleton.md)

## Qualification classes

| Class | Meaning | Typical procurement path |
|---|---|---|
| COTS-R | Rail-certified COTS module | Preferred for doors, windows, HVAC, intercom |
| COTS-B | Heavy-duty bus module with rail-compatible evidence | Acceptable for seats, lighting, PIS, CCTV where authority allows |
| COTS-I | Industrial module needing enclosure and vibration evidence | Acceptable for non-safety displays/cameras only |
| MAKE-ADAPT | Local adapter plate, harness tail, duct, or bracket | Allowed when it does not change the primary steel frame |

Safety-critical rotating, braking, traction, battery, and door-lock
parts are not downgraded to generic commodity components. They remain
supplier-certified modules with incoming inspection and type-test
evidence.

## Reserved module envelopes

Per 18.9 m self-contained car:

| Module | Qty / car | Envelope | Mass limit | Power budget | Interface |
|---|---:|---|---:|---:|---|
| Door cassette | 2 | clear opening 1 250 × 2 000 mm; cassette ≤ 1 850 W × 2 450 H × 260 D mm | 180 kg each | 600 W peak each | 24/110 V DC, Ethernet/CAN, hardwired closed/locked loop |
| Side glazing | 4 | nominal 900 × 1 200 mm aperture | 35 kg each | 0 | Bonded/gasketed cassette, drain path |
| Roof HVAC | 1 | ≤ 2 700 L × 1 900 W × 450 H mm | 420 kg | 20 kW cooling electrical allowance | 400 V AC, condensate drain, CAN/Ethernet diagnostics |
| Interior lighting | set | two 18.9 m ceiling runs + door-zone lights | 45 kg | 350 W | 24 V DC, emergency-light input |
| Exterior marker/head/tail lights | set | nose/cowl mounted | 25 kg | 150 W | 24 V DC, hardwired marker functions |
| PIS displays + speakers | set | above-door and saloon ceiling mounts | 45 kg | 250 W | Ethernet, 24 V DC, audio line |
| CCTV | set | door sill, saloon, and nose service views | 20 kg | 180 W | PoE or 24 V DC + Ethernet |
| Passenger intercom | 4 | recessed wall modules | 12 kg | 80 W | Ethernet/SIP, 24 V DC, OCC call button |
| Longitudinal seats | 20 seats | under-window modules over battery covers | 120 kg | 0 | M10 floor/side inserts |
| Grab rails/stanchions | set | centre-door and vestibule zones | 45 kg | 0-80 W | M8/M10 floor/ceiling inserts |
| Interior wall/ceiling panels | set | FRP/phenolic cassettes | 220 kg | 0 | Clip/bolt to secondary rails |
| Floor boards + hatches | set | full saloon floor | 280 kg | 0 | Removable panels over battery/HV zones |

Per `light-metro-3car` consist, multiply by three cars. HVAC
dominates auxiliary power; the aux converter and station-energy
models should assume roughly 60 kW HVAC peak plus lighting, PIS,
CCTV, intercom, control electronics, and battery thermal loads.

## Candidate supplier classes

Named suppliers are examples of the class of product, not a locked
vendor list.

| Module | Example class | Required evidence |
|---|---|---|
| Door cassette | IFE, Vapor, Knorr-Bremse, Fuji, Nanjing Kangni rail door family | EN 14752 or equivalent, obstruction detection, lifecycle test, emergency release |
| Side glazing | Pilkington/AGC/Saint-Gobain rail laminated safety glass | EN 15152 or equivalent, impact, fire/smoke data for seals |
| HVAC | Liebherr, Thermo King, Hispacold, Sutrak, Merak roof HVAC | EN 50155/50121 where applicable, +50 °C performance curve, refrigerant data |
| Lighting | Rail/bus LED strip or troffer modules | EN 45545 material data, EMC evidence, emergency-mode behaviour |
| Seats | Kiel, Grammer, Fainsa, McConnell, local bus/rail equivalent | EN 45545 R7, static strength, vandal-resistance data |
| Grab rails | Stainless modular rail/bus stanchion system | Pull-load data, corrosion grade, fastener spec |
| PIS displays | Advantech/IEI/Litemax/rail LCD class | EN 50155 preferred or vibration/temperature evidence |
| CCTV | Axis/Hikvision/industrial PoE camera class in rail enclosure | EMC/vibration evidence, cybersecurity hardening path |
| Intercom | Zenitel/Vingtor, Commend, rail SIP intercom class | EN 50155 preferred, audio intelligibility, emergency-call behaviour |
| Floor/interior panels | Phenolic/FRP rail interior panel supplier | EN 45545 HL2 R1/R5 evidence, cleanability, repair method |

## Supplier-change rule

A supplier change is valid without changing the carbody if all are true:

1. The replacement fits inside the reserved envelope.
2. Mass is no more than the row limit, or the weight budget is updated
   and bogie axle-load margins still pass.
3. Power draw is no more than the row budget, or aux-power sizing is
   updated and thermal checks still pass.
4. Mounting can be handled by adapter plates or harness tails.
5. The primary steel frame, door posts, bolsters, and coupler pockets
   are unchanged.
6. Required fire, EMC, vibration, lifecycle, and maintainability
   evidence is present.

If any supplier change needs new primary steel, it is a body-design
change and must go through v2 CAD/FEA release.

## Incoming inspection

| Module | Incoming checks |
|---|---|
| Door cassette | Dimensional check, serial/cert pack, lock loop continuity, manual release |
| Window cassette | Glass marking/cert pack, edge damage inspection, seal/adhesive shelf life |
| HVAC | Nameplate, refrigerant record, factory test sheet, drain and duct fit |
| Lighting/PIS/CCTV/intercom | Power-on test, firmware version, MAC/serial register, mounting hardware |
| Seats/grab rails | Fire certificate, pull-test certificate or batch test, finish defects |
| Panels/floor | Fire certificate, flatness, insert locations, repair kit present |

## Installation evidence

Each car receives a COTS fit-out evidence pack:

- Supplier certificate and installation manual for every COTS-R/B item.
- Envelope compliance sheet signed by production engineering.
- Mounting torque record for seats, rails, doors, HVAC, and hatches.
- Water ingress test for doors/windows/roof equipment.
- HVAC drain test.
- Door obstruction and emergency-release test.
- Lighting lux test and emergency-light mode test.
- PIS/CCTV/intercom network enumeration report.
- Material fire certificate index.

This evidence pack becomes part of the trainset technical file and
feeds the compliance matrix in
[`docs/rolling-stock/light-metro-3car/compliance.md`](../../docs/rolling-stock/light-metro-3car/compliance.md).
