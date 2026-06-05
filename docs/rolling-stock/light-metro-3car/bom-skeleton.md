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

City CAPEX uses this BOM as an audit lower bound, not as the delivered
rolling-stock price. The deployable trainset cost is carried in
[`lib/templates/capex-costs.toml`](../../../lib/templates/capex-costs.toml)
as a delivered planning unit, and the separate city railway
production-plant setup allowance is 100 k USD per vehicle/car module
base, with 200 k USD per vehicle/car module retained as a high
sensitivity check.

Generated CSV outputs:

- [`build/bom/rolling_stock_bom.csv`](../../../build/bom/rolling_stock_bom.csv)
  adds low/base/high cost bands to every BOM line.
- [`build/bom/rolling_stock_cots_fitout_bom.csv`](../../../build/bom/rolling_stock_cots_fitout_bom.csv)
  is generated directly from the source-shaped COTS fit-out catalogue
  in `mechanical-py`.

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

- 3 cars, each 17 m, **51 m over couplers**.
- Car 1 and Car 3 are powered; Car 2 is the unpowered trailer.
- 2 new powered bogies total, one at each outer end; 4 converted
  freight trailer bogies.
- 4 traction motors total, 600 kW peak consist output.
- Roof solar arrays on each car, with compact end HVAC modules.
- Wide passenger windows, segmented dark glass driverless end panes with
  LED headlamp/marker clusters, white/silver body shell, green waist
  band, dark skirts, and yellow door thresholds.
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
| T1 ref | [TSA rail traction motors](https://tsa.at/rail/), ABB Traction, Skoda Electric | PMSM package includes water jacket, mounting feet, terminal box, HV glands, resolver cover |
| T5, T6, T16, T17 | [Toshiba SCiB traction battery systems](https://www.global.toshiba/ww/products-solutions/railway/rolling-stock/energy-storage-applications.html), [Saft rail traction batteries](https://saft.com/en/mobility/rail-traction), CATL/HiNa Na-ion | Under-seat module envelope keeps OSR Na-ion primary, but reserves cold plate, BMS harness, vent/fire paths for rail battery suppliers |
| T14 ref | [Liebherr rail HVAC](https://www.liebherr.com/en-ca/aerospace-and-transportation-systems/solutions-and-services/solutions-for-railway/on-board-systems/classical-hvac-7178128), Knorr-Bremse Merak, Wabtec/Faiveley | Roof curb sized for compact/split saloon unit, pressure-protection damper, filter, drains, ducts |
| T21, T22 | [Sunman eArc lightweight modules](https://www.sunman-energy.com/), [Solbian flexible solar panels](https://www.solbian.eu/en/4-solar-panels), [SnapNrack Ultra Rail](https://www.snapnrack.com/ultra-rail-roof-mount-system), [IronRidge QRail](https://www.ironridge.com/quickmount/qrail-system/) | CAD reserves both bonded flexible laminates and raised clamped rail panels, with junction boxes, fire isolation, roof raceways, and MPPT combiner |
| T12, T19, T23 | [ABB BORDLINE rail converters](https://www.abb.com/global/en/areas/motion/traction/traction-converter/cc400), [SepsaMedha auxiliary converters/battery chargers](https://www.sepsamedha.com/products/auxiliary-power/), [Wabtec DepotPANTO](https://www.wabteccorp.com/transit-bus/e-bus-charging/depotpanto), [ABB HVC150](https://e-mobility.abb.com/en/products/power/hvc150) | Per-car charge inverter uses commodity DC charge power modules; side-pin primary keeps pantograph-down alternate as a deployment option |
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
| B6 | Composite side sandwich panels, fire-rated | 150 m² | BID | 9 000 | Alibaba fire-rated panel anchor; GFRP/basalt FR sandwich needs EN 45545 evidence |
| B7 | Composite roof fairings + skirts | 95 m² | BID | 4 000 | Alibaba fire-rated/composite-panel anchor; removable service panels |
| B8 | Composite end-glass sensor cowl shells | 2 | BID | 4 000 | Alibaba FRP/composite proxy; accepts segmented panoramic glass panes and LED lamp clusters |
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
| B27 | Segmented laminated glass end-pane assemblies | 2 | BID | 10 000 | Alibaba train curved/laminated glass anchor; RF-transparent heated/de-iced end glazing still needs RFQ |
| B28 | Concept livery package: white/silver body, green band, yellow thresholds | set | SOURCE | 2 000 | Alibaba vinyl/paint-mask anchor; exterior decals and safety edging |
| B29 | Articulation adapter-frame steel, anti-lift, and shim kit | 2 | MAKE | 6 000 | Marketplace machined-steel proxy; underframe anchors, clevis brackets, shear-key datums, machined shims |
| **Body + interior subtotal** | | | | **235 200** | |

## Bogies (6 per consist)

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| G1 | Welded bogie frame (new powered) | 2 | MAKE | 10 000 | Alibaba train-bogie fabrication proxy; EN 15085 CL1 required |
| G2 | Converted freight trailer bogie frame | 4 | MAKE | 12 000 | Alibaba bogie-frame/rail-part proxy; existing frame reworked with new bearings/brakes/air springs |
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
| G18 | Motor cradle + torque-link weldment | 2 powered bogies | MAKE | 4 000 | Alibaba machined/welded steel proxy; uses RFC 0022 motor mount datum |
| G19 | Flexible gear coupling / torque flange set | 4 | BID | 2 000 | Alibaba industrial coupling anchor; motor-to-reduction gear interface |
| G20 | Bogie inspection covers and guards | 6 | MAKE | 3 000 | Removable non-structural covers |
| **Bogies subtotal** | | | | **114 600** | |

## Traction + power

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| T1 | PMSM axle motor (150 kW peak) | 4 | BID | 30 000 | Alibaba 150 kW EV PMSM anchor plus rail mounting/cooling allowance |
| T2 | Reduction gear (single-stage 6.5:1) | 4 | BID | 10 000 | Alibaba industrial gearbox proxy; matches RFC 0008 / gearbox.py |
| T3 | SiC inverter (300 kW peak) | 2 | BID | 15 000 | Alibaba EV/PCS inverter proxy; one per powered bogie |
| T4 | Cold-plate + chiller for traction | 3 | SOURCE | 6 000 | Alibaba EV cooling-module anchor |
| T5 | Na-ion under-seat pack (150 kWh usable) | 3 | BID | 45 000 | Alibaba 150 kWh battery-pack anchor; rail battery certification excluded |
| T6 | BMS electronics (pack-level) | 3 | BID | 4 500 | Commodity pack-BMS anchor; rail battery supplier must verify HVIL, thermal, and fire-path interfaces |
| T7 | Pack cooling plate set | 3 | SOURCE | 2 000 | Alibaba battery cold-plate anchor |
| T8 | Under-seat aluminium module enclosure set | 3 | MAKE | 6 000 | Alibaba aluminium battery-box fabrication proxy |
| T9 | Aspirating smoke detector (battery + traction bay) | 6 | SOURCE | 10 800 | Alibaba aspirating smoke-detector anchor; rail detector certificate required |
| T10 | Fire suppression (aerosol, auto-discharge) | 6 | SOURCE | 3 000 | Alibaba aerosol fire-suppression anchor; EN 45545/rolling-stock approval required |
| T11 | HV contactor + bus bar set | 3 | SOURCE | 3 000 | Alibaba/AliExpress 1 000 V DC contactor anchor plus copper busbar |
| T12 | Station charging side-pin connector | 3 | SOURCE | 4 500 | Alibaba 30 kW DC module/EV connector proxy; pantograph-down alternate per site |
| T13 | Aux inverter (400 V / 110 V / 24 V) | 3 | SOURCE | 6 000 | Alibaba EV auxiliary converter / PCS anchor |
| T14 | COTS packaged roof HVAC unit (20 kW each, per car) | 3 | BID | 12 000 | Alibaba electric bus roof-HVAC anchor; rail certification still required |
| T15 | Regen dump resistor (roof-mount) | 1 | SOURCE | 1 000 | Alibaba braking-resistor proxy |
| T16 | Battery module service disconnect, fuses, and contactors | 24 module positions | SOURCE | 2 400 | Alibaba/AliExpress HV contactor/fuse anchor; 8 modules per car per traction.md |
| T17 | Battery vent duct + fire exhaust path | 3 cars | MAKE | 3 000 | Alibaba sheet-metal duct proxy; side vent, intumescent edge seals |
| T18 | HV cable, bonding strap, and EMC filter set | 3 cars | MAKE | 12 000 | Alibaba HV cable/harness proxy; 1 500 V DC pack, inverter, charger, and roof PV paths |
| T19 | Station-charge connector actuator + contact monitor | 3 | BID | 3 000 | Commodity actuator/sensor anchor; completes side-pin connector line T12 |
| T20 | Coolant pump, hose, manifold, and bleed kit | 3 cars | SOURCE | 2 500 | Alibaba EV coolant-pump/hose anchor; battery, inverter, motor, HVAC tie-in |
| T21 | Commodity full-roof solar panel set | 3 cars | SOURCE | 6 000 | Alibaba 400 W rigid/flexible solar-panel anchors; sixteen modules per car |
| T22 | Roof solar mounts, MPPT combiner, isolation, and roof harness | 3 cars | SOURCE | 6 000 | Alibaba roof-mount/combiner/MPPT proxies; bond pads, raised rails, edge clamps, junction boxes, fire-isolation labels |
| T23 | Multi-input PV/station battery charge inverter | 3 | SOURCE | 12 000 | Alibaba 30 kW DC charge-module stack accepts roof PV MPPT and station dock DC; contactors/cooling/harness covered by T11/T18/T20 |
| **Traction + power subtotal** | | | | **205 700** | |

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
| Body + interior | 235 200 |
| Bogies | 114 600 |
| Traction + power | 205 700 |
| Electronics + safety | 34 340 |
| Safety/accessibility/maintainability | 3 000 |
| **Total direct-material consist** | **592 840** |

Generated cost band from the same line items:

| Case | Direct material | +35% labour / assembly | Planning total |
|---|---:|---:|---:|
| Low | 466 844 | 163 395 | 630 239 |
| Base | 592 840 | 207 494 | 800 334 |
| High | 907 244 | 317 535 | 1 224 779 |

**Marketplace listed-price per-consist floor (volume 100): 0.63-1.22 M
USD with assembly allowance, base 0.80 M USD.**

This table is an audit lower bound for raw procurement. City CAPEX uses
the delivered rolling-stock planning unit in
[`lib/templates/capex-costs.toml`](../../../lib/templates/capex-costs.toml):
**4.2 M USD per `light-metro-3car` trainset**. That unit adds production
labour, shop overhead, fixture/tool amortisation, rail QA and
homologation evidence, freight, duty, insurance, warranty, initial
spares/tools, manuals, training, commissioning, and acceptance testing.

For comparison, legacy-vendor light-metro trainsets in the target
regions typically land 4-6 M USD each. The marketplace floor shows how
cheap the commodity hardware can be, but it is not a certified rail
quote; supplier qualification, freight, homologation, warranty, and
acceptance testing will lift any production purchase above this floor.

## Per-deployment customisation

The operator's own procurement office fills in:

- Livery paint scheme (B20).
- Seat fabric colour (B14).
- TRG-1 5G carrier SIM spec (per-country mobile network).
- Public-safety radio band (E-: not in base BOM).
- Pantograph dock voltage if a non-1500 V DC dock is used (out
  of scope upstream).

## v2 deliverables (not in v1)

- Supplier shortlist per BID line with qualification criteria.
- Lead-time analysis per SOURCE / MAKE / BID.
- Risk log: single-source parts + mitigation.
- Weight budget with per-line tare contribution + final target
  vs actual.
