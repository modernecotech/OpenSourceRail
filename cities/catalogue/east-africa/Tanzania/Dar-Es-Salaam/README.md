# Dar Es Salaam — railway design and city programme

**TZ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=dar-es-salaam) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=dar-es-salaam) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Dar Es Salaam current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 7,404,689 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 610.84 km / 2 trackways |
| Lines / operational platform groups | 14 / 262 |
| Original access markers / separately costed access sites | 309 / 119 |
| Explicit interchange references | 71 |
| Fleet including reserve | 706 six-car trainsets |
| Train distance | 395,822 train-km/day; 144,475,212 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 57.49 | 27 | 200 | 90.5 | 57 + 9 | 4,181 | S terminal ↔ N terminal |
| line-2 | 71.95 | 28 | 200 | 106.9 | 66 + 10 | 4,181 | SE terminal ↔ N terminal |
| line-3 | 46.61 | 18 | 200 | 69.3 | 44 + 7 | 4,181 | NW terminal ↔ SE terminal |
| line-4 | 51.97 | 32 | 200 | 90.6 | 57 + 9 | 4,181 | N terminal ↔ S terminal |
| line-5 | 29.14 | 13 | 200 | 55.8 | 36 + 6 | 4,181 | S terminal ↔ NE terminal |
| line-6 | 43.07 | 16 | 200 | 72.5 | 46 + 7 | 4,181 | NW terminal ↔ SE terminal |
| line-7 | 27.57 | 12 | 200 | 41.3 | 27 + 5 | 4,181 | NE terminal ↔ W terminal |
| line-8 | 37.70 | 25 | 200 | 67.4 | 43 + 7 | 4,181 | NE terminal ↔ SW terminal |
| line-9 | 187.17 | 72 | 200 | 285.4 | 172 + 26 | 4,181 | Ring / closed circuit |
| line-10 | 6.19 | 3 | 200 | 8.9 | 8 + 2 | 4,181 | E terminal ↔ S terminal |
| line-11 | 8.21 | 3 | 200 | 12.5 | 10 + 2 | 4,181 | SW terminal ↔ S terminal |
| line-12 | 8.77 | 3 | 200 | 15.5 | 12 + 2 | 4,181 | SE terminal ↔ SE terminal |
| line-13 | 13.10 | 3 | 200 | 14.6 | 11 + 2 | 4,181 | W terminal ↔ SW terminal |
| line-14 | 21.90 | 7 | 200 | 30.0 | 20 + 3 | 4,181 | S terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 131.70 | False | Unestablished |
| 800.00 | 13.33 | 526.78 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,676,747 kWh mechanical | 612.01 GWh mechanical |
| Nominal auxiliary load | 2,302,020 kWh | 840.24 GWh |
| Auxiliary supply including scenario charging losses | 2,423,179 kWh | 884.46 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $105.18m | $271.60m | $815.60m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |
| line-12 | Station launch reference | 0 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 57.49 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 71.95 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 46.61 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 51.97 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 4 / 749.2 kW | 27.57 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 37.70 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 187.17 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-12 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-13 | 4 / 749.2 kW | 13.10 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 21.90 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 7,003.1 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 5,708.6 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,835.9 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,150.8 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,880.4 m | 5,554.5 m |
| line-8 | 2 | Coast stops before receiving zone | 6,740.2 m | 5,554.5 m |
| line-9 | 4 | Coast stops before receiving zone | 6,632.9 m | 5,554.5 m |
| line-13 | 2 | Coast stops before receiving zone | 6,833.4 m | 5,554.5 m |
| line-14 | 2 | Coast stops before receiving zone | 6,286.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 48.46 km |
| Bridge route | 24.14 km |
| Elevated route | 538.24 km |
| Tunnel route | 0.00 km |
| Precast span stock | 57,112 spans |
| Independent supports | 59,292 |
| Running rail | 2,454.79 rail-km / 147,803 t |
| Complete fastening sets | 4,295,881 |
| Protected at-grade crossing packages | 413 |
| Bridge runs / tunnel portals | 333 / 0 |
| Additional station track | 5,720 m |
| Access connector allowance | 3,884.5 m; actual accessible paths require survey |
| Pooled depot area | 492,440 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.94m | $10.23m | $66.70m |
| Civil production campaign | $15.81m | $78.31m | $470.69m |

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
| low | make | 23 | 199,892 | 1,484,912 | 1,979,883 |
| base | make | 54 | 485,452 | 3,883,616 | 5,178,155 |
| high | make | 146 | 1,313,576 | 10,737,056 | 14,316,075 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 121 | Unestablished | 874,467 | 437.2 |
| Vehicle production / low | 100 | 200 | Unestablished | Unestablished |
| Civil field / low | 208 | 416 | 2,155,435 | Unestablished |
| Civil other installation / low | 1,394 | 2,788 | 14,489,485 | Unestablished |
| Civil precast / low | 184 | 368 | 1,979,883 | Unestablished |
| Control room and access-site coverage / base | 242 | Unestablished | 1,987,425 | 993.7 |
| Vehicle production / base | 283 | 566 | Unestablished | Unestablished |
| Civil field / base | 770 | 1,540 | 6,770,901 | Unestablished |
| Civil other installation / base | 10,198 | 20,396 | 89,738,386 | Unestablished |
| Civil precast / base | 432 | 864 | 5,178,155 | Unestablished |
| Control room and access-site coverage / high | 484 | Unestablished | 4,769,820 | 2,384.9 |
| Vehicle production / high | 776 | 1,552 | Unestablished | Unestablished |
| Civil field / high | 3,352 | 6,704 | 18,766,464 | Unestablished |
| Civil other installation / high | 103,693 | 207,386 | 580,677,783 | Unestablished |
| Civil precast / high | 1,168 | 2,336 | 14,316,075 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 238 | 977.3 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.894bn | $10.395bn | $63.126bn |
| Installed capital / route-km | $4.74m | $17.02m | $103.34m |
| 30-year whole-life NPV | $5.855bn | $20.574bn | $117.974bn |
| Annual operating provision | $139.93m | $457.40m | $2.298bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $2.245bn | $2.245bn |
| Guideway | $860.60m | $860.60m |
| Stations power | $1.468bn | $1.468bn |
| Factory tooling | $88.54m | $88.54m |
| Construction | $4.893bn | $4.893bn |
| Land utilities depot | $567.27m | $567.27m |
| Fleet | $204.83m | $204.83m |
| Energy | $0 | $4.697bn |
| Operations | $0 | $268.84m |
| Maintenance | $0 | $2.667bn |
| Renewals | $0 | $2.174bn |
| Recovery | $67.88m | $138.31m |
| Reliability | $0 | $206.81m |
| Disposal | $0 | $96.15m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-419.67m | $-19.921bn | -0.62 |
| 50% | 150.91m | 0.50 | $75.45m | $-381.94m | $-19.269bn | -0.57 |
| 50% | 150.91m | 1.00 | $150.91m | $-306.49m | $-17.964bn | -0.46 |
| 75% | 226.36m | 0.25 | $56.59m | $-400.81m | $-19.595bn | -0.60 |
| 75% | 226.36m | 0.50 | $113.18m | $-344.22m | $-18.617bn | -0.51 |
| 75% | 226.36m | 1.00 | $226.36m | $-231.04m | $-16.660bn | -0.34 |
| 100% | 301.81m | 0.25 | $75.45m | $-381.94m | $-19.269bn | -0.57 |
| 100% | 301.81m | 0.50 | $150.91m | $-306.49m | $-17.964bn | -0.46 |
| 100% | 301.81m | 1.00 | $301.81m | $-155.58m | $-15.355bn | -0.23 |

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
| low | $2.026bn | $868.13m | $187.30m |
| base | $7.276bn | $3.118bn | $672.79m |
| high | $44.188bn | $18.938bn | $4.086bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/dar-es-salaam.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Tanzania/Dar-Es-Salaam) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `8038bd54682108856f9b7c4469277530816ffe5b42d2d4edc67d62ba6034b22b` |
| cost_evaluation_id | `e58da469b951996b81ec99d71bc6a29c5cecbdd827dfce845288a1e5a7f56dc2` |
| outline_evaluation_id | `1cc1162c661afe1f97e31240510bff29bfc64249ac66791d0c5403be9d06a9eb` |
| research_configuration_id | `64cdbde3d8e521908d21cdb9725c37d923da4354759a1d9f01f39b9c20b91edd` |
| seed_id | `b0cc31dcee622f938fc5cbfb352b08787aa8d04fa95878c5421d18b72a8e526f` |
| selected_alignment_id | `93541cd37bfbe33ef514e940b5afcf0ab99442af5e42aab93ee9757411364b57` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `54e2d02697d3eae4cb5db985501215b7a55c9c74104a8f806af6c1e6ac0cca8e` |
| source_result_sha256 | `c2d901b715bc6a4e13ef76707ef0c2e184a1943886069d6af0bb0f0a3aec209b` |

Atlas packet `082a719deec56b36b8a516dbb316a1a60a2645c2b60a1d41b2811b154eaa63e6`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
