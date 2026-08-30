# Procurement BOM skeleton — `light-metro-3car`

This is the **source-identified parts list** a fabricator uses to
price the consist. Parts split three ways:

- **SOURCE** — commodity off-the-shelf. Distributor, catalogue, or
  marketplace quote line available; no engineering work required.
- **MAKE** — fabricator produces in-house. Single-supplier tender.
- **BID** — multi-supplier tender. The deployment's procurement
  office runs the bid.

Costs are BASE USD volume-100. Country cost factor from
[`lib/templates/country-costs.toml`](../../../lib/templates/country-costs.toml)
scales them per deployment.

Scope note: this is a **consist-level procurement BOM**, not a final
manufacturer MBOM. It now covers every train-level subassembly needed
to build, commission, and maintain the v1 trainset concept; supplier
drawings still break many lines into child parts during v2.

City CAPEX uses this BOM as an audit lower bound, not as the final
rolling-stock price. The deployable trainset cost is carried in
[`lib/templates/capex-costs.toml`](../../../lib/templates/capex-costs.toml)
as a local-owner production planning unit, and the shared national railway
production-plant setup allowance is 60 k USD per supported vehicle/car module
base, with 120 k USD per vehicle/car module retained as a high
sensitivity check.

Generated CSV outputs:

- `build/bom/rolling_stock_bom.csv`
  adds low/base/high cost bands to every BOM line.
- `build/bom/rolling_stock_cots_fitout_bom.csv`
  is generated directly from the source-shaped COTS fit-out catalogue
  in `design/component-catalogue`.

Cost confidence:

- **SOURCE** lines use public catalogue/distributor or commodity quote
  bands until procurement replaces them with current supplier quotes.
- **MAKE** lines use local fabrication estimate bands until a shop
  route, fixture plan, and labour-rate pack are issued.
- **BID** lines are tender-only rail components. Public product pages
  inform shape, interface, and supplier class; exact price requires RFQ.

## Concept alignment

This BOM is keyed to the visual and layout concept in
[`docs/assets/solar-metro-trainset.png`](../../../docs/assets/solar-metro-trainset.png):

- 3 cars, each 16.5 m, **49.5 m over couplers**.
- Each car repeats the same self-contained architecture: one powered
  bogie, one trailer bogie, one 180 kWh usable under-seat battery pack,
  two independent motor controllers, isolated LV DC/DC, and protected
  station/PV DC interfaces.
- 3 powered bogies and 3 trailer bogies total.
- 6 traction motors total; the planning profile caps consist traction
  peak at 1.8 MW.
- Roof solar arrays on each car, with compact end HVAC modules.
- Wide passenger windows, identical multi-part fiberglass driverless end
  cowls with one large dark panoramic glass pane and LED headlamp/marker
  clusters, white/silver body shell, green waist band, dark skirts, and
  yellow door thresholds.
- Standard bogies under every car, requiring ~3 m high-floor end decks
  over the bogies and a ~10 m low-floor centre zone with two door
  openings per side.
- Batteries remain under longitudinal seats, not on the roof or deep
  underframe.

## Vendor fit-in references

These are reference product families used to size the CAD envelopes
and short-list tender alternates. They are not sole-source selections:
the v2 release gate still accepts any supplier that fits the envelope,
keeps mass/power within budget, and supplies certification evidence.

| BOM lines | Reference families fitted into the design | Fit-in implication |
|---|---|---|
| B10, B27 | [AGC Lamisafe/Heatlight railway glazing](https://www.agc.com/en/everyday/mobility/train.html), Pilkington/Saint-Gobain rail glazing | Laminated bonded cassette, drain channel, optional heated anti-fog busbar |
| B11, B25 | [Knorr-Bremse/IFE entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/), Wabtec/Faiveley, Kangni | Sliding/plug door cassette with controller, obstruction detection, emergency release, sill drainage |
| B12, B13 | [Altro Transflor Tungsten rail flooring](https://www.altro.com/us/products/altro-transflor-tungsten), Forbo transport flooring | 2 mm anti-slip pre-cut floor covering over removable low-floor and service-bay panels |
| B14, B15 | [Compin-Fainsa SB09 Metro/LRV seat](https://www.compinfainsa.com/product/railway-seats-and-interiors-sb09), Kiel, Grammer, McConnell | Longitudinal bench stays cantilevered over battery strakes with removable pads |
| B16, B17 | [Teknoware rolling-stock lighting](https://www.teknoware.com/rail-road/rolling-stock-lighting-and-interiors/), Luminator lighting | Continuous main/emergency lighting channels plus sealed head/tail/marker cassettes |
| B18, B19, E14 | [Luminator onboard products](https://www.luminator.com/en-us/products.html), Televic GSP | Above-door VESA screens, PA speakers, audio/data trunks, amplifier/service trays |
| B22, B23 | [Dellner automatic coupler Type 10](https://www.dellner.com/products/automatic-couplers/automatic-coupler-type-10), Voith Scharfenberg class | Type 10 pocket with crash absorber, electrical head, pneumatic lines, D-REX Ethernet carrier |
| B9, B24, B29 | [Hübner tram/metro articulation and gangway systems](https://www.hubner-group.com/en/products/articulations/articulation-systems-for-trams/), [Hübner gangway systems](https://www.hubner-group.com/en/products/gangway-systems/gangway-systems-for-metros-subways-and-suburban-railways/), [Schaeffler central articulated pivot](https://www.schaeffler.com/remotemedien/media/_shared_media/08_media_library/01_publications/schaeffler_2/publication/downloads_18/img_de_en.pdf) | Lower spherical pivot, anti-lift keeper, upper articulation links, double-wall bellows, turntable, energy guidance, adapter-frame shim pack |
| G9 ref | [Knorr-Bremse WheelAct/AxleAct brake actuators](https://rail.knorr-bremse.com/en/us/portfolio/products-and-systems/braking-systems/actuation/), Wabtec Faiveley | Compact caliper envelope now includes actuator, spring park brake, pads, ports, wear indicator |
| T1, T3 ref | Inovance HM47/LD32-class heavy-vehicle PMSM/controller set or qualified equivalent | One controller per motor; published OSR voltage/current, safe-torque-off, CAN, cooling, mounting, EMC, vibration and fault interface remains supplier-neutral |
| T5, T6, T16, T17 | EVE-class liquid-cooled railway/high-power LFP or qualified equivalent | Eight fire-resistant under-seat module compartments per car with two string zones, cold plates, BMS harness, outward vents, off-gas detection and localized mist |
| T14 ref | Longertek-class direct-HV DC rail HVAC or qualified equivalent | Roof curb sized for a 650–700 V DC input unit with internal motor electronics, pressure-protection damper, filter, drains and removable ducts |
| T21, T22 | [Sunman eArc lightweight modules](https://www.sunman-energy.com/), [Solbian flexible solar panels](https://www.solbian.eu/en/4-solar-panels), [SnapNrack Ultra Rail](https://www.snapnrack.com/ultra-rail-roof-mount-system), [IronRidge QRail](https://www.ironridge.com/quickmount/qrail-system/) | CAD reserves both bonded flexible laminates and raised clamped rail panels, with junction boxes, fire isolation, roof raceways, MPPT combiner, and a filtered low-pressure air-knife cleaner |
| T12, T19, T23 | Supplier-neutral side contact plus protected 800 V-class vehicle DC interface | Side contact is the single production interface; station cabinet owns the 500 kW conversion and two contacts share that cabinet budget |
| E18, E19 | [Rail Vision MainLine](https://railvision.io/main-line/), [Ouster OS1](https://ouster.com/product-os1/), [LSLiDAR train-end intrusion system](https://www.lslidar.com/solution/rail-transportation/train-end-railway-intrudment-inspection-system/) | Front/back sensor mount reserves LIDAR, thermal/wide/narrow cameras, radar, heaters, wash/wipe |

## Marketplace sanity check

Alibaba and AliExpress were checked as listed-price marketplace anchors
for every BOM line, using a directly comparable listing where possible
and a clearly marked marketplace proxy where the part is custom,
safety-critical, or tender-only. Full line-by-line anchors are in
[marketplace-price-anchors.md](marketplace-price-anchors.md). These
references constrain the estimate; they do not replace rail supplier
qualification, test reports, fire/smoke/toxicity evidence, freight,
duty, warranty terms, or acceptance testing.

| Marketplace anchor | BOM lines adjusted | Pricing implication |
|---|---|---|
| [Full marketplace anchor ledger](marketplace-price-anchors.md) | B1-B29, G1-G20, T1-T23, E1-E23, A1-A4 | Every BOM line now has an Alibaba, AliExpress, or PriceArchive-listed anchor/proxy and a marketplace-only direct-material base |
| [Alibaba bus seats](https://www.alibaba.com/showroom/plastic-bus-seat.html), [handrail fittings](https://www.alibaba.com/showroom/bus-handrails.html), [24 V bus lighting](https://www.alibaba.com/showroom/bus-interior-light-lamp.html), [passenger displays](https://www.alibaba.com/showroom/bus-passenger-information-display.html), and [bus CCTV kits](https://www.alibaba.com/showroom/bus-cctv-systems.html) | B14-B19, E14, E15 | Interior fit-out moved from rail-OEM pricing toward bus/metro commodity modules with qualification uplift |
| [Alibaba fire-rated composite panels](https://www.alibaba.com/showroom/fire-rated-composite-panel.html), [bus/train vinyl flooring](https://www.alibaba.com/showroom/bus-vinyl-flooring.html), and [laminated transport glass](https://www.alibaba.com/showroom/train-tempered-laminated-glass-window.html) | B6, B7, B10, B13, B21, B28 | Shell panels, floor finish, window cassettes, and trim reduced, while end glazing stays BID because it is curved/heated/sensor-integrated |
| [Alibaba railway axle bearings](https://www.alibaba.com/showroom/railway-vehicle-axle-bearing-price.html), [rail air springs](https://www.alibaba.com/showroom/railway-air-spring.html), [rail dampers](https://www.alibaba.com/showroom/railway-hydraulic-damper.html), and [rail brake pads](https://www.alibaba.com/showroom/brake-pads-railway.html) | G4-G8, G10-G16, G19 | Bogie consumables reduced to marketplace-plus-documentation levels; wheelsets and calipers remain tender-only |
| [Alibaba 150 kW EV PMSM motors](https://www.alibaba.com/showroom/pmsm-150kw-motor.html), [EV charge modules](https://www.alibaba.com/showroom/30kw-dc-module.html), [bus roof HVAC](https://www.alibaba.com/showroom/bus-rooftop-air-conditioning.html), and [1 000 V DC contactors](https://www.alibaba.com/showroom/1000v-dc-contactors.html) | T1-T4, T9-T14, T16, T19, T20, T23 | Traction and power electronics reduced to EV/bus commodity anchors, with rail integration margin retained |
| AliExpress price-tracked [10.1 in touchscreens](https://www.pricearchive.org/search/aliexpress.com/touch-screen-10.1/1), [PoE cameras](https://www.pricearchive.org/aliexpress.com/item/1005009073001872), and [small HV contactors](https://www.pricearchive.org/aliexpress.com/item/1005004649240380) | E10, E15, E21; T11 lower-bound only | Used as a lower-bound cross-check for non-safety electronics and spares; qualified main HV contactors stay B2B-sourced |

## Body + interior

| Line | Desc | Qty per consist | Source | Base USD | Notes |
|---|---|---|---|---|---|
| B1 | S355 RHS tube, underframe + side/roof frame | 3.2 t | SOURCE | 3 000 | Alibaba S355 RHS tube anchor; cut/bend/weld locally |
| B2 | S355 folded plate, bolsters/coupler pockets/brackets | 2.0 t | SOURCE | 2 000 | Alibaba S355 plate anchor; press-brake + weld |
| B3 | CNC cutting, drilling, fixture consumables | set | MAKE | 6 000 | Alibaba fabrication-service proxy; per consist allocation |
| B4 | Weld consumables + shielding gas | set | SOURCE | 2 000 | Alibaba welding-wire/gas anchor; EN 15085 WPS-controlled |
| B5 | Shot blast + zinc-rich primer + cavity wax | set | SOURCE | 4 000 | Alibaba zinc-rich primer/blast proxy; corrosion package |
| B6 | Clip-on fiberglass side body modules, fire-rated | 96 × 1 m modules | BID | 7 000 | One common 1,000 mm mould pitch with CNC-trimmed solid/window/door variants; GFRP needs EN 45545 evidence |
| B7 | Clip-on fiberglass roof modules, retainers, seals + skirts | 48 × 1 m roof modules + kit | BID | 4 000 | Reusable short moulds, keyed captive clips, anti-lift retainers, dry EPDM joints, and removable service skirts |
| B8 | Multi-part fiberglass A/B-end sensor cowl cast kits | 2 | BID | 4 000 | Alibaba FRP/composite proxy; CWL-FRP-01 through CWL-FRP-06 cast kit accepts one bonded panoramic glass pane, LED lamp clusters, washer/heater service hatches, and T-OBS aperture |
| B9 | Complete inter-car articulation/gangway module | 2 | BID | 30 000 | Alibaba train-gangway anchor; lower pivot, upper links, bellows, turntable floor |
| B10 | COTS laminated safety-glass window cassette | 18 | SOURCE | 6 000 | Alibaba laminated transport-glass anchor; bonded/gasketed rail-style cassette |
| B11 | COTS electric plug/sliding door cassette | 12 | BID | 90 000 | Alibaba sliding-door-system proxy; door, controller, obstruction sensors, seals, emergency release |
| B12 | Stepped floor board + hatch system, EN 45545 | 135 m² | SOURCE | 6 000 | Marketplace honeycomb/composite-board anchor; 350 mm low centre, 760 mm bogie-end decks |
| B13 | Vinyl/rubber floor covering, EN 45545 R5 | 135 m² | SOURCE | 1 500 | Alibaba bus/train vinyl-floor anchor |
| B14 | COTS longitudinal seat modules, EN 45545 R7 | 60 seats | SOURCE | 6 000 | Alibaba bus/metro seat anchor; rail fire-test evidence still required |
| B15 | COTS grab rail + stanchion kit | set | SOURCE | 2 500 | Alibaba bus handrail fittings anchor; stainless modular system |
| B16 | COTS interior LED lighting kit | 3 cars | SOURCE | 1 500 | Alibaba/AliExpress 24 V bus-light anchor; emergency mode |
| B17 | COTS exterior marker + head/taillight kit | set | SOURCE | 1 200 | Alibaba bus lamp anchor; sealed head/tail/marker class |
| B18 | COTS PIS display + speaker kit | set | SOURCE | 3 000 | Alibaba bus/metro display anchor; interior/exterior |
| B19 | COTS CCTV + intercom kit | set | SOURCE | 2 500 | Alibaba bus CCTV plus AliExpress PoE camera anchor; passenger intercom included |
| B20 | Paint + 2K urethane topcoat | set | SOURCE | 3 000 | Alibaba automotive coating proxy; white/silver base coat under concept livery |
| B21 | Interior FR panels + trim clips | set | SOURCE | 5 000 | Alibaba FR/composite panel anchor; supplier-certified HL2 required |
| B22 | Scharfenberg Type 10 end coupler + electric head | 2 | BID | 8 000 | Alibaba railway-coupler proxy; rescue unlock handle, certified coupler RFQ required |
| B23 | EN 15227 crash energy absorber / crush-can set | 2 | BID | 4 000 | Alibaba draft-gear/crash-part proxy; bolts to coupler pocket |
| B24 | Inter-car energy-guidance trainline and service-loop kit | 2 | SOURCE | 4 000 | Commodity HV jumper/cable-chain anchor; TCN-E, CAN-FD, 24 V, 110 V, EB loop, coolant, HVAC sleeve |
| B25 | Door sill gap-filler + external emergency release kit | 12 | BID | 6 000 | Commodity actuator anchor plus door-safety qualification; per exterior door cassette |
| B26 | Jacking, lifting, towing, and recovery fittings | set | MAKE | 3 000 | Alibaba machined/welded steel proxy; welded pads, tow eyes, labels |
| B27 | Single laminated panoramic end-glass assemblies | 2 | BID | 10 000 | Alibaba train curved/laminated glass anchor; RF-transparent heated/de-iced end glazing still needs RFQ |
| B28 | Concept livery package: white/silver body, green band, yellow thresholds | set | SOURCE | 2 000 | Alibaba vinyl/paint-mask anchor; exterior decals and safety edging |
| B29 | Articulation adapter-frame steel, anti-lift, and shim kit | 2 | MAKE | 6 000 | Marketplace machined-steel proxy; underframe anchors, clevis brackets, shear-key datums, machined shims |
| **Body + interior subtotal** | | | | **233 200** | |

## Bogies (6 per consist)

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| G1 | Welded common bogie frame, powered build | 3 | MAKE | 15 000 | Alibaba train-bogie fabrication proxy; EN 15085 CL1 required |
| G2 | Welded common bogie frame, trailer build | 3 | MAKE | 9 000 | Alibaba bogie-frame/rail-part proxy; fresh OSR frame, no recovered freight-frame splice |
| G3 | Wheelset monobloc (RFC 0022, S1002) | 12 | BID | 18 000 | Alibaba railway wheelset anchor; inspection and profile verification required |
| G4 | Axle bearing box (SKF / FAG) | 24 | SOURCE | 12 000 | Alibaba railway axle-bearing/box anchor with certified bearing uplift |
| G5 | Primary chevron spring | 24 | SOURCE | 4 800 | Alibaba rail spring/rubber anchor; qualified compound required |
| G6 | Secondary air spring + levelling valve | 12 | SOURCE | 6 000 | Alibaba railway air-spring anchor; matches RFC 0022 twin-bellows spec |
| G7 | Secondary damper | 12 | SOURCE | 3 000 | Alibaba railway hydraulic-damper proxy |
| G8 | Brake disc | 12 | SOURCE | 12 000 | Alibaba rail brake-disc/brake-part proxy; EN material traceability required |
| G9 | Electromagnetic brake caliper | 24 | BID | 12 000 | Alibaba caliper proxy; rail electromagnetic caliper RFQ required |
| G10 | Park-brake spring assembly | 24 | SOURCE | 2 400 | Alibaba rail spring anchor; caliper integration remains G9 |
| G11 | Centre-pin ring bearing + PTFE slider | 6 | SOURCE | 3 000 | Alibaba heavy bearing/PTFE slider anchor |
| G12 | Yaw-restraint link + bushes | 12 | SOURCE | 1 800 | Alibaba rail bushing/link anchor |
| G13 | Cable-guide + centre-pin assembly | 6 | MAKE | 3 000 | Marketplace rail-part fabrication proxy |
| G14 | Wheel-tach (quadrature encoder) | 12 | SOURCE | 600 | Alibaba/AliExpress encoder anchor; rail harnessing in G17 |
| G15 | Axle bearing temp sensor | 24 | SOURCE | 500 | Commodity sealed temperature-sensor anchor |
| G16 | Brake pad / friction lining kit | 12 axle sets | SOURCE | 1 500 | Alibaba rail brake-pad anchor; commissioning set, per disc |
| G17 | WSP + brake control harness | 6 | MAKE | 3 000 | Tacho, caliper command, temp sensor loom |
| G18 | Motor cradle + torque-link weldment | 3 powered bogies | MAKE | 6 000 | Alibaba machined/welded steel proxy; uses RFC 0022 motor mount datum |
| G19 | Flexible gear coupling / torque flange set | 6 | BID | 3 000 | Alibaba industrial coupling anchor; motor-to-reduction gear interface |
| G20 | Bogie inspection covers and guards | 6 | MAKE | 3 000 | Removable non-structural covers |
| G21 | Suspension air-supply compressor, dryer, reservoir, and isolation manifold | 3 car sets | SOURCE | 6 000 | Local secondary-suspension air only; no trainwide pneumatic brake, door, or coupler supply |
| **Bogies subtotal** | | | | **125 600** | |

## Traction + power

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| T1 | HM47-class PMSM axle motor (350 kW short peak candidate) | 6 | BID | 36 000 | RFQ planning share of the $48k–72k six-set motor/controller target; rail duty evidence excluded |
| T2 | Single-stage reduction gear, ratio to be selected | 6 | BID | 15 000 | Current 6.5:1 CAD seed is not released; select from torque-speed, wheel, adhesion, grade and thermal analysis |
| T3 | LD32-class independent motor controller | 6 | BID | 24 000 | One per motor; 400–750 V candidate envelope requires transient-margin qualification |
| T4 | Cold-plate + traction cooling branch | 6 | SOURCE | 6 000 | One monitored branch per axle controller/motor set |
| T5 | LFP under-seat car pack (180 kWh usable / 225 kWh gross) | 3 | BID | 75 000 | EVE-class RFQ target; includes liquid-cooled module hardware but not unsupported commodity-price claims |
| T6 | BMS electronics (pack-level) | 3 | BID | 4 500 | Commodity pack-BMS anchor; rail battery supplier must verify HVIL, thermal, and fire-path interfaces |
| T7 | Pack cooling plate set | 3 | SOURCE | 2 000 | Alibaba battery cold-plate anchor |
| T8 | Under-seat aluminium module enclosure set | 3 | MAKE | 6 000 | Alibaba aluminium battery-box fabrication proxy |
| T9 | Battery temperature/off-gas detection plus electrical-enclosure smoke detection | 3 car sets | BID | 10 800 | Qualified detector response, calibration, poisoning and false-positive evidence required |
| T10 | Localized battery water-mist reservoir, DC pump, stainless pipe, nozzles and feedback sensors | 3 car sets | BID | 9 000 | Battery compartments only; includes reservoir level, pump, pressure and flow diagnostics |
| T11 | 800 V-class HV distribution, contactors, IMD and bus bars | 3 | BID | 10 000 | Train-level RFQ target $8k–12k; interrupt rating and isolation architecture must close |
| T12 | Standard station charging side-pin connector | 3 | BID | 4 500 | Touch-safe sequence, HVIL, weld detection, contact monitoring and emergency isolation |
| T13 | Isolated 800 V to 110/48/24 V DC/DC set | 3 | BID | 7 500 | No central 400 V AC bus; safety domains remain independent |
| T14 | Direct-HV DC packaged roof HVAC unit (24 kW each, per car) | 3 | BID | 17 250 | 650–700 V input, internal motor electronics, 50 °C curve and rail evidence required |
| T15 | Regen dump resistor (roof-mount) | 3 | SOURCE | 1 000 | Alibaba braking-resistor proxy; one per car, consist cost allowance shown |
| T16 | Battery module service disconnect, fuses, and contactors | 24 module positions | SOURCE | 2 400 | Alibaba/AliExpress HV contactor/fuse anchor; 8 modules per car per traction.md |
| T17 | Battery vent duct + fire exhaust path | 3 cars | MAKE | 3 000 | Alibaba sheet-metal duct proxy; side vent, intumescent edge seals |
| T18 | HV cable, bonding strap, and EMC filter set | 3 cars | MAKE | 12 000 | 800 V-class pack/controller/station/PV paths with physical segregation |
| T19 | Station-charge connector actuator + contact monitor | 3 | BID | 3 000 | Commodity actuator/sensor anchor; completes side-pin connector line T12 |
| T20 | Coolant pump, hose, manifold, and bleed kit | 3 cars | SOURCE | 2 500 | Alibaba EV coolant-pump/hose anchor; battery, inverter, motor, HVAC tie-in |
| T21 | Commodity full-roof solar panel set | 3 cars | SOURCE | 6 000 | Alibaba 400 W rigid/flexible solar-panel anchors; twelve modules per car / 36 modules per trainset |
| T22 | Roof solar mounts, MPPT combiner, isolation, and roof harness | 3 cars | SOURCE | 6 000 | Alibaba roof-mount/combiner/MPPT proxies; bond pads, raised rails, edge clamps, junction boxes, fire-isolation labels |
| T23 | Per-car roof MPPT and station-DC protection/controller | 3 | BID | 3 000 | Station owns the 500 kW DC/DC power conversion; car rack provides PV MPPT, protection, precharge and arbitration |
| **Traction + power subtotal** | | | | **266 450** | |

## Electronics + safety

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| E1 | T-ECU/S board (2× RP2350 + CM5) | 2 | BID | 1 200 | Alibaba PCB-assembly proxy; custom baseboard per RFC 0007 §4 |
| E2 | T-ECU/A board (CM5) | 2 | BID | 1 500 | Alibaba PCB-assembly proxy; RFC 0007 standard, two units per consist |
| E3 | ADIS16505 IMU (or BMI088) | 2 | SOURCE | 200 | AliExpress/PriceArchive IMU-module proxy |
| E4 | u-blox NEO-F10N GNSS | 2 | SOURCE | 100 | AliExpress/PriceArchive GNSS module proxy |
| E5 | PN5180 NFC balise reader | 1 | SOURCE | 20 | AliExpress/PriceArchive PN5180 proxy |
| E6 | ATECC608B SE chip (on T-ECU/S + T-ECU/A carriers) | 6 | SOURCE | 20 | AliExpress/PriceArchive secure-element proxy; T-OBS anchors included inside E18 |
| E7 | Cat.22 5G M.2 module | 1 | SOURCE | 200 | AliExpress/PriceArchive 5G module proxy |
| E8 | LoRa SX1276 breakout | 1 | SOURCE | 20 | PriceArchive SX1276 LoRa module anchor |
| E9 | NVMe SSD 256 GB (event recorder) | 1 | SOURCE | 40 | AliExpress/PriceArchive NVMe proxy |
| E10 | 10.1" maintenance/service touchscreen | 2 | SOURCE | 300 | AliExpress/Alibaba industrial touchscreen anchor; hidden end-cabinet HMI, not a driver cab |
| E11 | Depot manual-control pendant + keyed enable | 2 | BID | 500 | Alibaba industrial pendant/switch proxy; normally stowed |
| E12 | Emergency plunger (hardwired) | 2 | SOURCE | 40 | AliExpress/Alibaba emergency switch proxy |
| E13 | Depot enable key-switch and guarded motion consent | 2 | SOURCE | 100 | Alibaba keyed-switch/guarded-switch proxy |
| E14 | PIS display (exterior + interior) | 12 | SOURCE | 3 000 | Alibaba bus/metro LCD/LED display anchor |
| E15 | CCTV camera (forward + door-sill + in-car) | 20 | SOURCE | 600 | Alibaba bus CCTV plus AliExpress PoE camera anchor |
| E16 | 2oo2 relay stage (per safety output) | 4 | SOURCE | 200 | Alibaba safety-relay proxy |
| E17 | Cable harness (pre-terminated, per car) | 3 | MAKE | 9 000 | Alibaba wiring-harness fabrication proxy |
| E18 | T-OBS complete nose module | 2 | BID | 8 000 | Alibaba industrial-LIDAR/camera/radar proxy; rail T-OBS supplier RFQ required |
| E19 | Sensor-window heater, washer, and service cover kit | 2 | SOURCE | 1 000 | Commodity washer/heater actuator anchor; keeps nose sensors inspectable in service |
| E20 | Door-sill camera / obstruction sensor harness | 12 doors | MAKE | 3 000 | Alibaba harness/camera proxy; ties doors to CCTV + door control |
| E21 | Roof antenna kit | set | SOURCE | 300 | Alibaba/AliExpress multi-antenna anchor; 5G MIMO, LoRa, GNSS, public-safety blank |
| E22 | DIN cabinets, power distribution, and terminal blocks | 3 cars | MAKE | 3 000 | Alibaba DIN cabinet/terminal-block proxy; T-ECU, BMS, door, HVAC cabinets |
| E23 | Crashworthy event-recorder memory module | 1 | SOURCE | 2 000 | Alibaba rugged recorder/SSD proxy; complements E9 NVMe operational recorder |
| **Electronics + safety subtotal** | | | | **34 340** | |

## Safety, accessibility, and maintainability

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| A1 | Wheelchair bay fixtures + passenger call buttons | 6 bays | SOURCE | 1 000 | Alibaba accessibility fixture/call-button anchor; two PRM spaces per car |
| A2 | Tactile / visual safety signage and labels | set | SOURCE | 500 | Alibaba safety-label/signage anchor; doors, emergency, high-voltage, lift points |
| A3 | Emergency lighting + exit marker kit | 3 cars | SOURCE | 1 000 | Alibaba/AliExpress emergency LED anchor; battery-backed, EN 45545 materials |
| A4 | Fire extinguisher, first-aid, and incident-seal kit | set | SOURCE | 500 | Marketplace consumables anchor; operator restocks consumables |
| **Safety/accessibility/maintainability subtotal** | | | | **3 000** | |

## Consist total

| Bucket | Subtotal (USD) |
|---|---|
| Body + interior | 233 200 |
| Bogies (6 per consist) | 125 600 |
| Traction + power | 266 450 |
| Electronics + safety | 34 340 |
| Safety, accessibility, and maintainability | 3 000 |
| **Total direct-material consist** | **662 590** |

Generated cost band from the same line items:

| Case | Direct material | +28% labour / assembly | Planning total |
|---|---:|---:|---:|
| Low | 516 027 | 144 488 | 660 515 |
| Base | 662 590 | 185 525 | 848 115 |
| High | 1 031 521 | 288 826 | 1 320 347 |

**Marketplace listed-price per-consist floor (volume 100): 0.70-1.40 M
USD with assembly allowance, base approximately 0.90 M USD.**

This table is an audit lower bound for raw procurement. City CAPEX uses
the local-owner rolling-stock planning unit in
[`lib/templates/capex-costs.toml`](../../../lib/templates/capex-costs.toml):
**1.0 M USD per `light-metro-3car` trainset**. That unit includes local
assembly/labour, nominal per-train QA/acceptance evidence, and modest
local handover logistics. Fixtures/tooling live in the railway
production plant line; warranty, spares, and routine commissioning
support are OPEX.

For comparison, legacy-vendor light-metro trainsets in the target
regions typically land 4-6 M USD each. The marketplace floor shows how
cheap the commodity hardware can be, but it is not a certified rail
quote; supplier qualification, local production overhead, plant setup,
QA, and acceptance testing will lift any production purchase above this
floor.

## Per-deployment customisation

The operator's own procurement office fills in:

- Livery paint scheme (B20).
- Seat fabric colour (B14).
- TRG-1 5G carrier SIM spec (per-country mobile network).
- Public-safety radio band (E-: not in base BOM).
- Station contact adapter geometry only where a legacy pilot cannot use the
  standard side contact; voltage and cabinet architecture are not customized.

## v2 deliverables (not in v1)

- Supplier shortlist per BID line with qualification criteria.
- Lead-time analysis per SOURCE / MAKE / BID.
- Risk log: single-source parts + mitigation.
- Weight budget with per-line tare contribution + final target
  vs actual.
