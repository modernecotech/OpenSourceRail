# Karachi — railway design and city programme

**PK · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=karachi) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=karachi) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Karachi current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 20,300,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 551.34 km / 2 trackways |
| Lines / operational platform groups | 14 / 221 |
| Original access markers / separately costed access sites | 242 / 112 |
| Explicit interchange references | 58 |
| Fleet including reserve | 618 six-car trainsets |
| Train distance | 357,266 train-km/day; 130,402,150 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 50.65 | 23 | 200 | 78.1 | 49 + 8 | 4,181 | E terminal ↔ W terminal |
| line-2 | 33.18 | 17 | 200 | 60.2 | 38 + 6 | 4,181 | N terminal ↔ SW terminal |
| line-3 | 43.68 | 16 | 200 | 63.3 | 40 + 6 | 4,181 | W terminal ↔ SE terminal |
| line-4 | 41.01 | 16 | 200 | 60.7 | 39 + 6 | 4,181 | E terminal ↔ W terminal |
| line-5 | 50.06 | 15 | 200 | 69.0 | 44 + 7 | 4,181 | NE terminal ↔ S terminal |
| line-6 | 44.46 | 24 | 200 | 73.6 | 46 + 7 | 4,181 | N terminal ↔ SE terminal |
| line-7 | 37.72 | 17 | 200 | 58.5 | 37 + 6 | 4,181 | NW terminal ↔ S terminal |
| line-8 | 59.41 | 23 | 200 | 88.0 | 55 + 9 | 4,181 | NE terminal ↔ SW terminal |
| line-9 | 143.62 | 52 | 200 | 215.2 | 130 + 20 | 4,181 | Ring / closed circuit |
| line-10 | 7.53 | 3 | 200 | 12.9 | 10 + 2 | 4,181 | NE terminal ↔ N terminal |
| line-11 | 12.29 | 5 | 200 | 23.7 | 17 + 3 | 4,181 | NE terminal ↔ N terminal |
| line-12 | 11.47 | 4 | 200 | 14.5 | 11 + 2 | 4,181 | SE terminal ↔ S terminal |
| line-13 | 9.72 | 3 | 200 | 11.5 | 9 + 2 | 4,181 | NW terminal ↔ NW terminal |
| line-14 | 6.53 | 3 | 200 | 8.5 | 7 + 2 | 4,181 | E terminal ↔ E terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 111.09 | False | Unestablished |
| 800.00 | 13.33 | 444.35 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,526,121 kWh mechanical | 557.03 GWh mechanical |
| Nominal auxiliary load | 2,010,960 kWh | 734.00 GWh |
| Auxiliary supply including scenario charging losses | 2,116,800 kWh | 772.63 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 12.49 GWh |
| Total priced grid-supply scenario | See annual budget | 1,473.39 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $94.32m | $243.94m | $734.91m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 50.65 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 43.68 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 41.01 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 50.06 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 44.46 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 37.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 59.41 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 143.62 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-12 | 4 / 749.2 kW | 11.47 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 4 / 749.2 kW | 9.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 6.53 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,241.5 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,417.7 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,066.5 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,172.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,220.4 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,822.8 m | 5,554.5 m |
| line-8 | 4 | Coast stops before receiving zone | 6,642.0 m | 5,554.5 m |
| line-9 | 4 | Coast stops before receiving zone | 6,351.8 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 5,753.7 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 6,186.0 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 6,327.6 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 59.35 km |
| Bridge route | 11.94 km |
| Elevated route | 480.05 km |
| Tunnel route | 0.00 km |
| Precast span stock | 49,744 spans |
| Independent supports | 50,842 |
| Running rail | 2,209.75 rail-km / 133,049 t |
| Complete fastening sets | 3,867,057 |
| Protected at-grade crossing packages | 355 |
| Bridge runs / tunnel portals | 107 / 0 |
| Additional station track | 2,200 m |
| Access connector allowance | 1,491.7 m; actual accessible paths require survey |
| Pooled depot area | 430,872 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.82m | $9.24m | $58.19m |
| Civil production campaign | $13.81m | $68.49m | $411.41m |

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
| low | make | 20 | 174,104 | 1,293,344 | 1,724,459 |
| base | make | 47 | 422,824 | 3,382,592 | 4,510,123 |
| high | make | 128 | 1,144,112 | 9,351,872 | 12,469,163 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 114 | Unestablished | 823,878 | 411.9 |
| Vehicle production / low | 87 | 174 | Unestablished | Unestablished |
| Civil field / low | 180 | 360 | 1,868,821 | Unestablished |
| Civil other installation / low | 1,108 | 2,216 | 11,520,039 | Unestablished |
| Civil precast / low | 160 | 320 | 1,724,459 | Unestablished |
| Control room and access-site coverage / base | 228 | Unestablished | 1,872,450 | 936.2 |
| Vehicle production / base | 248 | 496 | Unestablished | Unestablished |
| Civil field / base | 668 | 1,336 | 5,871,765 | Unestablished |
| Civil other installation / base | 8,002 | 16,004 | 70,417,120 | Unestablished |
| Civil precast / base | 376 | 752 | 4,510,123 | Unestablished |
| Control room and access-site coverage / high | 456 | Unestablished | 4,493,880 | 2,246.9 |
| Vehicle production / high | 679 | 1,358 | Unestablished | Unestablished |
| Civil field / high | 2,907 | 5,814 | 16,277,077 | Unestablished |
| Civil other installation / high | 80,619 | 161,238 | 451,462,975 | Unestablished |
| Civil precast / high | 1,024 | 2,048 | 12,469,163 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 224 | 919.8 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.473bn | $8.716bn | $52.066bn |
| Installed capital / route-km | $4.49m | $15.81m | $94.44m |
| 30-year whole-life NPV | $5.107bn | $17.755bn | $100.722bn |
| Annual operating provision | $125.06m | $408.05m | $2.048bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $2.000bn | $2.000bn |
| Guideway | $757.46m | $757.46m |
| Stations power | $1.237bn | $1.237bn |
| Factory tooling | $77.73m | $77.73m |
| Construction | $3.896bn | $3.896bn |
| Land utilities depot | $506.12m | $506.12m |
| Fleet | $181.37m | $181.37m |
| Energy | $0 | $4.218bn |
| Operations | $0 | $253.29m |
| Maintenance | $0 | $2.334bn |
| Renewals | $0 | $1.902bn |
| Recovery | $61.26m | $124.82m |
| Reliability | $0 | $186.67m |
| Disposal | $0 | $80.62m |

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
| City project risk contingency | $1.743bn | 20.0% |
| Network delivered assembled fleet | $1.506bn | 17.3% |
| Design prototypes independent review | $515.39m | 5.9% |
| Bridge special foundations deck temporary | $422.11m | 4.8% |
| Repeat box beams | $366.05m | 4.2% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.473bn | $8.716bn | $52.066bn |
| Water-evidence alternative capital | $2.456bn | $8.616bn | $51.246bn |
| Alternative capital / route-km | $4.45m | $15.63m | $92.95m |
| Alternative whole-life NPV | $5.091bn | $17.655bn | $99.890bn |
| Included non-water obstruction reserve | $540,609 | $3.60m | $25.23m |

7.21 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 12 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-370.33m | $-17.103bn | -0.66 |
| 50% | 150.91m | 0.50 | $75.45m | $-332.60m | $-16.451bn | -0.59 |
| 50% | 150.91m | 1.00 | $150.91m | $-257.15m | $-15.146bn | -0.46 |
| 75% | 226.36m | 0.25 | $56.59m | $-351.46m | $-16.777bn | -0.62 |
| 75% | 226.36m | 0.50 | $113.18m | $-294.87m | $-15.798bn | -0.52 |
| 75% | 226.36m | 1.00 | $226.36m | $-181.70m | $-13.841bn | -0.32 |
| 100% | 301.81m | 0.25 | $75.45m | $-332.60m | $-16.451bn | -0.59 |
| 100% | 301.81m | 0.50 | $150.91m | $-257.15m | $-15.146bn | -0.46 |
| 100% | 301.81m | 1.00 | $301.81m | $-106.24m | $-12.536bn | -0.19 |

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
| low | $1.731bn | $741.85m | $160.05m |
| base | $6.102bn | $2.615bn | $564.16m |
| high | $36.446bn | $15.620bn | $3.370bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/karachi.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Pakistan/Karachi) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `9a64ceb34f245cdf686cfce4b058b52bbe42adb2c9c6ddbc4c7315eb820cc9e3` |
| cost_evaluation_id | `8e4809ef1492102fa9abf20f502d2eb7dd09556b90f243510ebbc2186cba3cea` |
| outline_evaluation_id | `fa18f1128aae9b8404c0df7a60b5094148008f9bd69ea5737ff699db1ef8b2c8` |
| research_configuration_id | `93153d6fba0801b9c09fe157983067d3d52d7409dcca3dd4c0653be91f6d2f28` |
| seed_id | `6b6875564967a766e6e20466e0ef9a59185e17c2a07f0d08cb90cf394474380d` |
| selected_alignment_id | `9e2814c8314c25cb13008a94482f2b8d48fd8672f7f576883ce3aa56d8165603` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `254e182cc717a0287796c457e316447e6690ed6914c6607f65299bd5a9a9f1c8` |
| source_result_sha256 | `855329b5a2a11cb9b4ab487209078bfc44c14ae0466b6b743eb2ed4a3b821c07` |

Atlas packet `123bafe6570b49e67c736504ec54e8c68a9dae9dc566d491b538065aee3135ae`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
