# Khartoum — railway design and city programme

**SD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=khartoum) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=khartoum) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Khartoum current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 5,829,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 461.13 km / 2 trackways |
| Lines / operational platform groups | 14 / 162 |
| Original access markers / separately costed access sites | 181 / 94 |
| Explicit interchange references | 43 |
| Fleet including reserve | 495 six-car trainsets |
| Train distance | 298,812 train-km/day; 109,066,426 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 43.10 | 15 | 200 | 61.7 | 39 + 6 | 4,181 | SE terminal ↔ NW terminal |
| line-2 | 35.87 | 17 | 200 | 57.0 | 36 + 6 | 4,181 | E terminal ↔ W terminal |
| line-3 | 57.62 | 16 | 200 | 76.6 | 48 + 8 | 4,181 | N terminal ↔ SE terminal |
| line-4 | 23.11 | 13 | 200 | 43.9 | 29 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-5 | 43.75 | 15 | 200 | 61.7 | 39 + 6 | 4,181 | NE terminal ↔ S terminal |
| line-6 | 34.04 | 10 | 200 | 45.8 | 30 + 5 | 4,181 | S terminal ↔ NE terminal |
| line-7 | 42.88 | 17 | 200 | 63.4 | 40 + 6 | 4,181 | W terminal ↔ E terminal |
| line-8 | 27.92 | 9 | 200 | 38.1 | 25 + 4 | 4,181 | SW terminal ↔ N terminal |
| line-9 | 118.61 | 38 | 200 | 170.6 | 104 + 16 | 4,181 | Ring / closed circuit |
| line-10 | 7.61 | 3 | 200 | 9.6 | 8 + 2 | 4,181 | W terminal ↔ W terminal |
| line-11 | 6.74 | 2 | 200 | 6.7 | 6 + 1 | 4,181 | NW terminal ↔ NW terminal |
| line-12 | 6.12 | 2 | 200 | 6.1 | 6 + 1 | 4,181 | SE terminal ↔ SE terminal |
| line-13 | 7.17 | 3 | 200 | 13.1 | 10 + 2 | 4,181 | SE terminal ↔ SE terminal |
| line-14 | 6.59 | 2 | 200 | 6.6 | 6 + 1 | 4,181 | W terminal ↔ W terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 81.43 | False | Unestablished |
| 800.00 | 13.33 | 325.72 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,238,225 kWh mechanical | 451.95 GWh mechanical |
| Nominal auxiliary load | 1,610,280 kWh | 587.75 GWh |
| Auxiliary supply including scenario charging losses | 1,695,032 kWh | 618.69 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $75.29m | $194.99m | $589.13m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Station launch reference | 0 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 43.10 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 35.87 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 57.62 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 43.75 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 34.04 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 42.88 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 27.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 118.61 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 4 / 749.2 kW | 7.61 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 4 / 749.2 kW | 6.74 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 4 / 749.2 kW | 6.12 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-14 | 4 / 749.2 kW | 6.59 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 3 | Coast stops before receiving zone | 5,726.5 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,703.4 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,624.2 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,870.9 m | 5,554.5 m |
| line-6 | 2 | Coast stops before receiving zone | 6,909.8 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,398.1 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 5,954.2 m | 5,554.5 m |
| line-9 | 5 | Coast stops before receiving zone | 6,744.4 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 6,071.9 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,741.7 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 6,124.5 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 6,592.8 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 35.93 km |
| Bridge route | 16.22 km |
| Elevated route | 408.98 km |
| Tunnel route | 0.00 km |
| Precast span stock | 42,822 spans |
| Independent supports | 43,590 |
| Running rail | 1,844.52 rail-km / 111,059 t |
| Complete fastening sets | 3,227,909 |
| Protected at-grade crossing packages | 216 |
| Bridge runs / tunnel portals | 87 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,476.1 m; actual accessible paths require survey |
| Pooled depot area | 345,540 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.56m | $7.86m | $47.12m |
| Civil production campaign | $11.99m | $59.24m | $355.31m |

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
| low | make | 17 | 149,877 | 1,113,372 | 1,484,496 |
| base | make | 41 | 363,987 | 2,911,896 | 3,882,528 |
| high | make | 110 | 984,906 | 8,050,536 | 10,734,048 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 96 | Unestablished | 693,792 | 346.9 |
| Vehicle production / low | 70 | 140 | Unestablished | Unestablished |
| Civil field / low | 155 | 310 | 1,606,880 | Unestablished |
| Civil other installation / low | 884 | 1,768 | 9,184,145 | Unestablished |
| Civil precast / low | 136 | 272 | 1,484,496 | Unestablished |
| Control room and access-site coverage / base | 192 | Unestablished | 1,576,800 | 788.4 |
| Vehicle production / base | 198 | 396 | Unestablished | Unestablished |
| Civil field / base | 574 | 1,148 | 5,049,024 | Unestablished |
| Civil other installation / base | 6,559 | 13,118 | 57,710,849 | Unestablished |
| Civil precast / base | 328 | 656 | 3,882,528 | Unestablished |
| Control room and access-site coverage / high | 384 | Unestablished | 3,784,320 | 1,892.2 |
| Vehicle production / high | 544 | 1,088 | Unestablished | Unestablished |
| Civil field / high | 2,500 | 5,000 | 13,996,960 | Unestablished |
| Civil other installation / high | 67,479 | 134,958 | 377,879,304 | Unestablished |
| Civil precast / high | 880 | 1,760 | 10,734,048 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 188 | 772.0 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.021bn | $7.178bn | $43.465bn |
| Installed capital / route-km | $4.38m | $15.57m | $94.26m |
| 30-year whole-life NPV | $4.130bn | $14.448bn | $82.894bn |
| Annual operating provision | $100.33m | $328.60m | $1.662bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.615bn | $1.615bn |
| Guideway | $645.70m | $645.70m |
| Stations power | $959.40m | $959.40m |
| Factory tooling | $67.11m | $67.11m |
| Construction | $3.275bn | $3.275bn |
| Land utilities depot | $418.83m | $418.83m |
| Fleet | $146.07m | $146.07m |
| Energy | $0 | $3.372bn |
| Operations | $0 | $213.30m |
| Maintenance | $0 | $1.888bn |
| Renewals | $0 | $1.521bn |
| Recovery | $51.32m | $104.57m |
| Reliability | $0 | $156.12m |
| Disposal | $0 | $66.39m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-290.88m | $-13.795bn | -0.63 |
| 50% | 150.91m | 0.50 | $75.45m | $-253.15m | $-13.143bn | -0.54 |
| 50% | 150.91m | 1.00 | $150.91m | $-177.70m | $-11.838bn | -0.38 |
| 75% | 226.36m | 0.25 | $56.59m | $-272.01m | $-13.469bn | -0.59 |
| 75% | 226.36m | 0.50 | $113.18m | $-215.42m | $-12.491bn | -0.46 |
| 75% | 226.36m | 1.00 | $226.36m | $-102.25m | $-10.533bn | -0.22 |
| 100% | 301.81m | 0.25 | $75.45m | $-253.15m | $-13.143bn | -0.54 |
| 100% | 301.81m | 0.50 | $150.91m | $-177.70m | $-11.838bn | -0.38 |
| 100% | 301.81m | 1.00 | $301.81m | $-26.79m | $-9.229bn | -0.06 |

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
| low | $1.415bn | $606.24m | $130.79m |
| base | $5.025bn | $2.153bn | $464.60m |
| high | $30.425bn | $13.039bn | $2.813bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/khartoum.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/north-africa/Sudan/Khartoum) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `eb2cf40281dd9e1cf4ed989402a28f5873abdb30ec446079607a5626c1db7e62` |
| cost_evaluation_id | `1a0e82e332f1633b9bb43d4226265bd82dab5ce8e43fa9b0a697232c17bc5f5d` |
| outline_evaluation_id | `27f53b3712b61bcbbcd2c786787d9c359aadbf89a177ea5b8c60081db69b994e` |
| research_configuration_id | `8180ed6cf73b3cf066c657cf3cbd4838b58060871363b46010164ba394d38ef0` |
| seed_id | `d76c2424289bc9c9c0c387ae6b3a84f72413ace88b55a9da59a22d68a089e86e` |
| selected_alignment_id | `8f15ec8667b0af2c23080382d7ce45e554e18bbbd822c3f60c7c3b8215a75aa9` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `16379d30146a3f12d4082a83d61af3077e9ac0a49d048fd2c791ff8f7f6fbadd` |
| source_result_sha256 | `bb2bacde708b0e248ad5a80c9b82517ee891c1b1e4cbf33435419029362b94fb` |

Atlas packet `ba6d896a1bcc4deb25eadffe022dc2d2789cf8aec1fc0e52c57cbbcbbb7aa02d`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
