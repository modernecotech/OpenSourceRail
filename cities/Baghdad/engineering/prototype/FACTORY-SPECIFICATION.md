# Baghdad Airport factory specification

The opening requires 36 cars, 72 powered bogies and 2,400 ten-metre beams. Use the tables to reserve shop capacity, quote locally made fixtures and contract specialist processes. Each count is a planning provision for the stated calendar. A contract service or a repair road is listed in its own unit.

Download the [equipment and tooling price return](factory-equipment.csv) or the [production routes and sizing assumptions](factory-routes.json). Both identify the opening and the factory evaluation. Each machine line belongs inside its named procurement lot. Price owned equipment, hire, contracted throughput and ongoing maintenance on their respective terms before replacing any part of the existing allowance.

## How quantities are calculated

For each machine, sum the hours it occupies across all products during a working day. Use the higher of the programme average and any declared peak. Spread one-off setup hours across the production window. Divide by usable hours per machine per day, round up, then apply the minimum required for simultaneous work or dedicated provision. A blank product quantity keeps the final machine count open. Hours of mould occupancy continue while a crew is off shift.

These are capacity screens for the identified operations. The supplier must return a feasible loading sequence, material handling and crew cover through changeovers, inspection, rework and outages. Parallel workloads on a shared crane, test bench or yard are booked once. Return power, air, extraction, floor and access requirements with the installed arrangement.

## Vehicle works

The planning window has 250 effective workdays. The standard resource day has 8 hours at 80.0% availability within the shift. Equipment with a different occupation window has its own daily hours below.

| Machine, tooling or service | Planning count | Known occupied h/day | Usable h/unit/day | Provision and price scope |
|---|---:|---:|---:|---|
| Receiving and long-stock racks | 1 (cell) | 0.92 | 6.40 | buy · `tooling` |
| Guarded section and liner saw | 1 (station) | 2.04 | 6.40 | buy · `tooling` |
| Bench preparation and liner drilling | 1 (station) | 0.81 | 6.40 | buy · `tooling` |
| Nested plate blank supply | 1 (supplier lane) | 0.56 | 6.40 | contract · `fleet` |
| Indexed 17 m body build bed | 2 (jig) | 8.83 | 6.40 | make · `tooling` |
| Removable bogie frame weld bed | 1 (jig) | 4.14 | 6.40 | make · `tooling` |
| Mobile pulsed MIG/MAG and source capture | 3 (set) | 8.23 | 6.40 | buy · `tooling` |
| Shared runway handling and rigging | 1 (set) | 1.55 | 6.40 | existing-or-hire · `tooling` |
| Shared portable tracker and dimensional QA | 1 (set) | 2.19 | 6.40 | hire · `tooling` |
| Weld inspection and NDT | 1 (team) | 1.98 | 6.40 | contract · `fleet` |
| Contract bogie seat and datum machining | 1 (supplier lane) | 1.85 | 6.40 | contract · `fleet` |
| Contract blast and coating | 1 (supplier lane) | 3.26 | 6.40 | contract · `fleet` |
| Bogie integration with clean stands | 1 (bay) | 5.05 | 6.40 | buy · `tooling` |
| Wheelset and supplier bearing assembly | 1 (supplier lane) | 1.20 | 6.40 | contract · `fleet` |
| Restrained bogie functional stand | 1 (station) | 1.57 | 6.40 | make · `tooling` |
| Portal and liner fixture with door support trolley | 1 (set) | 2.38 | 6.40 | make · `tooling` |
| Body mechanical and cabin fit | 1 (bay) | 5.35 | 6.40 | buy · `tooling` |
| Electrical cabinet and harness build benches | 1 (station) | 2.97 | 6.40 | make · `tooling` |
| Shared cabinet and harness tester | 1 (station) | 0.92 | 6.40 | buy · `tooling` |
| Onboard collector set install tools | 1 (set) | 0.24 | 6.40 | make · `tooling` |
| Body lift and marriage road | 1 (road) | 1.26 | 6.40 | buy · `tooling` |
| Static integration and factory acceptance test road | 1 (road) | 1.25 | 6.40 | buy · `tooling` |
| Set-level integration and controls test road | 1 (road) | 0.34 | 6.40 | existing-or-hire · `fleet` |
| Off-line exchange and repair road | 1 (road) | 0.21 | 6.40 | buy · `depot-control` |

| Manufactured or integrated item | Opening quantities by source item | Routing and inspection |
|---|---|---|
| Gross RHS and liner blanks | RHS and liner blanks × 3168 | Receive, saw, trim, deburr and mark. First-off heat, setup, length, square/angle and traceability. |
| Plate gussets and seat blanks | nested plate pieces × 2016 | Nest, cut, mark, deburr and dimensional check. Heat, dimensions and released edge/finish allowance. |
| Braced steel body | Braced steel body × 36 | Preset side fields, join under dimensional control, inspect and coat. Body release with joint and datum records after unclamping. |
| Powered bogie | Removable powered bogie × 72 | Join, inspect, machine, coat and integrate axle, suspension, drive and brake. Seat and axle survey, mounting records and restrained functional check. |
| Wheelsets and bearing seats | Wheelset × 144, Axlebox bearing positions × 288 | Buy traceable wheelsets and approved mounted bearings. Seat position is distinct from the supplier bearing component count. |
| Door opening assemblies | Door opening and controller × 288 | Fit liners, slide/stop/retention hardware and complete door; set and verify. Eight loaded/worn apertures and full leaves sweep per car; proof of return/anti-drop. |
| Door liner hardware | flush liner screws × 3456, liner threaded receivers × 3456 | Prepare and fit approved flush fasteners. Six paired positions per liner, stock fastener strength and access subject to joint design. |
| Roof HVAC modules | Roof HVAC module × 72 | Receive, stage, lift, fasten, connect and test. Fitted mass and mount, removal sweep, cool/condensate, bond and leak tests. |
| Onboard electrical cabinet and harness kits | Braced steel body × 36 | Prepare cabinet/boards by car role, cut/build harness, bench-test and install. Kit proxy per car, individual cabinet and harness count open. Validate crimp, continuity, isolation and installed flex. |
| Onboard collector sets | onboard_contact_sets × 24 | Fit suspended collector sets by role, connect and align. Check actual travel, contact forces and protective clearances. |
| Drive, brake and spring interfaces | Axle drive module × 144, Brake controller × 72, Primary spring interface × 288, Secondary spring interface × 144 | Clean assembly and torque, protect fluid/electrical runs and verify restraint. Preserve individual quantities by family; independent brake and parking friction scope open. |
| Equipped cars | Braced steel body × 36 | Marriage, weigh, static test and stage six sets. Serialised retention, flexible services, electrical and release/test records. |

## Civil yard and erection front

The planning window has 425 effective workdays. The standard resource day has 8 hours at 87.5% availability within the shift. Equipment with a different occupation window has its own daily hours below.

| Machine, tooling or service | Planning count | Known occupied h/day | Usable h/unit/day | Provision and price scope |
|---|---:|---:|---:|---|
| Wet-cast box mould and prestress position | 8 (position) | 192.00 | 24.00 | make / buy · `tooling` |
| Beam reinforcement cage build and check jig | 5 (place) | 32.00 | 7.00 | make · `tooling` |
| Calibrated stressing and controlled detensioning plant | 1 (set) | 6.00 | 7.00 | buy / hire · `tooling` |
| Shared batching and concrete delivery to placement crews | ≥1, final open (service) | 5.36 | 7.00 | contract · `elevated-civil` |
| Beam placement, vibration and finishing crews | 3 (crew) | 16.00 | 7.00 | contract · `elevated-civil` |
| Beam yard lifting and trailer loadout | 1 (hook service) | 6.00 | 7.00 | buy / hire · `elevated-civil` |
| Single-tier beam storage and dispatch buffer | 176 (position) | — | 7.00 | make / lease · `yard-access` |
| Beam tractor, matched trailer and haul crew | 4 (set) | 32.00 | 8.00 | contract · `elevated-civil` |
| Foundation, column and cap work areas | Open (site work area) | — | 7.00 | contract · `elevated-civil` |
| Bearing seat survey and installation crews | 1 (crew) | 6.40 | 7.00 | contract · `elevated-civil` |
| Site erection front and at-radius crane service | 1 (front) | 6.00 | 6.00 | hire / contract · `elevated-civil` |
| Flat station panel casting table | ≥4, final open (table) | Open | 24.00 | make / buy · `stations` |
| Panel strip, yard and dispatch handling | ≥1, final open (hook service) | Open | 7.00 | hire / contract · `stations` |

| Manufactured or integrated item | Opening quantities by source item | Routing and inspection |
|---|---|---|
| Track beam | beam_count × 2400 | Cut/bend and cage, set core and ends, pretension, inspect, cast, protect/cure, verify strength, detension and strip, inspect, store, release to trailer. Hold for pre-pour cage and insert survey, batch and cure records, calibrated strand force/elongation, approved concrete strength at transfer and lifting, and measured camber and mass. |
| Beam delivery and erection | lift_count × 2400 | Dispatch by seat readiness, haul, clear possession, rig, place, provisionally restrain, release, survey. Actual crane chart and safe radius, verified rig, ground/temporary stability, bearing contact and geometry, as-installed rail and traction interface tolerances. |
| Pier and foundation positions | pier_foundation_count × 2402 | Survey and investigate, stage utilities and access, excavate, build footing and superstructure support, verify cure, survey seats and release contiguous site bays. Ground, strength, temporary stability, geometry, offset, settlement and independent site acceptance. |
| Bearing provision | bearing_unit_allowance × 9600 | Approve seat, bearing, guide, jack and restraint scheme, procure, identify position, survey and fit, grout where specified, confirm release. Confirm seat plane, anchors, restraint, rated reaction and movement, and future replacement clearances. |
| Station deck panel | station bay panels after plant and access openings open | Issue station panel family, set shutters and cage, cast and finish, cure, verify lifting strength, remove, stage, dispatch and fit to station datums. Check panel width and length, finish and fall, joints, edge geometry, openings and accessible boarding gap and step on the surveyed installation. |

## Wayside electrical integrator

The planning window has 250 effective workdays. The standard resource day has 8 hours at 80.0% availability within the shift. Equipment with a different occupation window has its own daily hours below.

| Machine, tooling or service | Planning count | Known occupied h/day | Usable h/unit/day | Provision and price scope |
|---|---:|---:|---:|---|
| Adjustable enclosure and removable backplate assembly stand | 1 (bench) | 2.56 | 6.40 | make or adapt at integrator · `signalling` |
| Wire preparation, labelled kitting and crimp inspection station | 1 (station) | 1.95 | 6.40 | adapt existing equipment or contract · `signalling` |
| Isolated low-voltage I/O proving bench with removable test harness | 1 (bench) | 2.78 | 6.40 | build jig and buy calibrated instruments · `signalling` |
| Supplier switchgear and rectifier test provision | Open (contract service) | Open | 6.40 | contract to capable power-equipment manufacturer · `traction-sites` |

| Manufactured or integrated item | Opening quantities by source item | Routing and inspection |
|---|---|---|
| Wired and labelled wayside control assemblies | grid_protection_gateways × 30, section_control_gateways × 116, station_dispatch_controllers × 6 | Issue revision and terminal list, prepare removable panel, kit and label conductors, fit modules, terminate, inspect, bench-test and preserve serial record. List quantities by allocated position, then return actual panel/terminal drawings, as-wired continuity, isolation, addressing and controlled configuration for each serial. |
| Installed and tested rectifier cabinets | installed and tested rectifier cabinets open | Match the selected radial circuit, approve the supplier drawings, witness the production tests and pass the evidence to the installing contractor. Check serials, declared fault duty, interlocks, protection study and inspection record against the issued site and circuit. |

## Locally manufacturable tooling components

Include these repeatable components inside the parent fixture quote. Counts scale with the planned number of jigs or mould positions. Working-face tolerances, welds, fasteners, lift points, anchorages and materials require the tool designer’s drawing and inspection plan.

| Tooling component | Parent resource | Per unit | Opening tool quantity | Manufacture and inspection |
|---|---|---:|---:|---|
| Primary datum wear pad | vehicle-body-bed | 3 | 6 | Machine three replaceable pads for the fixture reference plane. Mark the jig and position, survey installed faces and retain the calibration record. |
| Centreline survey monument | vehicle-body-bed | 2 | 4 | Machine and attach target nests outside the joining heat zone. Record the two target locations and the transform to the car frame. |
| Adjustable longitudinal reference stop | vehicle-body-bed | 1 | 2 | Fabricate the bolted stop base, machine the replaceable contact face and inspect its position against the car datum. |
| Primary seat locator block | vehicle-bogie-bed | 4 | 4 | Machine replaceable blocks for the four primary positions at local x ±1,050 and y ±1,040 mm. Survey jig faces before and after the trial weld. |
| Secondary seat locator block | vehicle-bogie-bed | 2 | 2 | Machine and identify a left and right locator at local x 0 and y ±850 mm. Inspect the face height and protect the approved reference surfaces during transport. |
| Removable end bulkhead assembly | civil-beam-position | 2 | 16 | Fabricate the two end assemblies around the coordinated insert and strand pattern. Trial form fit, strand clearance, core extraction and removal sequence on the approved casting arrangement. Prestress anchorage is designed separately. |
| Box core former set | civil-beam-position | 1 | 8 | Make one removable or collapsible core set per active mould position. Demonstrate extraction, restraint and mold survey before repeating the tool. The sections per set await the chosen core mechanism. |
| Replaceable I/O breakout carrier | wayside-test | 1 | 1 | Issue the approved low-voltage terminal list, produce a labelled removable backplate, fit the keyed test harness and check every route against the independent point list. Connector type and the number of mating adapter variants stay open. |

## Workshop trials and buying terms

Trial a quick-change body fixture and replaceable datum stops on a representative frame. Record setup time from the last accepted part to the next accepted part, first-pass yield and the reinspection time after changing the fixture. Compare the repeat run with a local subcontracted process using the same part and acceptance basis. [Vehicle workcells](vehicle-factory/VEHICLE-WORKCELLS.md) · [NIST shop improvement methods](https://www.nist.gov/mep/lean-and-process-improvement)

The Airport monthly schedule reaches 163 beams in storage before erection. Reserve stack and crane access by issue and release date. Compare a reusable mould and exchangeable end forms with an existing precaster's bed. Trial laser or tracker survey against surveyed targets and physical gauges at the actual inserts and bearing seats. Hidden reinforcement needs separate pre-pour inspection. A factory study on arch segments and panels provides a method to test locally. [Civil workcells](infrastructure/CIVIL-WORKCELLS.md) · [Published scan-to-IFC study](https://www.mdpi.com/2075-5309/16/12/2383)

For wayside wiring, issue the connector list and revision before cutting a batch. Trial a labelled wire kit on a movable backplate fixture. Compare local manual cut, strip and crimp with outsourced digitally prepared terminals by first-pass continuity, rework, setup and ownership of the wire list. The proposed electrical shop counts 30 grid-protection gateways, 116 section gateways and 6 station dispatch controllers as work drivers. The number of rectifier cabinets and actual terminations is still open. The vehicle harness bench is in a separate assumed shop. If one bidder co-locates the two, combine their load profiles and report the released equipment. [Electrical enquiry](infrastructure/ELECTRICAL-CONTROLS.md) · [Modular wiring workstation example](https://www.rittal.com/com-en/products/PG20231215RAS101/PG20240408RAS202/PG20240408RAS203/PRO114365?variantId=4051130)

Attach the completed equipment return to the matching ERPNext RFQ and submit the lot price through the buyer portal. The register covers first production, shared capacity and outsourced work. The existing $44.80m tooling allowance also covers route and recovery equipment. A machine subtotal cannot replace that whole allowance until the buyer matches the exclusions and gives credit for equipment included in a supplier's unit price. [Buyer procedure](PROCUREMENT-PLAN.md)

Factory evaluation `be5bfe8fa5ff42de8792c720fafedd736a0cfee618ced81ba95dbd18944d891c`. Rebuild with `python3 -m cities.Baghdad.engineering.prototype.factory --check`.
