# Amman — railway design and city programme

**JO · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=amman) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=amman) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Amman current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 4,007,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 412.73 km / 2 trackways |
| Lines / operational platform groups | 14 / 128 |
| Original access markers / separately costed access sites | 132 / 77 |
| Explicit interchange references | 39 |
| Fleet including reserve | 469 six-car trainsets |
| Train distance | 267,451 train-km/day; 97,619,682 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 48.15 | 13 | 200 | 64.5 | 41 + 7 | 4,181 | SW terminal ↔ NE terminal |
| line-2 | 52.59 | 14 | 200 | 69.2 | 44 + 7 | 4,181 | N terminal ↔ S terminal |
| line-3 | 30.28 | 9 | 200 | 40.9 | 27 + 5 | 4,181 | S terminal ↔ NW terminal |
| line-4 | 18.22 | 8 | 200 | 33.0 | 22 + 4 | 4,181 | N terminal ↔ S terminal |
| line-5 | 32.99 | 10 | 200 | 45.6 | 30 + 5 | 4,181 | W terminal ↔ SE terminal |
| line-6 | 35.80 | 13 | 200 | 63.8 | 41 + 7 | 4,181 | E terminal ↔ W terminal |
| line-7 | 28.80 | 10 | 200 | 40.5 | 27 + 5 | 4,181 | E terminal ↔ W terminal |
| line-8 | 34.87 | 11 | 200 | 61.0 | 39 + 6 | 4,181 | NE terminal ↔ SW terminal |
| line-9 | 82.33 | 23 | 200 | 115.1 | 70 + 11 | 4,181 | Ring / closed circuit |
| line-10 | 11.10 | 4 | 200 | 17.0 | 13 + 2 | 4,181 | S terminal ↔ E terminal |
| line-11 | 8.37 | 3 | 200 | 12.9 | 10 + 2 | 4,181 | NW terminal ↔ NW terminal |
| line-12 | 13.34 | 4 | 200 | 22.1 | 16 + 3 | 4,181 | E terminal ↔ E terminal |
| line-13 | 8.30 | 3 | 200 | 14.0 | 11 + 2 | 4,181 | NE terminal ↔ NE terminal |
| line-14 | 7.59 | 3 | 200 | 12.1 | 10 + 2 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 64.34 | False | Unestablished |
| 800.00 | 13.33 | 257.36 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 945,660 kWh mechanical | 345.17 GWh mechanical |
| Nominal auxiliary load | 1,515,780 kWh | 553.26 GWh |
| Auxiliary supply including scenario charging losses | 1,595,558 kWh | 582.38 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 9.88 GWh |
| Total priced grid-supply scenario | See annual budget | 1,024.35 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $65.98m | $169.59m | $504.07m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |
| line-12 | Station launch reference | 0 kg | 250 kg |
| line-13 | Station launch reference | 0 kg | 250 kg |
| line-14 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 48.15 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 52.59 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 30.28 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 32.99 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 4 / 749.2 kW | 28.80 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 82.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-12 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-13 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-14 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 5,744.8 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 5,761.9 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,689.5 m | 5,554.5 m |
| line-5 | 4 | Coast stops before receiving zone | 6,699.9 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,554.8 m | 5,554.5 m |
| line-9 | 5 | Coast stops before receiving zone | 6,052.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 31.58 km |
| Bridge route | 1.65 km |
| Elevated route | 379.51 km |
| Tunnel route | 0.00 km |
| Precast span stock | 38,334 spans |
| Independent supports | 38,964 |
| Running rail | 1,650.93 rail-km / 99,403 t |
| Complete fastening sets | 2,889,134 |
| Protected at-grade crossing packages | 252 |
| Bridge runs / tunnel portals | 26 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 381.2 m; actual accessible paths require survey |
| Pooled depot area | 326,924 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.41m | $7.50m | $45.28m |
| Civil production campaign | $10.78m | $53.25m | $318.68m |

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
| low | make | 15 | 134,169 | 996,684 | 1,328,912 |
| base | make | 37 | 325,839 | 2,606,712 | 3,475,616 |
| high | make | 98 | 881,682 | 7,206,792 | 9,609,056 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 79 | Unestablished | 570,933 | 285.5 |
| Vehicle production / low | 66 | 132 | Unestablished | Unestablished |
| Civil field / low | 139 | 278 | 1,437,856 | Unestablished |
| Civil other installation / low | 716 | 1,432 | 7,443,533 | Unestablished |
| Civil precast / low | 120 | 240 | 1,328,912 | Unestablished |
| Control room and access-site coverage / base | 158 | Unestablished | 1,297,575 | 648.8 |
| Vehicle production / base | 188 | 376 | Unestablished | Unestablished |
| Civil field / base | 514 | 1,028 | 4,518,016 | Unestablished |
| Civil other installation / base | 4,812 | 9,624 | 42,342,539 | Unestablished |
| Civil precast / base | 296 | 592 | 3,475,616 | Unestablished |
| Control room and access-site coverage / high | 316 | Unestablished | 3,114,180 | 1,557.1 |
| Vehicle production / high | 515 | 1,030 | Unestablished | Unestablished |
| Civil field / high | 2,237 | 4,474 | 12,525,088 | Unestablished |
| Civil other installation / high | 46,459 | 92,918 | 260,168,376 | Unestablished |
| Civil precast / high | 784 | 1,568 | 9,609,056 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 154 | 632.4 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.695bn | $5.872bn | $34.522bn |
| Installed capital / route-km | $4.11m | $14.23m | $83.64m |
| 30-year whole-life NPV | $3.549bn | $12.298bn | $69.311bn |
| Annual operating provision | $87.99m | $288.56m | $1.463bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.399bn | $1.399bn |
| Guideway | $578.00m | $578.00m |
| Stations power | $903.16m | $903.16m |
| Factory tooling | $60.75m | $60.75m |
| Construction | $2.370bn | $2.370bn |
| Land utilities depot | $384.50m | $384.50m |
| Fleet | $130.55m | $130.55m |
| Energy | $0 | $2.933bn |
| Operations | $0 | $175.53m |
| Maintenance | $0 | $1.694bn |
| Renewals | $0 | $1.381bn |
| Recovery | $46.36m | $94.45m |
| Reliability | $0 | $139.74m |
| Disposal | $0 | $54.32m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Price inputs and confidence

These are calculated v0.6-derived outline prices. Country-specific demand, ground conditions, local contracts and supplier quotations are not established by this calculation. The price includes the declared mixed propulsion research configurations shown above; it is not a quotation for an already proven station-powered railway.

| Operating input | Low | Base | High |
|---|---|---|---|
| Electricity · US$/kWh | 0.066 | 0.166 | 0.464 |
| Loaded operating wage · US$/paid hour | 6.21 | 7.82 | 10.93 |

Input status: transferred-reference-estimates. Scoped local tariff/wage overrides can replace those accounts; they do not apply a blanket discount to imported equipment or civil quantities. Reserve-fleet auxiliary consumption and charging losses are included in the electricity budget.

| Largest capital allowance | Base estimate | Share of capital |
|---|---|---|
| City project risk contingency | $1.174bn | 20.0% |
| Network delivered assembled fleet | $1.143bn | 19.5% |
| Design prototypes independent review | $347.16m | 5.9% |
| Repeat box beams | $282.09m | 4.8% |
| Piers and foundations | $261.45m | 4.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.695bn | $5.872bn | $34.522bn |
| Water-evidence alternative capital | $1.683bn | $5.802bn | $33.947bn |
| Alternative capital / route-km | $4.08m | $14.06m | $82.25m |
| Alternative whole-life NPV | $3.537bn | $12.226bn | $68.721bn |
| Included non-water obstruction reserve | $114,108 | $760,720 | $5.33m |

1.52 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-250.83m | $-11.646bn | -0.66 |
| 50% | 150.91m | 0.50 | $75.45m | $-213.11m | $-10.993bn | -0.56 |
| 50% | 150.91m | 1.00 | $150.91m | $-137.65m | $-9.688bn | -0.36 |
| 75% | 226.36m | 0.25 | $56.59m | $-231.97m | $-11.319bn | -0.61 |
| 75% | 226.36m | 0.50 | $113.18m | $-175.38m | $-10.341bn | -0.46 |
| 75% | 226.36m | 1.00 | $226.36m | $-62.20m | $-8.384bn | -0.16 |
| 100% | 301.81m | 0.25 | $75.45m | $-213.11m | $-10.993bn | -0.56 |
| 100% | 301.81m | 0.50 | $150.91m | $-137.65m | $-9.688bn | -0.36 |
| 100% | 301.81m | 1.00 | $301.81m | $13.25m | $-7.079bn | 0.03 |

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
| low | $1.187bn | $508.54m | $109.71m |
| base | $4.111bn | $1.762bn | $380.09m |
| high | $24.165bn | $10.357bn | $2.234bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/amman.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Jordan/Amman) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `fb81af96079ac2ad1de5af7213ba84c3845912f3fa4ced071f777b5930cfc27e` |
| cost_evaluation_id | `3fab8d4a9fced39eeae4615c9508924ae1e22e2ca52c209d381ca147586068b1` |
| outline_evaluation_id | `f070fab8a47ac55b53ba7ce089a8856c288819506e444ac21258cff098bc1b61` |
| research_configuration_id | `d64be5eb034898dca4d2ee109c710fca90d33188b71ef898ed797d5bf2d0fb82` |
| seed_id | `4b1231219d3316207799294ce73fc2ce52d6c0e690cce768393996a7211704f7` |
| selected_alignment_id | `987d820ab0308ef36b8af12b35bba0083fd96d75a82ddb09020d658a50b76ccb` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `5a76a84615476d9e6d9f35844bd6e81a8372d259d969e63ba1cb0ff4760b35f5` |
| source_result_sha256 | `2fca782751596de96a74da5d743793c7f1cf3ebc8ed8fcfed43e1afbd666ff96` |

Atlas packet `8250974951fb706cdee58497429616589c56e325eb994966c2236dbf2aa8c9e5`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
