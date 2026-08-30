# Marketplace Price Proxies (cost studies only)

> **Do not use this page to select build parts.** The controlled
> [supplier-anchor register](../../../design/component-catalogue/catalog/buildable-trainset/supplier-anchors.md)
> assigns a real manufacturer family, known fit gaps and local-equivalent route
> to every bought-in LM3 product. This older ledger remains only to reproduce
> the low-cost sensitivity in the BOM; marketplace listings are not engineering
> or procurement approval.

Checked 2026-06-04 against public Alibaba marketplace pages and
AliExpress item history through PriceArchive where direct AliExpress
search pages are unstable. These are listed-price anchors, not certified
rail procurement quotes. They exclude freight, duty, supplier audits,
rail fire/smoke/toxicity reports, EN/TSI evidence packs, warranty terms,
and acceptance testing unless the BOM line says otherwise.

The updated BOM therefore represents a marketplace-only procurement
floor for a three-car standard-gauge consist. BID lines still need
supplier RFQs before a build can be treated as qualified rolling stock.

## RFC 0021 procurement baseline

The T-series rows below preserve the marketplace evidence ledger, but RFC
RFC 0021 defines the procurement baseline. Current RFQs shall target:

- three 225 kWh gross liquid-cooled LFP car packs: $65k–80k per train;
- six heavy-vehicle-class PMSM/controller sets: $48k–72k per train;
- HV distribution/contactors/insulation monitoring: $8k–12k per train;
- isolated LV DC/DC equipment: $5k–10k per train; and
- roof MPPT/DC electronics: $2k–4k per train.

These are target bands, not observed quotations. Candidate reference evidence
includes [EVE's railway LFP application](https://www.evebattery.com/en/news-1532),
[Inovance HM47/LD32 product data](https://en.inovance-automotive.com/solve/index103.html),
[Longertek direct-DC rail HVAC](https://en.longertek.com/technological-innovation.html),
and the [SINEXCEL PDS1-750K-H datasheet](https://en.sinexcel.com/uploads/soft/20260208/PDS1-750K-H%20Datasheet%2020250905.pdf).
None of those pages demonstrates compliance with the complete OSR railway
duty; the RFQ must price qualification, software/interface support, spares,
warranty, freight, and acceptance testing separately.

## Anchor Index

| Line(s) | Marketplace anchor | Listed price observed | BOM base used | Qualification note |
|---|---|---:|---:|---|
| B1 | [Alibaba S235/S355 rectangular steel tube](https://www.alibaba.com/showroom/s235-s355-rectangular-steel-tube.html) | 380-720 USD/t | 3,000 | Includes 3.2 t steel, waste, local handling, and cut premium. |
| B2 | [Alibaba S355 steel plate](https://www.alibaba.com/showroom/s355-steel-plates.html) and [S355 price table](https://www.alibaba.com/showroom/s355-prices.html) | 435-790 USD/t | 2,000 | Includes 2.0 t plate plus material loss and freight allowance. |
| B3 | [Alibaba steel fabrication services](https://www.alibaba.com/showroom/sheet-metal-fabrication-service.html) | quoted per piece/order | 6,000 | Fixture consumables and cut/drill setup allowance; real quote needs DXF pack. |
| B4 | [Alibaba welding wire](https://www.alibaba.com/showroom/welding-wire-price.html) | 0.86-1.50 USD/kg | 2,000 | Consumables only; certified welding labour remains outside direct material. |
| B5 | [Alibaba zinc-rich coating](https://www.alibaba.com/showroom/zinc-rich-primer.html) | 2.11-4.21 USD/kg | 4,000 | Primer, blast media, cavity wax, masking, and waste allowance. |
| B6, B7, B21 | [Alibaba fire-rated composite panel](https://www.alibaba.com/showroom/fire-rated-composite-panel.html) | 2-50 USD/sq m | 9,000; 4,000; 5,000 | Commodity panels priced low; EN 45545 certificate must be supplied or tested. |
| B8 | [Alibaba FRP/composite panel proxy](https://www.alibaba.com/showroom/frp-composite-panel.html) | 5-40 USD/sq m | 4,000 | Multi-part fiberglass end-cowl cast kit only; glazing and sensor hardware are separate lines. |
| B9 | [Alibaba train gangway suppliers](https://www.alibaba.com/supplier/train-gangway.html) | 3,500-15,999 USD/set | 30,000 | Covers two articulation/gangway sets at listed rail-part levels. |
| B10, B27 | [Alibaba train tempered laminated glass](https://www.alibaba.com/showroom/train-tempered-laminated-glass-window.html) | 5-90 USD/sq m; rail curved glass 38.50-41.50 USD/sq m | 6,000; 10,000 | Side window cassettes are commodity anchored; heated curved end panes need RFQ. |
| B11 | [Alibaba automatic sliding door systems](https://www.alibaba.com/showroom/automatic-sliding-door-systems.html) | 145-200 USD/operator; 890-2,988 USD/hermetic door proxy | 90,000 | Marketplace door hardware is a proxy; passenger door certification is still BID. |
| B12 | [Alibaba floor sandwich / composite board proxy](https://www.alibaba.com/showroom/honeycomb-sandwich-panel.html) | 5-50 USD/sq m | 6,000 | Structural floor board, hatches, inserts, and fire rating require supplier pack. |
| B13, B28 | [Alibaba bus vinyl flooring](https://www.alibaba.com/showroom/bus-vinyl-flooring.html) and vehicle decal/vinyl proxies | 5-45 USD/sq m | 1,500; 2,000 | Flooring and exterior livery film are commodity-priced. |
| B14 | [Alibaba bus seats](https://www.alibaba.com/showroom/bus-seat-plastic.html) | 15-160 USD/seat | 6,000 | Seat shell/listed transit seating anchor; rail upholstery/fire evidence needed. |
| B15 | [Alibaba bus handrail fittings](https://www.alibaba.com/showroom/bus-handrail-fittings.html) | 1.15-10.40 USD/fitting | 2,500 | Stainless tube, joints, brackets, and installation hardware. |
| B16, A3 | [Alibaba 12/24 V bus interior lamps](https://www.alibaba.com/showroom/bus-24v-interior-lamp.html) | 3-15 USD/lamp | 1,500; 1,000 | Emergency lighting battery packs are included in A3 allowance. |
| B17 | [Alibaba bus lighting and marker lamps](https://www.alibaba.com/showroom/bus-light.html) | 1-150 USD/lamp | 1,200 | Exterior head/tail/marker kit with sealed lamp allowance. |
| B18, E14 | [Alibaba bus LED sign/display](https://www.alibaba.com/showroom/led-bus-sign.html) and [destination sign suppliers](https://www.alibaba.com/supplier/led-destination-sign-for-bus.html) | 55-350 USD/display | 3,000; 3,000 | Includes interior/exterior display mix and controller allowance. |
| B19, E15 | [Alibaba bus CCTV systems](https://www.alibaba.com/showroom/bus-cctv-systems.html) and [AliExpress PoE camera history](https://www.pricearchive.org/aliexpress.com/item/1005009073001872) | 37-580 USD/kit; cameras from a few USD | 2,500; 600 | CCTV/intercom kit uses commodity camera anchor; safety outputs remain separate. |
| B20 | [Alibaba automotive urethane coating proxy](https://www.alibaba.com/showroom/2k-urethane-paint.html) | 2-15 USD/kg | 3,000 | Paint material only; booth labour and rework outside direct material. |
| B22 | [Alibaba railway coupler proxy](https://www.alibaba.com/showroom/railway-coupler.html) | RFQ/listed parts around low thousands | 8,000 | Rescue-capable coupler still requires rail supplier RFQ before build. |
| B23 | [Alibaba railway draft gear proxy](https://www.alibaba.com/showroom/railway-draft-gear.html) | RFQ/listed parts around low thousands | 4,000 | EN 15227 crush-can qualification remains a tender item. |
| B24, T18, E17, E20 | [Alibaba wiring harness services](https://www.alibaba.com/showroom/wiring-harness-custom.html) and HV cable proxies | quoted per loom/order | 4,000; 12,000; 9,000; 3,000 | Harness direct material anchor only; drawings and tests must be quoted. |
| B25, T19 | [Alibaba linear actuator proxy](https://www.alibaba.com/showroom/linear-actuator.html) | 20-300 USD/actuator | 6,000; 3,000 | Door and charging actuators need safety interlock validation. |
| B26, B29 | [Alibaba machined steel fabrication proxy](https://www.alibaba.com/showroom/custom-machined-steel-parts.html) | quoted per part/order | 3,000; 6,000 | Jacking/lifting fittings and articulation adapter frames need final drawings. |
| G1, G2, G13, G17, G18, G20 | [Alibaba train railway bogie parts](https://www.alibaba.com/showroom/train-railway-bogie-parts.html) | 900-15,000 USD/frame/part | 10,000; 12,000; 3,000; 3,000; 4,000; 3,000 | Fabricated bogie items are anchored to marketplace rail-part fabrication. |
| G3 | [Alibaba railway wheel price](https://www.alibaba.com/showroom/railway-wheel-price.html) and [locomotive wheelset](https://www.alibaba.com/showroom/locomotives-wheelset.html) | 500-2,000 USD/wheelset | 18,000 | Twelve wheelsets at listed wheelset range with inspection allowance. |
| G4 | [Alibaba railway bearing proxy](https://www.alibaba.com/showroom/railway-vehicle-axle-bearing-price.html) | 40-150 USD/bearing; higher for certified units | 12,000 | Uses marketplace bearing housings plus certified bearing uplift. |
| G5, G10, G12 | [Alibaba rail spring/bushing proxies](https://www.alibaba.com/showroom/railway-air-spring.html) | 20-125 USD/spring or link proxy | 4,800; 2,400; 1,800 | Elastomer and spring compounds require certificate traceability. |
| G6 | [Alibaba railway air spring](https://www.alibaba.com/showroom/railway-air-spring.html) | 300-1,500 USD/unit | 6,000 | Twelve air springs at low listed rail range. |
| G7 | [Alibaba railway hydraulic damper proxy](https://www.alibaba.com/showroom/railway-hydraulic-damper.html) | 50-300 USD/unit proxy | 3,000 | Damping curve and temperature envelope need supplier confirmation. |
| G8, G16 | [Alibaba railway brake pads](https://www.alibaba.com/showroom/brake-pads-railway.html) and rail brake-disc proxies | pads 13-100 USD; discs via RFQ/proxy | 12,000; 1,500 | Braking friction material must be qualified with the selected caliper. |
| G9 | [Alibaba brake caliper proxy](https://www.alibaba.com/showroom/railway-brake-caliper.html) | industrial calipers 40-215 USD; rail RFQ higher | 12,000 | Rail electromagnetic caliper remains BID despite commodity proxy. |
| G11 | [Alibaba heavy bearing / PTFE slider proxy](https://www.alibaba.com/showroom/ptfe-slide-bearing.html) | 50-500 USD/unit proxy | 3,000 | Centre-pin ring and slider stack need load rating. |
| G14, G15 | [AliExpress/Alibaba encoder and temperature sensor proxies](https://www.pricearchive.org/search/aliexpress.com/encoder-sensor/1) | single to tens of USD | 600; 500 | Rail harnessing and environmental protection covered elsewhere. |
| G19 | [Alibaba flexible gear coupling proxy](https://www.alibaba.com/showroom/flexible-gear-coupling.html) | 100-800 USD/set | 2,000 | Torque rating needs confirmation against final motor/gearbox. |
| T1 | [Alibaba PMSM motor proxies](https://www.alibaba.com/showroom/pmsm-150kw-motor.html) | 3,200-11,150 USD/motor; supplier table 4,500-7,000 USD | 36,000 motor share | Six HM47-class 350 kW short-peak candidates; controller share is T3 and rail duty remains unqualified. |
| T2 | [Alibaba industrial gearbox proxy](https://www.alibaba.com/showroom/industrial-gearbox.html) | 500-4,000 USD/unit proxy | 10,000 | Rail duty cycle and noise target need gearbox RFQ. |
| T3 | [Alibaba EV inverter / PCS proxy](https://www.alibaba.com/showroom/300kw-solar-power-inverter.html) | 4,999-5,450 USD for PCS proxy | 24,000 | Six independent LD32-class controllers; generic PCS listings are lower-bound evidence only. |
| T4, T7, T20 | [Alibaba EV cooling and pump proxies](https://www.alibaba.com/showroom/ev-coolant-pump.html) | tens to hundreds USD per pump/plate | 6,000; 2,000; 2,500 | Cooling loops need thermal validation. |
| T5 | [Alibaba 200 kWh battery packs](https://www.alibaba.com/showroom/200-kwh-battery-pack.html) | marketplace BESS and EV-pack listings vary widely by certification scope | 75,000 | Three 225 kWh gross / 180 kWh usable LFP car packs; liquid cooling, segmentation, IEC 62928 test evidence and propagation controls require RFQ. |
| T6 | [Alibaba BMS proxy](https://www.alibaba.com/showroom/ev-bms.html) | hundreds to low thousands USD/system | 4,500 | Pack-level BMS electronics only. |
| T8, T17 | [Alibaba aluminium enclosure / duct fabrication proxies](https://www.alibaba.com/showroom/aluminum-battery-box.html) | quoted per part/order | 6,000; 3,000 | Under-seat enclosure and vent ducts need final sheet-metal drawings. |
| T9 | [Alibaba aspirating smoke detector](https://www.alibaba.com/showroom/aspirating-smoke-detector.html) | 1,095-1,850 USD/unit proxy | 10,800 | Six detector channels at commodity detector pricing. |
| T10 | [Alibaba water-mist component proxy](https://www.alibaba.com/showroom/water-mist-fire-suppression-system.html) | component listings vary by pump/nozzle scope | 9,000 | Three localized battery-only systems with reservoir, DC pump, stainless pipe, nozzles and feedback; propagation testing excluded. |
| T11, T16 | [Alibaba 1000 V DC contactors](https://www.alibaba.com/showroom/1000v-dc-contactor.html) and [AliExpress contactor history](https://www.pricearchive.org/aliexpress.com/item/1005004649240380) | 7-100 USD/contactors; larger vacuum units 290-621 USD | 10,000; 2,400 | Main 800 V-class HV distribution requires interrupt, weld, IMD, vibration and supplier evidence. |
| T12, T23 | [Alibaba 30 kW DC charge modules](https://www.alibaba.com/showroom/30kw-dc-module.html) | 480-510 USD/module; PCS 4,999-5,450 USD | 4,500; 3,000 | Train has a protected station-DC interface and roof MPPT; the 500 kW conversion stage is wayside. |
| T13 | [Alibaba auxiliary DC/DC proxy](https://www.alibaba.com/showroom/ev-dc-dc-converter.html) | 100-1,500 USD/unit proxy | 7,500 | Isolated 800 V to 110/48/24 V DC domains; no central AC inverter. |
| T14 | [Alibaba bus rooftop air conditioning](https://www.alibaba.com/showroom/bus-rooftop-air-conditioning.html) | 2,237-6,500 USD/bus roof unit | 12,000 | Three roof HVAC units at bus commodity pricing. |
| T15 | [Alibaba braking resistor proxy](https://www.alibaba.com/showroom/braking-resistor.html) | 50-1,000 USD/unit proxy | 1,000 | Regen dump resistor needs thermal enclosure design. |
| T21 | [Alibaba 400 W solar panels](https://www.alibaba.com/showroom/solar-panels-400w.html) and [flexible 400 W panels](https://www.alibaba.com/showroom/solar-panel-400w-12v.html) | rigid 41-79 USD/panel; flexible 50-139 USD/panel | 6,000 | Full-roof panel material for 36 mixed rigid/flexible modules. |
| T22 | [Alibaba solar mounting/combiner proxies](https://www.alibaba.com/showroom/solar-panel-mounting-rail.html) | low dollars per clamp/rail; combiner/MPPT low hundreds | 6,000 | Bond pads, raised rails, clamps, junction boxes, MPPT, and isolation. |
| E1, E2 | [Alibaba PCB assembly proxy](https://www.alibaba.com/showroom/pcb-assembly.html) | quoted per board/order | 1,200; 1,500 | Custom boards include assembly allowance; SIL evidence excluded. |
| E3 | [AliExpress IMU proxy](https://www.pricearchive.org/search/aliexpress.com/imu-module/1) | tens to hundreds USD/module | 200 | ADIS-grade part can exceed commodity proxy; base uses low-cost alternate. |
| E4 | [AliExpress GNSS module proxy](https://www.pricearchive.org/search/aliexpress.com/u-blox-gnss-module/1) | tens of USD/module | 100 | Uses commodity GNSS board anchor. |
| E5 | [AliExpress NFC reader proxy](https://www.pricearchive.org/search/aliexpress.com/pn5180-nfc/1) | single to tens of USD/module | 20 | Reader board only. |
| E6 | [AliExpress secure-element proxy](https://www.pricearchive.org/search/aliexpress.com/atecc608b/1) | single USD/module | 20 | Chip/module allowance only. |
| E7 | [AliExpress 5G M.2 modem proxy](https://www.pricearchive.org/search/aliexpress.com/5g-m.2-module/1) | tens to hundreds USD/module | 200 | Carrier approval and antenna certification excluded. |
| E8 | [PriceArchive SX1276 LoRa modules](https://www.pricearchive.org/search/aliexpress.com/915mhz-lora-sx1276/1) | 5.62-19.04 USD/module; 55.66 USD/10-pack | 20 | One radio plus spares. |
| E9 | [AliExpress NVMe proxy](https://www.pricearchive.org/search/aliexpress.com/256gb-nvme-ssd/1) | tens of USD | 40 | Operational recorder storage only; crash memory is E23. |
| E10 | [PriceArchive 10.1 inch touchscreens](https://www.pricearchive.org/search/aliexpress.com/touch-screen-10.1/1) | 100-255 USD/display class | 300 | Two maintenance screens. |
| E11, E12, E13 | [Alibaba industrial pendant / switch proxies](https://www.alibaba.com/showroom/industrial-control-pendant.html) | low to hundreds USD each | 500; 40; 100 | Depot-only manual controls, plungers, and guarded keyed switches. |
| E16 | [Alibaba safety relay proxy](https://www.alibaba.com/showroom/safety-relay.html) | tens of USD/module | 200 | Relay stage material only; safety case excluded. |
| E18 | [Alibaba industrial LIDAR proxy](https://www.alibaba.com/showroom/industrial-lidar-sensor.html) | 598-3,289 USD/sensor proxy | 8,000 | Two nose modules with LIDAR/cameras/radar allowance; rail T-OBS supplier RFQ needed. |
| E19 | [Alibaba washer/heater actuator proxies](https://www.alibaba.com/showroom/car-washer-pump.html) | tens to hundreds USD/system | 1,000 | Keeps glass sensor windows serviceable. |
| E21 | [Alibaba 5G/GNSS antenna proxy](https://www.alibaba.com/showroom/5g-gnss-antenna.html) | tens to hundreds USD/antenna | 300 | Roof antenna set material only. |
| E22 | [Alibaba DIN rail cabinet proxy](https://www.alibaba.com/showroom/electrical-control-cabinet.html) | hundreds to low thousands USD/cabinet | 3,000 | Three electronics cabinets and distribution hardware. |
| E23 | [Alibaba rugged SSD/event-recorder proxy](https://www.alibaba.com/showroom/rugged-ssd.html) | hundreds to low thousands USD | 2,000 | Crashworthy event recorder still requires qualification. |
| A1 | [Alibaba bus call button/accessibility proxy](https://www.alibaba.com/showroom/passenger-call-button.html) | single to tens USD/device | 1,000 | Wheelchair bay fixtures, buttons, trims, and guards. |
| A2 | [Alibaba safety label/signage proxy](https://www.alibaba.com/showroom/safety-warning-label.html) | cents to low dollars per label | 500 | Full train labels and tactile/visual signage. |
| A4 | [Alibaba fire extinguisher / first aid proxy](https://www.alibaba.com/showroom/fire-extinguisher-first-aid-kit.html) | tens of USD per kit | 500 | Operator consumables and seals. |

## Cost Interpretation

The BOM numbers were reduced where the marketplace anchor directly
covered the quantity. Safety-critical, custom, and certified rail parts
remain marked BID or MAKE where the listed price is only a proxy. The
direct-material base is therefore useful for open-source design trade
studies and commodity purchasing discussions, but it should not be used
as a production-ready certified trainset quote.
