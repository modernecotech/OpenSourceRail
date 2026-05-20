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

Per 17 m self-contained car:

| Module | Qty / car | Envelope | Mass limit | Power budget | Interface |
|---|---:|---|---:|---:|---|
| Door cassette | 2 | clear opening 1 250 × 2 000 mm; cassette ≤ 1 850 W × 2 450 H × 260 D mm | 180 kg each | 600 W peak each | 24/110 V DC, Ethernet/CAN, hardwired closed/locked loop |
| Side glazing | 4 | nominal 900 × 1 200 mm aperture | 35 kg each | 0 | Bonded/gasketed cassette, drain path |
| Roof HVAC | 1 | ≤ 2 700 L × 1 900 W × 450 H mm | 420 kg | 20 kW cooling electrical allowance | 400 V AC, condensate drain, CAN/Ethernet diagnostics |
| Interior lighting | set | two 17 m ceiling runs + door-zone lights | 45 kg | 350 W | 24 V DC, emergency-light input |
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

## COTS Reference Baselines

The CAD now uses COTS-inspired integration geometry rather than plain
boxes. These references are not sole-source selections; they define
the type of commodity/supplier evidence the v2 drawing pack must
accept or replace.

| Function | Reference family | CAD/design implication |
|---|---|---|
| Automatic coupler | Dellner / Voith Scharfenberg Type 10 family | Coupler head, guide horns, electrical-head carrier, brake-pipe hoses, bolted shear plate, EN 15227 crash absorber pocket |
| Door cassette | Electric rail/bus sliding or plug door systems, e.g. Vapor/Wabtec class products | Top operator rail, hanger rollers, two sliding leaves, bonded glass, lock/release unit, threshold drainage, gap-filler hinge |
| Nose LIDAR | Livox HAP class automotive-grade solid-state LIDAR | 105 × 131.6 × 65 mm LIDAR body, heated optical window, service fasteners, 9-18 V feed allowance |
| Radar | TI AWR1843BOOST class 77 GHz radar module | Nose-centred radar envelope, radome window, CAN-FD harness clearance |
| Power connector | Anderson SB50 class connector | Keyed service/traction connector envelope with cable strain-relief allowance |
| Access fastener | Camloc quarter-turn class fastener | Quarter-turn retainers on removable skirts, panels, and service lids |
| Linear guide | HIWIN HG class guide block | Guide-block envelope for removable bogie/motor service adapters |
| Gas spring | Stabilus LIFT-O-MAT class gas spring | Rod/cylinder/end-fitting envelope for supported service flaps |

The matching mechanical reference models are generated under
`mechanical-py/catalog/fixtures/` and the rolling-stock system
assemblies under `mechanical-py/catalog/rolling_stock/`.

Reference datasheets/product pages used for the current supplier-neutral
envelope geometry:
[Dellner automatic coupler Type 10](https://www.dellner.com/products/automatic-couplers/automatic-coupler-type-10),
[Wabtec/Vapor doors and access](https://www.wabteccorp.com/transit-bus/doors-access),
[Livox HAP specifications](https://www.livoxtech.com/hap/specs),
[TI AWR1843BOOST](https://www.ti.com/tool/AWR1843BOOST),
[Anderson SB50 datasheet](https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/DS-SB50.pdf),
[HIWIN HGW25CC catalogue page](https://www.hiwin.de/sk/Shop/Profilschienenf%C3%BChrungen/Laufwagen/Kugelf%C3%BChrungen/HG-QH/HGW-QHW/HGW25CCZAC/p/5-001153),
and [Stabilus LIFT-O-MAT](https://www.stabilus.com/products/gas-springs/lift-o-mat).

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
