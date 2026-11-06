# Kinshasa — railway design and city programme

**CD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kinshasa) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kinshasa) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kinshasa current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 17,178,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 628.26 km / 2 trackways |
| Lines / operational platform groups | 14 / 507 |
| Original access markers / separately costed access sites | 617 / 143 |
| Explicit interchange references | 101 |
| Fleet including reserve | 915 six-car trainsets |
| Train distance | 407,114 train-km/day; 148,596,591 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 59.18 | 70 | 200 | 147.6 | 91 + 14 | 4,181 | NW terminal ↔ SE terminal |
| line-2 | 70.59 | 68 | 200 | 152.4 | 94 + 15 | 4,181 | E terminal ↔ NW terminal |
| line-3 | 29.44 | 22 | 200 | 61.3 | 39 + 6 | 4,181 | SE terminal ↔ W terminal |
| line-4 | 60.79 | 59 | 200 | 140.1 | 86 + 13 | 4,181 | S terminal ↔ N terminal |
| line-5 | 54.26 | 42 | 200 | 102.7 | 64 + 10 | 4,181 | SW terminal ↔ E terminal |
| line-6 | 69.60 | 38 | 200 | 117.2 | 73 + 11 | 4,181 | SE terminal ↔ NW terminal |
| line-7 | 90.65 | 71 | 200 | 176.8 | 108 + 17 | 4,181 | NE terminal ↔ SW terminal |
| line-8 | 36.49 | 16 | 200 | 64.1 | 41 + 7 | 4,181 | NE terminal ↔ W terminal |
| line-9 | 124.12 | 107 | 200 | 256.9 | 156 + 24 | 4,181 | Ring / closed circuit |
| line-10 | 6.39 | 3 | 200 | 9.3 | 8 + 2 | 4,181 | SW terminal ↔ SE terminal |
| line-11 | 6.52 | 3 | 200 | 9.9 | 8 + 2 | 4,181 | E terminal ↔ SE terminal |
| line-12 | 6.54 | 2 | 200 | 6.5 | 6 + 1 | 4,181 | E terminal ↔ NE terminal |
| line-13 | 7.38 | 4 | 200 | 12.1 | 10 + 2 | 4,181 | SE terminal ↔ SE terminal |
| line-14 | 6.32 | 2 | 200 | 6.3 | 6 + 1 | 4,181 | E terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 254.85 | False | Unestablished |
| 800.00 | 13.33 | 1,019.38 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 2,102,838 kWh mechanical | 767.54 GWh mechanical |
| Nominal auxiliary load | 2,986,200 kWh | 1,089.96 GWh |
| Auxiliary supply including scenario charging losses | 3,143,368 kWh | 1,147.33 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 18.15 GWh |
| Total priced grid-supply scenario | See annual budget | 2,119.40 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $136.69m | $350.89m | $1.040bn |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Station launch reference | 0 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 70.59 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 54.26 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 69.60 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 90.65 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 124.12 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-12 | 4 / 749.2 kW | 6.54 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-14 | 4 / 749.2 kW | 6.32 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 6,658.7 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,857.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,597.9 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,463.9 m | 5,554.5 m |
| line-9 | 3 | Coast stops before receiving zone | 6,862.0 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 6,540.4 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 6,322.9 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 31.06 km |
| Bridge route | 15.43 km |
| Elevated route | 581.77 km |
| Tunnel route | 0.00 km |
| Precast span stock | 61,316 spans |
| Independent supports | 62,650 |
| Running rail | 2,564.97 rail-km / 154,437 t |
| Complete fastening sets | 4,488,696 |
| Protected at-grade crossing packages | 308 |
| Bridge runs / tunnel portals | 156 / 0 |
| Additional station track | 25,960 m |
| Access connector allowance | 8,650.3 m; actual accessible paths require survey |
| Pooled depot area | 638,196 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $2.36m | $13.66m | $85.63m |
| Civil production campaign | $16.90m | $83.99m | $504.88m |

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
| low | make | 24 | 214,606 | 1,594,216 | 2,125,621 |
| base | make | 58 | 521,186 | 4,169,488 | 5,559,317 |
| high | make | 157 | 1,410,268 | 11,527,408 | 15,369,877 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 145 | Unestablished | 1,047,915 | 524.0 |
| Vehicle production / low | 129 | 258 | Unestablished | Unestablished |
| Civil field / low | 222 | 444 | 2,303,360 | Unestablished |
| Civil other installation / low | 2,277 | 4,554 | 23,675,494 | Unestablished |
| Civil precast / low | 192 | 384 | 2,125,621 | Unestablished |
| Control room and access-site coverage / base | 290 | Unestablished | 2,381,625 | 1,190.8 |
| Vehicle production / base | 366 | 732 | Unestablished | Unestablished |
| Civil field / base | 823 | 1,646 | 7,237,099 | Unestablished |
| Civil other installation / base | 13,831 | 27,662 | 121,705,112 | Unestablished |
| Civil precast / base | 464 | 928 | 5,559,317 | Unestablished |
| Control room and access-site coverage / high | 580 | Unestablished | 5,715,900 | 2,857.9 |
| Vehicle production / high | 1,005 | 2,010 | Unestablished | Unestablished |
| Civil field / high | 3,583 | 7,166 | 20,061,973 | Unestablished |
| Civil other installation / high | 119,800 | 239,600 | 670,878,140 | Unestablished |
| Civil precast / high | 1,256 | 2,512 | 15,369,877 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 286 | 1,174.4 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $3.838bn | $13.031bn | $73.092bn |
| Installed capital / route-km | $6.11m | $20.74m | $116.34m |
| 30-year whole-life NPV | $7.840bn | $26.790bn | $146.185bn |
| Annual operating provision | $184.62m | $605.11m | $3.013bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $2.767bn | $2.767bn |
| Guideway | $916.18m | $916.18m |
| Stations power | $2.973bn | $2.973bn |
| Factory tooling | $97.65m | $97.65m |
| Construction | $5.303bn | $5.303bn |
| Land utilities depot | $647.14m | $647.14m |
| Fleet | $256.93m | $256.93m |
| Energy | $0 | $6.068bn |
| Operations | $0 | $322.17m |
| Maintenance | $0 | $3.789bn |
| Renewals | $0 | $3.175bn |
| Recovery | $69.54m | $141.68m |
| Reliability | $0 | $212.71m |
| Disposal | $0 | $120.53m |

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
| City project risk contingency | $2.606bn | 20.0% |
| Network delivered assembled fleet | $2.229bn | 17.1% |
| Design prototypes independent review | $769.46m | 5.9% |
| Network auxiliary charging | $562.38m | 4.3% |
| Bridge special foundations deck temporary | $557.14m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $3.838bn | $13.031bn | $73.092bn |
| Water-evidence alternative capital | $3.831bn | $12.991bn | $72.763bn |
| Alternative capital / route-km | $6.10m | $20.68m | $115.82m |
| Alternative whole-life NPV | $7.834bn | $26.752bn | $145.862bn |
| Included non-water obstruction reserve | $458,231 | $3.05m | $21.38m |

6.11 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 20 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-567.38m | $-26.138bn | -0.67 |
| 50% | 150.91m | 0.50 | $75.45m | $-529.65m | $-25.486bn | -0.63 |
| 50% | 150.91m | 1.00 | $150.91m | $-454.20m | $-24.181bn | -0.54 |
| 75% | 226.36m | 0.25 | $56.59m | $-548.52m | $-25.812bn | -0.65 |
| 75% | 226.36m | 0.50 | $113.18m | $-491.93m | $-24.833bn | -0.58 |
| 75% | 226.36m | 1.00 | $226.36m | $-378.75m | $-22.876bn | -0.45 |
| 100% | 301.81m | 0.25 | $75.45m | $-529.65m | $-25.486bn | -0.63 |
| 100% | 301.81m | 0.50 | $150.91m | $-454.20m | $-24.181bn | -0.54 |
| 100% | 301.81m | 1.00 | $301.81m | $-303.30m | $-21.571bn | -0.36 |

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
| low | $2.686bn | $1.151bn | $248.39m |
| base | $9.122bn | $3.909bn | $843.42m |
| high | $51.164bn | $21.927bn | $4.731bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kinshasa.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/central-africa/DR%20Congo/Kinshasa) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `f6e02e25b95a12e5346bda1a83108b67f224f1277be4274561647441c9619d91` |
| cost_evaluation_id | `8c7e604fa05f00a31cd23dc7ad8a234282fb89386e31f41213a2f8cb3c7d1f33` |
| outline_evaluation_id | `d54c4232f1e303964aa28a5dc1162537242750725c6b05ef9949398d28dad718` |
| research_configuration_id | `482049749c8dcecfca3cef3843af5c297729351c81e8274afd4bbe231cb8a583` |
| seed_id | `86b18576ddb15d9ad1358ec9d08e4a6c8f5bc51a061164cf56a93db600afa122` |
| selected_alignment_id | `ca8cfd444e65f9333be8b15db41c12cc971f6abc9cd5a0ff405cbb347248ae3b` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `082dc1e86674451269df66e6ea08047dfb70c827a387296c998cc865c3acb11b` |
| source_result_sha256 | `6581d4f383f35ca9cd7f7765c33e3bcf74c74d667d6e83af3ede8dd3cf56a34a` |

Atlas packet `c983af6654097d8adbd9d6e0c9e8559221bc61ab8e716cc236f4db7e945ece6d`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
