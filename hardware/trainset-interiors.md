# Trainset interiors and closures — COTS equipment catalogue

The `light-metro-3car` body is a welded steel primary frame with
composite non-structural side/roof/nose panels. Passenger-facing
equipment is not bespoke OSR hardware: doors, windows, HVAC,
lighting, seats, grab rails, PIS, CCTV, and intercom are COTS rail
or heavy-duty bus modules installed into reserved envelopes.

This file is the supplier-neutral catalogue promised by
[RFC 0008](../docs/rfcs/0008-rolling-stock-reference-design.md).
The envelope is the contract; named SKU classes are examples only.
Any replacement is acceptable if it fits the envelope, stays inside
the mass/power budget, exposes the required interface, and arrives
with usable certification evidence.

Related rolling-stock package:

- [`body.md`](../docs/rolling-stock/light-metro-3car/body.md)
- [`fabrication-plan.md`](../docs/rolling-stock/light-metro-3car/fabrication-plan.md)
- [`bom-skeleton.md`](../docs/rolling-stock/light-metro-3car/bom-skeleton.md)

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
| Roof HVAC | 1 | ≤ 2 700 L × 1 900 W × 450 H mm | 420 kg | 20 kW cooling electrical allowance | Direct-HV DC input, condensate drain, CAN/Ethernet diagnostics |
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
| Door cassette | Knorr-Bremse/IFE, Wabtec/Faiveley, Kangni electric rail sliding or plug door systems | Top operator rail, hanger rollers, controller/diagnostics box, two sliding leaves, bonded glass, obstruction light curtain, anti-pinch edge, lock/release unit, threshold drainage, gap-filler hinge |
| Nose sensing | Rail Vision MainLine / Ouster OS1 / LSLiDAR train-end intrusion class | Rail-grade LIDAR shroud, heated optical window, wide/narrow/thermal camera pods, radar, wash/wipe, service fasteners, 24 V feed allowance |
| Radar | TI AWR1843BOOST class 77 GHz radar module | Nose-centred radar envelope, radome window, CAN-FD harness clearance |
| Power connector | Anderson SB50 class connector | Keyed service/traction connector envelope with cable strain-relief allowance |
| Access fastener | Camloc quarter-turn class fastener | Quarter-turn retainers on removable skirts, panels, and service lids |
| Linear guide | HIWIN HG class guide block | Guide-block envelope for removable bogie/motor service adapters |
| Gas spring | Stabilus LIFT-O-MAT class gas spring | Rod/cylinder/end-fitting envelope for supported service flaps |

The matching mechanical reference models are generated under
`mechanical-py/catalog/fixtures/` and the rolling-stock system
assemblies under `mechanical-py/catalog/rolling_stock/`.

The passenger fit-out source now generates a separate cost/source CSV at
`build/bom/rolling_stock_cots_fitout_bom.csv`.
Each row carries quantity per car, quantity per consist, low/base/high
unit cost, mass, power, public source URL, and the geometry basis used
for the supplier-neutral CAD envelope.

Reference datasheets/product pages used for the current supplier-neutral
envelope geometry:
[Dellner automatic coupler Type 10](https://www.dellner.com/products/automatic-couplers/automatic-coupler-type-10),
[Knorr-Bremse/IFE train entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/),
[Rail Vision MainLine](https://railvision.io/main-line/),
[Ouster OS1 LIDAR](https://ouster.com/product-os1/),
[LSLiDAR train-end railway intrusion detection](https://www.lslidar.com/solution/rail-transportation/train-end-railway-intrudment-inspection-system/),
[TI AWR1843BOOST](https://www.ti.com/tool/AWR1843BOOST),
[Anderson SB50 datasheet](https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/DS-SB50.pdf),
[HIWIN HGW25CC catalogue page](https://www.hiwin.de/sk/Shop/Profilschienenf%C3%BChrungen/Laufwagen/Kugelf%C3%BChrungen/HG-QH/HGW-QHW/HGW25CCZAC/p/5-001153),
and [Stabilus LIFT-O-MAT](https://www.stabilus.com/products/gas-springs/lift-o-mat).

## Vendor fit-in shortlist

These supplier families are now reflected in the CAD labels and BOM
notes. The exact SKU remains a v2 procurement decision.

| Module | Reference families | Current envelope reservation |
|---|---|---|
| Door cassette | Knorr-Bremse/IFE entrance systems, Wabtec/Faiveley, Kangni | 1 250 × 2 000 mm clear opening; cassette controller, light curtain, pressure edge, drain scuppers |
| Side glazing | AGC Lamisafe/Heatlight W, Pilkington rail glazing, Saint-Gobain transport glazing | 1 400 × 900 mm laminated cassette with heated busbar option and drain channel |
| Floor covering | Altro Transflor Tungsten, Forbo transport flooring | 2 mm pre-cut anti-slip sheets bonded over removable floor and hatch panels |
| Seats | Compin-Fainsa SB09, Kiel, Grammer, McConnell | Cantilevered longitudinal bench over the under-seat battery strake |
| Lighting | Teknoware rolling-stock lighting, Luminator rail lighting | Continuous main/emergency ceiling channels plus sealed exterior head/tail/marker cassettes |
| PIS and audio | Luminator onboard displays/audio, Televic TRACS/GSP | Above-door VESA plates, PA speaker backboxes, amplifier/controller trays |
| HVAC | Liebherr rail HVAC, Knorr-Bremse Merak, Wabtec/Faiveley, Hispacold | Roof curb, compact/split unit envelope, pressure damper, filter cassette, drains, drop ducts |
| Battery package | EVE or qualified equivalent high-power LFP system | Under-seat sealed modules with cold plates, BMS/HVIL harness, outward vent, off-gas detection, and water-mist interface |
| Motor/brake | TSA/ABB/Skoda PMSM motors; Knorr-Bremse WheelAct/AxleAct or Wabtec Faiveley brakes | Axle-hung motor package and compact caliper package with mounting/diagnostic details |
| Coupler | Dellner Type 10, Voith Scharfenberg class | Crashworthy pocket, gas-hydraulic/deformation unit allowance, D-REX Ethernet and pneumatic heads |
| T-OBS nose module | Rail Vision MainLine, Ouster OS1, LSLiDAR train-end intrusion | LIDAR, thermal/wide/narrow camera pods, radar, ultrasonic, heater/wash/wipe service hardware |

## Generated fit-out cost band

Generated from `mechanical-py/src/osr_mech/rolling_stock/cots_equipment.py`
for one `light-metro-3car` consist:

| Module | Qty / consist | Base USD | Low-high USD | Shape basis |
|---|---:|---:|---:|---|
| Side glazing panel | 18 | 27 000 | 17 100-46 800 | Laminated/heated rail glazing cassette |
| Rooftop HVAC unit | 3 | 75 000 | 54 000-126 000 | Compact/split passenger-saloon rail HVAC |
| Continuous LED ceiling strip | 6 | 9 000 | 5 400-15 000 | Serviceable main/emergency lighting rail |
| Passenger-information LCD | 12 | 9 600 | 5 400-21 600 | Luminator rail display datasheet dimensions |
| Longitudinal bench run | 18 | 24 000 | 14 400-45 000 | SB09-style removable-pad light-alloy bench |
| Vertical grab pole | 24 | 7 992 | 3 840-16 800 | Stainless modular stanchion with flanges |
| Emergency intercom / help-point | 6 | 4 800 | 2 100-10 800 | Recessed SIP/audio help-point module |

## Candidate supplier classes

Named suppliers are examples of the class of product, not a locked
vendor list.

| Module | Example class | Required evidence |
|---|---|---|
| Door cassette | Knorr-Bremse/IFE, Wabtec/Faiveley, Fuji, Nanjing Kangni rail door family | EN 14752 or equivalent, obstruction detection, lifecycle test, emergency release |
| Side glazing | AGC/Pilkington/Saint-Gobain rail laminated safety glass | EN 15152 or equivalent, impact, fire/smoke data for seals |
| HVAC | Liebherr, Knorr-Bremse Merak, Wabtec/Faiveley, Hispacold roof HVAC | EN 50155/50121 where applicable, +50 °C performance curve, refrigerant data |
| Lighting | Teknoware/Luminator rail LED strip or troffer modules | EN 45545 material data, EMC evidence, emergency-mode behaviour |
| Seats | Compin-Fainsa, Kiel, Grammer, McConnell, local bus/rail equivalent | EN 45545 R7, static strength, vandal-resistance data |
| Grab rails | Stainless modular rail/bus stanchion system | Pull-load data, corrosion grade, fastener spec |
| PIS displays | Luminator/Televic/IEI/Litemax rail LCD class | EN 50155 preferred or vibration/temperature evidence |
| CCTV | Axis/Hikvision/industrial PoE camera class in rail enclosure | EMC/vibration evidence, cybersecurity hardening path |
| Intercom | Televic TRACS, Luminator audio, Zenitel/Vingtor, Commend rail SIP intercom class | EN 50155 preferred, audio intelligibility, emergency-call behaviour |
| Floor/interior panels | Altro/Forbo rail flooring plus phenolic/FRP rail interior panel supplier | EN 45545 HL2 R1/R5 evidence, cleanability, repair method |

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
[`docs/rolling-stock/light-metro-3car/compliance.md`](../docs/rolling-stock/light-metro-3car/compliance.md).
