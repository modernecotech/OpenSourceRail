# Baghdad Airport workshop cost estimate

Use this estimate to compare workshop equipment and services for the selected opening. The [factory specification](FACTORY-SPECIFICATION.md) gives the capacity, tooling and manufacturing routes. The editable [unit rates](shop-rates.toml) and [machine-readable estimate](shop-costs.json) identify each resource and its procurement lot.

| Period and scope | Low USD | Base USD | High USD |
|---|---:|---:|---:|
| Equipment purchase | 1,197,500 | 2,827,200 | 5,926,600 |
| Opening services | 2,860,308.8 | 6,972,900 | 16,342,230.4 |
| Annual equipment upkeep | 23,950 | 113,088 | 414,862 |

The first line buys dedicated or retained equipment once. The second pays for the opening production run, including subcontract work and hire. The third reserves 2%, 4% or 7% of retained equipment cost per year for maintenance and calibration while that equipment stays in use. Keep the annual reserve separate from purchase and from service rates that already cover the contractor’s equipment.

These sums cover the quantities shown below. A minimum provision for a table or a known part of a contract gives a quantity lower bound. The low, base and high rates are estimating scenarios. Even the high subtotal leaves some scope unpriced. Freight to Iraq, customs and tax, major works, staffing outside service contracts, approval tests and contingency need separate returns. CAM and staff training have a separate scenario below. No complete installed price or committed purchase is available.

## Purchase and booking quantities

Hours include each production operation and its setup once. Grouped shifts round the total hours up at the usable hours per unit in the factory specification. Peak throughput determines parallel capacity. The supplier should return calendar days, minimum callouts, idle time and mobilisation for the actual booking sequence.

### Vehicle works

| Resource | Capacity provision | Quantity priced | Unit rate USD low / base / high | Base extended USD | Scope and choice |
|---|---:|---:|---:|---:|---|
| Receiving and long-stock racks | 1 cell | 1 cell | 8,000 / 18,000 / 40,000 | 18,000 | One long-stock cell with rated cantilever racks, axle cradles, tags and quarantine barriers. Building and forklift hire excluded. |
| Guarded section and liner saw | 1 station | 1 station | 20,000 / 34,000 / 56,000 | 34,000 | Hydraulic horizontal saw with at least 350 × 320 mm throat and supported long-stock lane. Lower rate assumes equivalent used or locally supplied equipment. |
| Bench preparation and liner drilling | 1 station | 1 station | 3,500 / 8,500 / 17,000 | 8,500 | Guarded geared drill, datum stops, replaceable bushes, bench grinder and extraction. Validate spindle runout on a liner. |
| Nested plate blank supply | 1 supplier lane | 140.96 occupied hour | 60 / 110 / 190 | 15,505.6 | Reserved CNC laser or plasma cutting and marking for 8–12 mm plate. Price includes supplier setup, machine and operator. Blank plate and freight belong to the parts lot. |
| Indexed 17 m body build bed | 2 jig | 2 jig | 40,000 / 100,000 / 210,000 | 200,000 | Local surveyed 18 × 3.2 m modular body bed with clamps and replaceable locators. Includes the listed fixture components and initial geometry check. Foundation design separate. |
| Removable bogie frame weld bed | 1 jig | 1 jig | 12,000 / 30,000 / 65,000 | 30,000 | Local 3.2 × 2.5 m axle-datum fixture and seat gauges. Includes its removable locators. |
| Mobile pulsed MIG/MAG and source capture | 3 set | 3 set | 8,000 / 14,000 / 26,000 | 42,000 | 400 A class pulse GMAW source, feeder, cooler, extraction and local commissioning per set. Major incoming supply and ongoing consumables excluded. |
| Shared runway handling and rigging | 1 set | 61 booked shift | 450 / 950 / 2,200 | 57,950 | Book an existing rated bridge crane plus rigging and operator in grouped shifts. Confirm heaviest lift, spreader weight, usable hook height and roof runway. |
| Shared portable tracker and dimensional QA | 1 set | 86 booked shift | 450 / 600 / 1,000 | 51,600 | Hire calibrated tracker and targets for grouped whole shifts. Local surveyor, travel and lost time between bookings extra. Lower rate assumes a multi-day agreement. |
| Weld inspection and NDT | 1 team | 495.6 occupied hour | 55 / 105 / 200 | 52,038 | Contract one field inspection team with calibrated equipment per allocated team-hour. Method, weld coverage, reporting and repeat visits require an approved inspection plan. |
| Contract bogie seat and datum machining | 1 supplier lane | 462 occupied hour | 100 / 190 / 320 | 87,780 | Supplier portal mill or horizontal borer with a surveyed bed that locates both axle planes. Machine, operator and setup only. |
| Contract blast and coating | 1 supplier lane | 816 occupied hour | 80 / 150 / 270 | 122,400 | Subcontract a booth accepting a 17 m body, with preparation, cure and coating team. Coating-system selection, extra blast repair and intershop transport require returns. |
| Bogie integration with clean stands | 1 bay | 1 bay | 10,000 / 25,000 / 55,000 | 25,000 | Axle cradle, positive restraints, rated handling fixtures and calibrated torque tooling per bay. |
| Wheelset and supplier bearing assembly | 1 supplier lane | 300 occupied hour | 65 / 130 / 230 | 39,000 | Press fitting and measurement service for mounted wheelsets. Credit inside purchased wheelset price when included by supplier. Excludes wheelsets and bearings. |
| Restrained bogie functional stand | 1 station | 1 station | 30,000 / 80,000 / 180,000 | 80,000 | Guarded functional rig with brake/drive adapters, leak test, recorder and isolation. Full thermal dynamometer and independent type testing excluded. |
| Portal and liner fixture with door support trolley | 1 set | 1 set | 2,500 / 7,000 / 16,000 | 7,000 | Opening gauge, liner templates, retention checks and handling trolley. Labour for fitting is in the vehicle routine. |
| Body mechanical and cabin fit | 1 bay | 1 bay | 10,000 / 28,000 / 65,000 | 28,000 | Mobile access platforms and torque/weather-sealing tool packages. Main lifting equipment booked in the crane line. |
| Electrical cabinet and harness build benches | 1 station | 1 station | 5,000 / 15,000 / 33,000 | 15,000 | Vehicle build station with crimp/die and pull testing, ESD and isolated supply. Production boards and cables are in the fleet lot. |
| Shared cabinet and harness tester | 1 station | 1 station | 6,500 / 20,000 / 50,000 | 20,000 | Expandable continuity system, independent insulation test and keyed adapters. Return pin count, protected paths, measurement ranges and calibration. |
| Onboard collector set install tools | 1 set | 1 set | 2,000 / 6,000 / 18,000 | 6,000 | Portable insulated setup fixture, spring/contact gauge and calibrated indicating tools for an installed collector. |
| Body lift and marriage road | 1 road | 1 road | 75,000 / 170,000 / 350,000 | 170,000 | One synchronized rail-vehicle lifting set with mechanical locks, cradles and logging. Number and rating of columns require installed mass, lift points and unbalanced load case. |
| Static integration and factory acceptance test road | 1 road | 1 road | 50,000 / 145,000 / 300,000 | 145,000 | Portable car wheel-load measuring system, brake and electrical instruments with isolated test area. Floor, track construction and route tests excluded. |
| Set-level integration and controls test road | 1 road | 14 booked shift | 700 / 1,800 / 4,000 | 25,200 | Grouped shifts booking an existing full-length protected and isolated six-car test road. Construction of a new road requires a separate site estimate. |
| Off-line exchange and repair road | 1 road | 1 road | 60,000 / 160,000 / 330,000 | 160,000 | Second lift and support set, exchange pallet, isolation and repair bench for the depot. Civil repair-road construction belongs to the depot lot. |

### Civil yard and erection front

| Resource | Capacity provision | Quantity priced | Unit rate USD low / base / high | Base extended USD | Scope and choice |
|---|---:|---:|---:|---:|---|
| Wet-cast box mould and prestress position | 8 position | 8 position | 80,000 / 175,000 / 350,000 | 1,400,000 | Per 10 m box mould including retractable core, end plates and allocated reaction-bed fabrication. Shared stressing jack separately priced. Ground improvement and building excluded. |
| Beam reinforcement cage build and check jig | 5 place | 5 place | 6,000 / 18,000 / 45,000 | 90,000 | One cage assembly position including gauges, jig and allocated share of a common cut-and-bend service setup. Reinforcement stock and production labour excluded. |
| Calibrated stressing and controlled detensioning plant | 1 set | 1 set | 30,000 / 75,000 / 180,000 | 75,000 | Buy a shared calibrated jack, pump, detensioning, grips and protection. Fixed reactions belong to the mould positions. Actual force and anchor design require specialist review. |
| Shared batching and concrete delivery to placement crews | ≥1 service | ≥1,608.48 occupied hour | 90 / 180 / 350 | 289,526.4 | Shared metered concrete delivery and placing equipment with operator, assumed 20 m³/h gross. Mix material and finishing crew excluded. Beam hours known, panel workload outstanding. |
| Beam placement, vibration and finishing crews | 3 crew | 4,800 occupied hour | 40 / 90 / 180 | 432,000 | Crew-hour for placement, vibration and finishing. Concrete and paid pump operator excluded. Provide shifted coverage during staggered releases. |
| Beam yard lifting and trailer loadout | 1 hook service | 258 booked shift | 700 / 1,500 / 3,200 | 387,000 | Operated precast-yard crane and rigging for stripping and loading. Verify cast gross load at working radius and actual ground capacity. |
| Single-tier beam storage and dispatch buffer | 176 position | 176 position | 250 / 700 / 1,600 | 123,200 | One set of reusable dunnage, lateral restraint, marking and layout per single-tier slot. Yard lease and permanent paving remain in the yard lot. |
| Beam tractor, matched trailer and haul crew | 4 set | 2,400 beam trip | 250 / 650 / 1,600 | 1,560,000 | One loaded beam per local low-loader trip with return leg, driver and routine restraint. Abnormal permits, exceptional haul distance and escorts require route-specific pricing. |
| Foundation, column and cap work areas | Open site work area | 2,402 support position | 150 / 450 / 1,200 | 1,080,900 | Survey setout, staging and record at each support position only. Excavation, piles, ground treatment, rig mobilisation and permanent piers require ground and design returns. |
| Bearing seat survey and installation crews | 1 crew | 9,600 bearing fitted | 25 / 70 / 180 | 672,000 | Installation team with calibrated survey and torque tools per bearing. Bearing supply, plate, anchor, grout materials and future replacement excluded. |
| Site erection front and at-radius crane service | 1 front | 300 booked shift | 3,000 / 7,000 / 16,000 | 2,100,000 | One site crane and crew in booked erection shifts at the assumed eight lifts/day. Include standard rigging. Obtain crane chart, access and ground works, mobilisation and traffic pricing separately. |
| Flat station panel casting table | ≥4 table | ≥4 table | 9,000 / 23,000 / 55,000 | 92,000 | One adaptable panel table with shutters and edge/insert gauges. Price four provisional positions pending the station-bay count and duty. |
| Panel strip, yard and dispatch handling | ≥1 hook service | Open booked shift | 550 / 1,200 / 2,800 | Open | Operated panel handling crane per shift with rig. Panel quantity and booked shifts open. If the same crane serves beam lifting, combine bookings and credit the overlap. |

### Wayside electrical integrator

| Resource | Capacity provision | Quantity priced | Unit rate USD low / base / high | Base extended USD | Scope and choice |
|---|---:|---:|---:|---:|---|
| Adjustable enclosure and removable backplate assembly stand | 1 bench | 1 bench | 3,000 / 9,500 / 22,000 | 9,500 | Backplate assembly stand with adjustable stops, template and controlled fastening equipment. Include integrator-owned equipment as supplier credit. |
| Wire preparation, labelled kitting and crimp inspection station | 1 station | 1 station | 5,000 / 14,000 / 35,000 | 14,000 | Bench cutter/stripper, matched crimp dies, ferrule labelling and pull tester for LV wire. High-power busbars and cable installation belong to power lots. |
| Isolated low-voltage I/O proving bench with removable test harness | 1 bench | 1 bench | 11,000 / 35,000 / 90,000 | 35,000 | Programmable isolated supply, protection and signalling interface simulator, breakout, recorder and controlled adapters. Excludes live HV fault tests. |
| Supplier switchgear and rectifier test provision | Open contract service | Open cabinet witnessed | 1,800 / 6,000 / 18,000 | Open | Factory routine acceptance service and witness per installed rectifier cabinet. Cabinet count, special type tests, HV laboratory and travel require supplier returns. |

## How to credit the existing procurement lots

The buyer compares the workshop lines below against matching scope inside the existing [lot estimates](sourcing-estimate.json). A supplier offering finished bogies, for example, may include machining and bearing fitting. Record who owns the tooling, how many operations the offer covers, its hire term, commercial exclusions and the credit accepted by the buyer. Keep unmatched scope in the original lot. An unreturned credit stays open. Adding these amounts to the opening budget would count the work twice.

| Parent lot | Existing base USD | Base work allocated here USD | Quantities still open or partial |
|---|---:|---:|---|
| tooling | 44,800,000 | 2,503,050 | — |
| fleet | 50,880,000 | 341,923.6 | — |
| depot-control | 75,000,000 | 160,000 | — |
| elevated-civil | 107,941,285.743 | 6,521,426.4 | civil-placement |
| yard-access | 874,172.185 | 123,200 | — |
| stations | 78,000,000 | 92,000 | civil-panel-table, civil-panel-hook |
| signalling | 14,400,000 | 58,500 | — |
| traction-sites | 348,472,470.858 | Open | wayside-power-test |

## What the outstanding panel and cabinet counts could cost

These one-time scenarios price additional services within the existing lots. The [station enquiry](infrastructure/STATION.md) describes an uninterrupted 125 m island. Use one such template per passenger station to test the budget. For the power supplier, test one or two witnessed cabinets per grid site. Actual panel schedules and cabinet lists remain open.

| Alternative scope | Additional bookings | Low USD | Base USD | High USD |
|---|---|---:|---:|---:|
| 6 nominal island templates, 600 panels | 82.82736 placement hours, 43 hook shifts | 31,104.46 | 66,508.92 | 149,389.58 |
| 30 cabinets at 1 per site | 30 cabinet tests | 54,000 | 180,000 | 540,000 |
| 60 cabinets at 2 per site | 60 cabinet tests | 108,000 | 360,000 | 1,080,000 |

Multiply the issued panel count by 0.1380456 placement hours. Multiply it by 2 moves of 0.25 h each, divide by 7 productive hours per shift and round up. Extend each quantity at the corresponding hourly or shift rate above. The four minimum tables and beam placement are already priced. This scenario excludes panel materials, finishing and installation. Credit shared crane time once.

Multiply the supplier’s issued cabinet count by the per-cabinet witness rate. Use one cabinet scenario at a time. Replace the provisional quantities and confirm the service scope and lot credit before budgeting. The 41-line register and its subtotals exclude these scenarios.

## CAD/CAM, first-off inspection and staff training

This separate scenario equips one programmer and one shop-floor reader, prepares one machine-specific post, and runs two supervised sessions for seven participants. The factory can reuse the [CAM handoff](cam/CAM.md) and the [instructor guide](training/INSTRUCTOR.md). A first-off booking allows two shop shifts and two inspections. The machine owner must confirm the actual part, fixture, machine travel, tooling, process and post before a trial.

| Period | Low USD | Base USD | High USD |
|---|---:|---:|---:|
| Initial setup | 3,790 | 7,510 | 14,320 |
| Annual support | 640 | 1,360 | 2,560 |
| First cohort and trials | 3,792 | 8,060 | 15,640 |
| Optional annual substitution | 680 | 680 | 680 |

The commercial licence is an optional annual substitution. Use the open-source seat in the reference case. Staff attendance and owner witnessing are resource costs even where payroll covers them. Record the included amount before changing a parent budget.

| Work | Quantity and base rate USD | Base extended USD | Check for an existing provision |
|---|---:|---:|---|
| One CAD/CAM workstation, dual screens, UPS and local backup for the manufacturing technician. | 1 workstation × 2,800 | 2,800 | Existing engineering PC or CAM supplier's workstation. |
| One rugged shop-floor reader for released drawings, work instructions and offline exercises. | 1 reader × 950 | 950 | Existing workstation or ERP terminal in the parent shop. |
| FreeCAD desktop licence on the technician's PC. Reader uses a browser and the offline material. | 1 seat-year × 0 | 0 | No commercial seat fee for the chosen open-source tool. |
| One systems technician for one eight-hour day to install pinned software, test imports and record restore steps. | 8 technician-hour × 55 | 440 | Buyer IT setup, including any installation bundled in the workstation quote. |
| One CAM specialist for three eight-hour days to configure one machine/controller post and document its constraints. | 24 specialist-hour × 110 | 2,640 | Contract cutter's own postprocessor and setup fee. |
| One reviewer for one eight-hour day for source geometry versus post output, offline backplot and independent review record. | 8 review-hour × 85 | 680 | Existing CAM validation or engineering-assurance labour. |
| Two supervised four-hour sessions for one cohort covering the seven workshop roles, followed by a skills handover. | 8 instructor-hour × 85 | 680 | Supplier training included with the machine or buyer induction. |
| Seven learners participate in both four-hour sessions. Attendance is owner time at a loaded hourly rate. | 56 learner-hour × 25 | 1,400 | Existing workforce payroll. Use as an opportunity cost when payroll is funded. |
| One owner quality representative for two eight-hour first-off visits, separate from the inspection supplier. | 16 owner-hour × 55 | 880 | Owner quality or first-article assurance. |
| Two supervised shop bookings for sample preparation and first-off cuts against four plate families plus a representative saw cut. Includes shop time and sample stock. | 2 trial shift × 850 | 1,700 | Cutting supplier's setup, coupons or first article in the fleet contract. |
| Two staffed first-off inspection visits for datum and dimensional checks with calibrated instruments and reports. Confirm instrument uncertainty against each feature. | 2 survey day × 1,700 | 3,400 | Credit the instrument hire and inspection labour where the series metrology booking already contains this work. |
| Two eight-hour days per year for backup restore, postprocessor change review and a reference backplot. | 16 support-hour × 85 | 1,360 | Included support, software assurance and workstation IT contracts. |
| Optional substitution of one standard commercial seat for the FreeCAD seat. Revalidate the post and confirm Iraqi licence terms before purchase. | 1 user-year × 680 | 680 | Alternative subscription. Exclude when budgeting the open-source scenario. |

The tooling lot also covers route and recovery equipment. The setout line covers survey and staging only. Ground treatment and foundation construction require a site return. Station panel and rectifier cabinet production require issued item counts. All resource IDs, including priced lines, retain the technical limits and open items in their factory specifications.

## Market observations

Prices and descriptions reviewed 2026-11-23. Supplier list prices below apply to their stated markets and configurations. Each workshop rate is an engineering allowance, including the rows that use a catalogue price as a benchmark. Obtain dated local quotations with currency, delivery, installation, warranty and validity.

- US catalogue USD 24,950 for the bare 20 × 26 inch class three-phase saw. The enquiry adds long-stock support, guarding and commissioning. Verify installed supply and frequency. [Grizzly G0887 hydraulic mitre bandsaw](https://www.grizzly.com/products/grizzly-20-x-26-5-hp-industrial-horizontal-mitering-metal-cutting-bandsaw/g0887)
- US catalogue USD 6,199 for the pulsed welder. The maker gives 60% duty at 400 A on its specified 240 V single-phase input. The workcell needs extraction and a verified local power interface. [Everlast Cyclone 503DPi](https://www.everlastgenerators.com/catalog-mig)
- US equipment-only USD 600/day, USD 2,500/week or USD 8,000/month for certified users. Staffed US survey USD 170/hour, ten-hour minimum. Travel, shipping and Baghdad availability require a return. [Metro Metrology equipment rental](https://metrometrology.com/services/)
- Technical example only. The low-voltage unit starts at 128 points and expands to 1,024. Provide independent insulation testing or an appropriately specified higher-voltage variant plus protected adapters. [Cirris 4200 tester](https://cirris.com/4200-2/)
- Technical example only. Mobile jack and release equipment use a separately designed bed reaction system. Quote against the strand, force, losses, tails, gauge and release plan. [PAUL single-strand stressing equipment](https://prestressed-concrete.paul.eu/fileadmin/Files/prestressed-concrete/B147.26_02-en.pdf)
- US 42 m boom pump USD 225/hour plus USD 4/cubic yard, four-hour minimum, permits and travel extra. A comparator for peak service. The proposed pooled yard-feed allowance assumes local fixed plant with shorter placement reach. [Whitehead Concrete Pumping 2026 rates](https://www.whiteheadconcretepumping.com/rates.html)
- US nominal 100 ton class USD 275/hour with an eight-hour minimum plus rigger, fuel and trailers. Capacity at the Airport lift radius is unresolved. The assumed shift rate includes a rigging crew. [C.O.I. Crane Service 2025–2026 rate sheet](https://coicraneservice.com/wp-content/uploads/2025/11/COI-Pricing-Worksheet-11042025.pdf)
- The project permits commercial use of FreeCAD without a licence fee. Workstation setup, postprocessor adaptation, verification and local support still require staff. [FreeCAD project licensing FAQ](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Frequently_asked_questions.md)
- US published standard subscription USD 680 per user/year. This optional comparison uses one standard seat. Regional eligibility, post support, future renewals and advanced manufacturing subscriptions require a supplier return. [Autodesk Fusion subscription types](https://www.autodesk.com/products/fusion-360/blog/fusion-subscription-types/)

Factory evaluation `be5bfe8fa5ff42de8792c720fafedd736a0cfee618ced81ba95dbd18944d891c`. Buyer estimate `83de4f2c3023521a1b9a9b02c436b10ffa9c24a67763d700da624e53036ad095`. Workshop estimate `59db6c1b6cced6790c56279c291b1c2bc6cdc1d7e6731de1b5badd2baad19a0f`.

Rebuild locally with `python3 -m cities.Baghdad.engineering.prototype.shop_costs --publish`. Check the published files with the same command and `--check`.
