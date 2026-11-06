# Kanpur — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kanpur) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kanpur) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kanpur current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,200,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 363.04 km / 2 trackways |
| Lines / operational platform groups | 8 / 113 |
| Original access markers / separately costed access sites | 115 / 70 |
| Explicit interchange references | 30 |
| Fleet including reserve | 398 six-car trainsets |
| Train distance | 235,248 train-km/day; 85,865,647 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 29.96 | 11 | 200 | 54.5 | 35 + 6 | 4,181 | SE terminal ↔ NW terminal |
| line-2 | 31.39 | 11 | 200 | 45.3 | 29 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-3 | 53.39 | 17 | 200 | 74.2 | 47 + 8 | 4,181 | W terminal ↔ E terminal |
| line-4 | 34.50 | 13 | 200 | 49.7 | 32 + 5 | 4,181 | SW terminal ↔ NE terminal |
| line-5 | 34.16 | 13 | 200 | 64.9 | 41 + 7 | 4,181 | E terminal ↔ W terminal |
| line-6 | 43.87 | 15 | 200 | 62.0 | 39 + 6 | 4,181 | N terminal ↔ S terminal |
| line-7 | 24.25 | 8 | 200 | 45.2 | 29 + 5 | 4,181 | SW terminal ↔ E terminal |
| line-8 | 111.50 | 25 | 200 | 150.0 | 90 + 14 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 56.80 | False | Unestablished |
| 800.00 | 13.33 | 227.20 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 874,533 kWh mechanical | 319.20 GWh mechanical |
| Nominal auxiliary load | 1,292,760 kWh | 471.86 GWh |
| Auxiliary supply including scenario charging losses | 1,360,800 kWh | 496.69 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $57.45m | $148.14m | $443.40m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 31.39 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 53.39 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 34.50 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 43.87 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 111.50 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 2 | Coast stops before receiving zone | 6,967.8 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,907.6 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,246.5 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,600.1 m | 5,554.5 m |
| line-8 | 10 | Coast stops before receiving zone | 6,806.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 28.86 km |
| Bridge route | 18.77 km |
| Elevated route | 315.40 km |
| Tunnel route | 0.00 km |
| Precast span stock | 34,096 spans |
| Independent supports | 34,708 |
| Running rail | 1,468.87 rail-km / 88,441 t |
| Complete fastening sets | 2,570,524 |
| Protected at-grade crossing packages | 101 |
| Bridge runs / tunnel portals | 101 / 0 |
| Additional station track | 8,360 m |
| Access connector allowance | 144.2 m; actual accessible paths require survey |
| Pooled depot area | 277,576 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.31m | $6.70m | $37.83m |
| Civil production campaign | $9.68m | $47.64m | $284.86m |

Factory capital is already included in the city capital ledger. It must not be added a second time. Make/buy comparisons use committed city volume, equipment/tooling, material, labour, yield and productive capacity; no speculative future-city discount is assumed.

| Component / process | Provisional route |
|---|---|
| located-stock/passive-bogie-pair/steel | buy |
| located-stock/passive-secondary/aluminium | buy |
| located-stock/retained-comfort/body/composite | buy |
| located-stock/retained-comfort/body/generic | make |
| located-stock/retained-comfort/doors/generic | Unestablished |
| located-stock/retained-comfort/glazing/generic | Unestablished |
| located-stock/retained-comfort/seating/generic | Unestablished |
| located-stock/wheel-underframe/aluminium | make |
| unlocated-account/attachments | Unestablished |
| unlocated-account/passive-bogie-pair | Unestablished |
| unlocated-account/retained-comfort/HVAC | Unestablished |
| unlocated-account/retained-comfort/body | buy |
| unlocated-account/retained-comfort/doors | Unestablished |
| unlocated-account/retained-comfort/frame-joints | Unestablished |
| unlocated-account/retained-comfort/glazing | Unestablished |
| unlocated-account/retained-comfort/seating | Unestablished |
| unlocated-account/roof-thermal | Unestablished |
| unlocated-account/services | Unestablished |
| six-car-final-vehicle-assembly | Unestablished |
| reference-factory-to-assembly-delivery | Unestablished |

| Precast case | Selected route | Parallel cells | Required cell-hours | Productive person-hours | Paid person-hours |
|---|---|---|---|---|---|
| low | make | 14 | 119,336 | 886,496 | 1,181,995 |
| base | make | 33 | 289,816 | 2,318,528 | 3,091,371 |
| high | make | 88 | 784,208 | 6,410,048 | 8,546,731 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 72 | Unestablished | 520,344 | 260.2 |
| Vehicle production / low | 56 | 112 | Unestablished | Unestablished |
| Civil field / low | 124 | 248 | 1,279,445 | Unestablished |
| Civil other installation / low | 868 | 1,736 | 9,027,119 | Unestablished |
| Civil precast / low | 112 | 224 | 1,181,995 | Unestablished |
| Control room and access-site coverage / base | 144 | Unestablished | 1,182,600 | 591.3 |
| Vehicle production / base | 160 | 320 | Unestablished | Unestablished |
| Civil field / base | 457 | 914 | 4,020,181 | Unestablished |
| Civil other installation / base | 6,206 | 12,412 | 54,611,289 | Unestablished |
| Civil precast / base | 264 | 528 | 3,091,371 | Unestablished |
| Control room and access-site coverage / high | 288 | Unestablished | 2,838,240 | 1,419.1 |
| Vehicle production / high | 437 | 874 | Unestablished | Unestablished |
| Civil field / high | 1,991 | 3,982 | 11,144,789 | Unestablished |
| Civil other installation / high | 61,942 | 123,884 | 346,869,761 | Unestablished |
| Civil precast / high | 704 | 1,408 | 8,546,731 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 140 | 574.9 | Source access coverage; accessible assistance and local duties require roster design |
| Vehicle workshop / electrical / brakes | Unestablished | Unestablished | Maintenance budget envelope exists; detailed roles, competence and productive hours require routing |
| Civil infrastructure / track / inspections | Unestablished | Unestablished | Maintenance scope exists; inspection tasks and geographic workload require a site plan |
| Station power / propulsion / controls | Unestablished | Unestablished | Qualified equipment-specific maintenance and protection work |
| Cleaning / security / passenger emergencies | Unestablished | Unestablished | Site/service responsibilities and employee/contractor allocation remain to be sized |
| Programme management / procurement / finance / HR | Unestablished | Unestablished | Business entity, reporting lines and operating overhead allocation require review |
| Training / competence / independent assurance | Unestablished | Unestablished | Independent release authority and competence records remain mandatory |

**Staffing boundary:** the operations rows size control-room and access-site coverage only. They are not the complete operating company. Unallocated maintenance/support functions have budget envelopes or open allocation; their unknown FTE is not zero. No recruitment or complete-organisation claim follows from this table.

The provisional delivery sequence is: Survey and site investigation → Detailed design and independent review → Factory setup and procurement → Foundation and civil production → Transport and installation → Power controls and access installation → Integration testing and release. Factories, field crews and access must be checked together. Aggregate resource envelopes are distinct from resource-levelled, site-approved construction schedules.

[Workforce cases](engineering/outline/workforce.csv) · [Production and construction requirements](engineering/outline/delivery_requirements.csv)

## Capital, operating costs and whole-life economics

| Programme estimate | Low | Base | High |
|---|---|---|---|
| Installed capital | $1.688bn | $6.085bn | $37.070bn |
| Installed capital / route-km | $4.65m | $16.76m | $102.11m |
| 30-year whole-life NPV | $3.332bn | $11.801bn | $68.142bn |
| Annual operating provision | $77.58m | $255.71m | $1.300bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.222bn | $1.222bn |
| Guideway | $514.15m | $514.15m |
| Stations power | $890.84m | $890.84m |
| Factory tooling | $54.35m | $54.35m |
| Construction | $2.919bn | $2.919bn |
| Land utilities depot | $330.92m | $330.92m |
| Fleet | $112.84m | $112.84m |
| Energy | $0 | $2.562bn |
| Operations | $0 | $159.97m |
| Maintenance | $0 | $1.534bn |
| Renewals | $0 | $1.238bn |
| Recovery | $41.39m | $84.33m |
| Reliability | $0 | $122.91m |
| Disposal | $0 | $56.29m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-234.15m | $-11.429bn | -0.59 |
| 50% | 86.23m | 0.50 | $43.12m | $-212.60m | $-11.056bn | -0.54 |
| 50% | 86.23m | 1.00 | $86.23m | $-169.48m | $-10.310bn | -0.43 |
| 75% | 129.35m | 0.25 | $32.34m | $-223.38m | $-11.242bn | -0.57 |
| 75% | 129.35m | 0.50 | $64.67m | $-191.04m | $-10.683bn | -0.49 |
| 75% | 129.35m | 1.00 | $129.35m | $-126.37m | $-9.565bn | -0.32 |
| 100% | 172.46m | 0.25 | $43.12m | $-212.60m | $-11.056bn | -0.54 |
| 100% | 172.46m | 0.50 | $86.23m | $-169.48m | $-10.310bn | -0.43 |
| 100% | 172.46m | 1.00 | $172.46m | $-83.25m | $-8.819bn | -0.21 |

This table holds the engineering cost case at **base** and varies demand and fare. A negative balance is retained as a financing/design warning. Operating balance excludes scheduled renewal capital and debt service; the whole-life NPV column uses the complete unfinanced cost.

| Demand hypothesis | Value |
|---|---|
| Counter-direction peak fraction | 60% |
| Mean section / peak section loading | 50% |
| Average trip / line length | 35% |
| Boardings per linked trip | 1.25 |
| Paid collection fraction | 95% |
| Daily profile | 22.2% of hours at 100% peak flow; 44.4% of hours at 45% peak flow; 33.3% of hours at 15% peak flow |

**Illustrative funding overlay:** 70% financed, 4% real annual interest, 20 years including 3 years without payments and with capitalised interest. The model draws the entire loan at year zero; a real construction draw schedule requires its own dated plan. DSCR compares annual receipts less operating provision with level post-grace debt service; no lender acceptance is implied.

| Cost case | Illustrative loan principal | Equity / grant requirement | Post-grace annual debt service |
|---|---|---|---|
| low | $1.182bn | $506.42m | $109.26m |
| base | $4.260bn | $1.826bn | $393.87m |
| high | $25.949bn | $11.121bn | $2.399bn |

[All demand, fare and funding sensitivities](engineering/outline/finance.csv). Assumptions, cost-covering fares and financing treatment are in [the complete dossier](engineering/outline/summary.json). Funding charges are separate from the canonical unfinanced engineering cost; a loan scenario does not change the railway capital ledger.

## Site, engineering and delivery evidence

| Work package | Current basis | Next evidence / action |
|---|---|---|
| Network and alignment | Mapped selected proposal and explicit interchange references | Survey alignment, land/access, gradients, clearances and crossing interfaces |
| Demand and accessibility | Declared peak-flow brief and outline passenger configuration | Local OD/demand validation, station naming, accessible walking and evacuation layouts |
| Ground, flood and utilities | Mapped civil classes and bounded site allowances | Survey control, utility records, geotechnical investigation, flood/drainage and foundation design |
| Vehicle and civil structure | Identified reference parts, mass allowances and priced quantities | Installed mass/CG, joints, fatigue, stability, bearings, moving loads and erection checks |
| Propulsion, energy and braking | Conditional force/energy/service model | Achievable force/thermal maps, independent braking, protected recovery and degraded journeys |
| Manufacturing and workforce | Calculated make/buy, tooling, shifts and resource envelopes | Detailed routing, QA, crew/workstation calendar, supplier confirmation and trial production |
| Business execution | Candidate-bound disabled procurement/BOM/HR drafts | Target-system schema validation, reviewed masters, permissions and approved release |

Outline completion is recorded positively. Physical engineering, prototype validation, procurement approval, manufacturing release and movement authority remain separate. [Candidate-bound physical evidence record](engineering/current/README.md).

## Files and reproduction

| File | Contents |
|---|---|
| [Summary](engineering/outline/summary.json) | Complete calculation-linked dossier and scenario policy |
| [Map](engineering/outline/network.svg) | Selected network over verified geographic context |
| [Lines](engineering/outline/lines.csv) / [stations](engineering/outline/stations.csv) | Service, fleet, section/stop/access references |
| [GIS bundle](engineering/outline/gis.zip) | Eight GeoJSON layers: routes, platforms, stations, original markers, interchanges, connectors, civil classes and unlocated requirements |
| [Costs](engineering/outline/costs.csv) / [finance](engineering/outline/finance.csv) | Canonical budgets and separate passenger/funding sensitivities |
| [Workforce](engineering/outline/workforce.csv) / [make-buy](engineering/outline/make_buy.csv) | Shift, resource and production comparisons |
| [Delivery requirements](engineering/outline/delivery_requirements.csv) | Provisional phase/resource and site tasks |
| [Delivery and business drafts](engineering/outline/delivery-draft.json.gz) | Source-bound procurement packages, provisional BOM/routing and disabled ERPNext/Frappe HR records |
| [Source identities](engineering/outline/manifest.json) | Presentation, atlas, outline, physical candidate and output hashes |
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kanpur.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Kanpur) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `27130666331e353154ecf85f8c6d3b3c0acb10fb1907b933c8ea4b9fae9b8906` |
| cost_evaluation_id | `4fff2edfb1877c944cb2e7a44f79b81d5f7803eb5d532405d7c0dfd11ad523f3` |
| outline_evaluation_id | `e1e54eb6d27c57652b09bc38a0dc1fbb368a7376e3f7684f7500acf309944d57` |
| research_configuration_id | `3ea4b33ee220b5128c3619c3af41a842062bb2fa82469a08c92759a09a199539` |
| seed_id | `1c4a9fabb0e411605abd70b4b06c2a18cd037f073a368b296239c0cda5f09c3c` |
| selected_alignment_id | `f042c54faaeb1e5bafb174d376b7a9d40b0d684332c2f2bbecff53f6c01db66e` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `6d5e67e9b4629775f964c9c114740efb87d9d98b2efe7a877379884fa606c214` |
| source_result_sha256 | `058beb201bdf1a66a0fe5dde5a964b0c1143020b11d002902189537605cb5f56` |

Atlas packet `a8981245f4a0beef1b96a5ada16314f51143b42d16e1077be19fff7304edef2c`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
