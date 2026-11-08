# Nairobi — railway design and city programme

**KE · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=nairobi) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=nairobi) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Nairobi current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 5,700,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 578.33 km / 2 trackways |
| Lines / operational platform groups | 14 / 243 |
| Original access markers / separately costed access sites | 304 / 124 |
| Explicit interchange references | 51 |
| Fleet including reserve | 655 six-car trainsets |
| Train distance | 374,761 train-km/day; 136,787,789 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 61.72 | 19 | 200 | 86.0 | 54 + 9 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 56.33 | 38 | 200 | 102.1 | 64 + 10 | 4,181 | E terminal ↔ W terminal |
| line-3 | 54.33 | 28 | 200 | 87.6 | 55 + 9 | 4,181 | N terminal ↔ SE terminal |
| line-4 | 27.30 | 13 | 200 | 53.7 | 35 + 6 | 4,181 | E terminal ↔ W terminal |
| line-5 | 49.81 | 18 | 200 | 72.1 | 46 + 7 | 4,181 | NE terminal ↔ SW terminal |
| line-6 | 63.66 | 20 | 200 | 89.2 | 56 + 9 | 4,181 | SE terminal ↔ NW terminal |
| line-7 | 56.73 | 28 | 200 | 90.7 | 57 + 9 | 4,181 | NW terminal ↔ SE terminal |
| line-8 | 46.86 | 15 | 200 | 66.0 | 42 + 7 | 4,181 | S terminal ↔ N terminal |
| line-9 | 107.86 | 44 | 200 | 165.3 | 100 + 15 | 4,181 | Ring / closed circuit |
| line-10 | 17.91 | 6 | 200 | 23.8 | 17 + 3 | 4,181 | NE terminal ↔ E terminal |
| line-11 | 10.21 | 4 | 200 | 13.4 | 10 + 2 | 4,181 | W terminal ↔ W terminal |
| line-12 | 8.67 | 3 | 200 | 10.6 | 9 + 2 | 4,181 | SW terminal ↔ SW terminal |
| line-13 | 7.32 | 3 | 200 | 9.4 | 8 + 2 | 4,181 | W terminal ↔ W terminal |
| line-14 | 9.63 | 4 | 200 | 12.7 | 10 + 2 | 4,181 | NE terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 122.15 | False | Unestablished |
| 800.00 | 13.33 | 488.58 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,572,194 kWh mechanical | 573.85 GWh mechanical |
| Nominal auxiliary load | 2,128,140 kWh | 776.77 GWh |
| Auxiliary supply including scenario charging losses | 2,240,147 kWh | 817.65 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 13.36 GWh |
| Total priced grid-supply scenario | See annual budget | 1,541.24 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $98.56m | $255.17m | $770.34m |

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
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 61.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 56.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 54.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 49.81 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 63.66 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 56.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 46.86 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 107.86 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 4 / 749.2 kW | 17.91 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 4 / 749.2 kW | 10.21 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 4 / 749.2 kW | 8.67 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 4 / 749.2 kW | 7.32 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 9.63 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,795.9 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 6,541.0 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,800.0 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,096.2 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,453.6 m | 5,554.5 m |
| line-7 | 4 | Coast stops before receiving zone | 6,306.6 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 5,866.5 m | 5,554.5 m |
| line-9 | 6 | Coast stops before receiving zone | 6,893.2 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 5,699.1 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,380.6 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 6,361.1 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 6,366.8 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 5,713.9 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 45.66 km |
| Bridge route | 5.10 km |
| Elevated route | 527.58 km |
| Tunnel route | 0.00 km |
| Precast span stock | 54,026 spans |
| Independent supports | 55,324 |
| Running rail | 2,324.78 rail-km / 139,975 t |
| Complete fastening sets | 4,068,365 |
| Protected at-grade crossing packages | 470 |
| Bridge runs / tunnel portals | 101 / 0 |
| Additional station track | 5,720 m |
| Access connector allowance | 4,228.0 m; actual accessible paths require survey |
| Pooled depot area | 457,028 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.84m | $9.65m | $61.04m |
| Civil production campaign | $14.99m | $74.31m | $446.04m |

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
| low | make | 22 | 189,091 | 1,404,676 | 1,872,901 |
| base | make | 52 | 459,221 | 3,673,768 | 4,898,357 |
| high | make | 139 | 1,242,598 | 10,156,888 | 13,542,517 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 126 | Unestablished | 910,602 | 455.3 |
| Vehicle production / low | 92 | 184 | Unestablished | Unestablished |
| Civil field / low | 196 | 392 | 2,030,816 | Unestablished |
| Civil other installation / low | 1,115 | 2,230 | 11,586,909 | Unestablished |
| Civil precast / low | 176 | 352 | 1,872,901 | Unestablished |
| Control room and access-site coverage / base | 252 | Unestablished | 2,069,550 | 1,034.8 |
| Vehicle production / base | 262 | 524 | Unestablished | Unestablished |
| Civil field / base | 726 | 1,452 | 6,380,587 | Unestablished |
| Civil other installation / base | 7,908 | 15,816 | 69,582,343 | Unestablished |
| Civil precast / base | 416 | 832 | 4,898,357 | Unestablished |
| Control room and access-site coverage / high | 504 | Unestablished | 4,966,920 | 2,483.5 |
| Vehicle production / high | 720 | 1,440 | Unestablished | Unestablished |
| Civil field / high | 3,159 | 6,318 | 17,687,221 | Unestablished |
| Civil other installation / high | 78,693 | 157,386 | 440,679,797 | Unestablished |
| Civil precast / high | 1,112 | 2,224 | 13,542,517 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 248 | 1,018.4 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.610bn | $9.061bn | $53.462bn |
| Installed capital / route-km | $4.51m | $15.67m | $92.44m |
| 30-year whole-life NPV | $5.398bn | $18.648bn | $105.280bn |
| Annual operating provision | $131.75m | $431.65m | $2.179bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $2.155bn | $2.155bn |
| Guideway | $814.38m | $814.38m |
| Stations power | $1.334bn | $1.334bn |
| Factory tooling | $83.96m | $83.96m |
| Construction | $3.882bn | $3.882bn |
| Land utilities depot | $533.25m | $533.25m |
| Fleet | $194.35m | $194.35m |
| Energy | $0 | $4.412bn |
| Operations | $0 | $279.95m |
| Maintenance | $0 | $2.509bn |
| Renewals | $0 | $2.039bn |
| Recovery | $64.57m | $131.56m |
| Reliability | $0 | $195.81m |
| Disposal | $0 | $83.81m |

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
| City project risk contingency | $1.812bn | 20.0% |
| Network delivered assembled fleet | $1.596bn | 17.6% |
| Design prototypes independent review | $535.71m | 5.9% |
| Repeat box beams | $397.56m | 4.4% |
| Shared access and transfer complexes | $387.69m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.610bn | $9.061bn | $53.462bn |
| Water-evidence alternative capital | $2.605bn | $9.031bn | $53.220bn |
| Alternative capital / route-km | $4.51m | $15.62m | $92.02m |
| Alternative whole-life NPV | $5.394bn | $18.619bn | $105.039bn |
| Included non-water obstruction reserve | $215,927 | $1.44m | $10.08m |

2.88 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 22 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-393.93m | $-17.995bn | -0.67 |
| 50% | 150.91m | 0.50 | $75.45m | $-356.20m | $-17.343bn | -0.61 |
| 50% | 150.91m | 1.00 | $150.91m | $-280.75m | $-16.038bn | -0.48 |
| 75% | 226.36m | 0.25 | $56.59m | $-375.06m | $-17.669bn | -0.64 |
| 75% | 226.36m | 0.50 | $113.18m | $-318.47m | $-16.691bn | -0.54 |
| 75% | 226.36m | 1.00 | $226.36m | $-205.29m | $-14.734bn | -0.35 |
| 100% | 301.81m | 0.25 | $75.45m | $-356.20m | $-17.343bn | -0.61 |
| 100% | 301.81m | 0.50 | $150.91m | $-280.75m | $-16.038bn | -0.48 |
| 100% | 301.81m | 1.00 | $301.81m | $-129.84m | $-13.429bn | -0.22 |

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
| low | $1.827bn | $783.05m | $168.94m |
| base | $6.343bn | $2.718bn | $586.46m |
| high | $37.423bn | $16.039bn | $3.460bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/nairobi.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Kenya/Nairobi) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `c2a038d90d063b8ae8a9459fceb3014b1ab24898211d4c049ca8c7ed03dd6380` |
| cost_evaluation_id | `37c6f9b6d25a89feca4374a0415be450d75fd3ac0505097cf44fa23bbdbb55de` |
| outline_evaluation_id | `aaef0bdf47aa176dfec0c1fa5b2119c64054bd791f8297c5783747a1181005f8` |
| research_configuration_id | `a5110ead1ba47a6f26f1ba8ce6f5afc0bcc3bff1c9f4ac0e880328c0b88d1fcf` |
| seed_id | `85b0d2d1d1c7eab6c778fec96980bb50349e9e8c4cda4834faabf830f5995b66` |
| selected_alignment_id | `6a739403a0d8c19a6445fad9db2453d817f24a09291e26df15a9f22dcf480021` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `6478a2d2f42aa8047b35b88a938eb9c357b31d942382c11cc78a289828023e9c` |
| source_result_sha256 | `5c720f49d4406a94f7df5acac8f840e1dc9ae23b5ce7a2274ae83f6e3aa5d7bd` |

Atlas packet `1f2f2b57dc95ea8cb37c953bdf0eeac863fc6fc29dc0bb0d1a77b7c921334b85`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
