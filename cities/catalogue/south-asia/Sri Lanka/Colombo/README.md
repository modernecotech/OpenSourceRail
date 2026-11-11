# Colombo — railway design and city programme

**LK · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=colombo) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=colombo) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Colombo current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 5,648,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 343.43 km / 2 trackways |
| Lines / operational platform groups | 14 / 149 |
| Original access markers / separately costed access sites | 172 / 74 |
| Explicit interchange references | 44 |
| Fleet including reserve | 429 six-car trainsets |
| Train distance | 222,545 train-km/day; 81,229,037 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 26.91 | 11 | 200 | 45.8 | 30 + 5 | 4,181 | SW terminal ↔ NE terminal |
| line-2 | 29.56 | 10 | 200 | 41.1 | 27 + 5 | 4,181 | NW terminal ↔ S terminal |
| line-3 | 46.23 | 18 | 200 | 68.2 | 43 + 7 | 4,181 | N terminal ↔ SE terminal |
| line-4 | 29.66 | 10 | 200 | 41.6 | 27 + 5 | 4,181 | E terminal ↔ SW terminal |
| line-5 | 28.31 | 12 | 200 | 52.2 | 34 + 6 | 4,181 | W terminal ↔ SE terminal |
| line-6 | 30.15 | 13 | 200 | 58.1 | 37 + 6 | 4,181 | NE terminal ↔ W terminal |
| line-7 | 22.70 | 13 | 200 | 41.6 | 27 + 5 | 4,181 | W terminal ↔ SE terminal |
| line-8 | 24.95 | 11 | 200 | 37.7 | 25 + 4 | 4,181 | W terminal ↔ S terminal |
| line-9 | 67.72 | 29 | 200 | 107.4 | 66 + 10 | 4,181 | Ring / closed circuit |
| line-10 | 6.43 | 2 | 200 | 6.4 | 6 + 1 | 4,181 | SW terminal ↔ S terminal |
| line-11 | 6.56 | 2 | 200 | 6.5 | 6 + 1 | 4,181 | N terminal ↔ N terminal |
| line-12 | 6.20 | 3 | 200 | 8.8 | 8 + 2 | 4,181 | NW terminal ↔ N terminal |
| line-13 | 9.23 | 7 | 200 | 21.0 | 15 + 3 | 4,181 | N terminal ↔ NE terminal |
| line-14 | 8.85 | 8 | 200 | 21.1 | 15 + 3 | 4,181 | N terminal ↔ N terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 74.90 | False | Unestablished |
| 800.00 | 13.33 | 299.58 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 850,919 kWh mechanical | 310.59 GWh mechanical |
| Nominal auxiliary load | 1,383,480 kWh | 504.97 GWh |
| Auxiliary supply including scenario charging losses | 1,456,295 kWh | 531.55 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 9.15 GWh |
| Total priced grid-supply scenario | See annual budget | 932.14 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $60.11m | $154.33m | $457.37m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Station launch reference | 0 kg | 250 kg |
| line-13 | Station launch reference | 0 kg | 250 kg |
| line-14 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 29.56 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 46.23 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 29.66 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 24.95 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 67.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 4 / 749.2 kW | 6.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 4 / 749.2 kW | 6.56 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-13 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-14 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 5,641.2 m | 5,554.5 m |
| line-3 | 3 | Coast stops before receiving zone | 6,585.5 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,852.9 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,260.5 m | 5,554.5 m |
| line-9 | 2 | Coast stops before receiving zone | 6,486.2 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 6,426.9 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,558.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 50.11 km |
| Bridge route | 15.72 km |
| Elevated route | 277.60 km |
| Tunnel route | 0.00 km |
| Precast span stock | 30,486 spans |
| Independent supports | 32,348 |
| Running rail | 1,392.22 rail-km / 83,825 t |
| Complete fastening sets | 2,436,379 |
| Protected at-grade crossing packages | 518 |
| Bridge runs / tunnel portals | 218 / 0 |
| Additional station track | 9,240 m |
| Access connector allowance | 1,799.1 m; actual accessible paths require survey |
| Pooled depot area | 299,052 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.33m | $7.11m | $40.68m |
| Civil production campaign | $8.70m | $42.66m | $255.04m |

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
| low | make | 12 | 106,701 | 792,636 | 1,056,848 |
| base | make | 29 | 259,131 | 2,073,048 | 2,764,064 |
| high | make | 78 | 701,178 | 5,731,368 | 7,641,824 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 76 | Unestablished | 549,252 | 274.6 |
| Vehicle production / low | 61 | 122 | Unestablished | Unestablished |
| Civil field / low | 112 | 224 | 1,158,005 | Unestablished |
| Civil other installation / low | 1,097 | 2,194 | 11,401,435 | Unestablished |
| Civil precast / low | 96 | 192 | 1,056,848 | Unestablished |
| Control room and access-site coverage / base | 152 | Unestablished | 1,248,300 | 624.1 |
| Vehicle production / base | 172 | 344 | Unestablished | Unestablished |
| Civil field / base | 414 | 828 | 3,636,608 | Unestablished |
| Civil other installation / base | 7,678 | 15,356 | 67,564,887 | Unestablished |
| Civil precast / base | 232 | 464 | 2,764,064 | Unestablished |
| Control room and access-site coverage / high | 304 | Unestablished | 2,995,920 | 1,498.0 |
| Vehicle production / high | 472 | 944 | Unestablished | Unestablished |
| Civil field / high | 1,800 | 3,600 | 10,077,003 | Unestablished |
| Civil other installation / high | 74,965 | 149,930 | 419,800,280 | Unestablished |
| Civil precast / high | 624 | 1,248 | 7,641,824 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 148 | 607.7 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.832bn | $6.714bn | $40.778bn |
| Installed capital / route-km | $5.34m | $19.55m | $118.73m |
| 30-year whole-life NPV | $3.578bn | $12.805bn | $74.061bn |
| Annual operating provision | $81.44m | $268.92m | $1.368bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.260bn | $1.260bn |
| Guideway | $468.39m | $468.39m |
| Stations power | $1.131bn | $1.131bn |
| Factory tooling | $49.77m | $49.77m |
| Construction | $3.314bn | $3.314bn |
| Land utilities depot | $334.94m | $334.94m |
| Fleet | $118.23m | $118.23m |
| Energy | $0 | $2.669bn |
| Operations | $0 | $168.86m |
| Maintenance | $0 | $1.657bn |
| Renewals | $0 | $1.379bn |
| Recovery | $38.08m | $77.59m |
| Reliability | $0 | $116.28m |
| Disposal | $0 | $62.10m |

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
| City project risk contingency | $1.343bn | 20.0% |
| Network delivered assembled fleet | $1.045bn | 15.6% |
| Bridge special foundations deck temporary | $661.58m | 9.9% |
| Design prototypes independent review | $396.80m | 5.9% |
| Shared access and transfer complexes | $244.93m | 3.6% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.832bn | $6.714bn | $40.778bn |
| Water-evidence alternative capital | $1.806bn | $6.560bn | $39.524bn |
| Alternative capital / route-km | $5.26m | $19.10m | $115.08m |
| Alternative whole-life NPV | $3.552bn | $12.650bn | $72.785bn |
| Included non-water obstruction reserve | $508,463 | $3.39m | $23.73m |

6.78 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 26 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-231.20m | $-12.153bn | -0.53 |
| 50% | 150.91m | 0.50 | $75.45m | $-193.47m | $-11.500bn | -0.45 |
| 50% | 150.91m | 1.00 | $150.91m | $-118.02m | $-10.196bn | -0.27 |
| 75% | 226.36m | 0.25 | $56.59m | $-212.33m | $-11.826bn | -0.49 |
| 75% | 226.36m | 0.50 | $113.18m | $-155.74m | $-10.848bn | -0.36 |
| 75% | 226.36m | 1.00 | $226.36m | $-42.56m | $-8.891bn | -0.10 |
| 100% | 301.81m | 0.25 | $75.45m | $-193.47m | $-11.500bn | -0.45 |
| 100% | 301.81m | 0.50 | $150.91m | $-118.02m | $-10.196bn | -0.27 |
| 100% | 301.81m | 1.00 | $301.81m | $32.89m | $-7.586bn | 0.08 |

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
| low | $1.283bn | $549.70m | $118.59m |
| base | $4.700bn | $2.014bn | $434.54m |
| high | $28.544bn | $12.233bn | $2.639bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/colombo.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Sri%20Lanka/Colombo) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `f71612365fa892d78a84d316830a2f9f3bd1b910d07c8bc7165131fd557004a8` |
| cost_evaluation_id | `09910386da50b1ac0d6284a2081a435f9ab2db83c715847a0d39eec2b9371150` |
| outline_evaluation_id | `fabb94008ec58aa5a2469b887ecf479bc91d1876cabc84d44c46213478a6aa14` |
| research_configuration_id | `b8d0440d017b8f2817ae954342cd841248d18ccff19aabc1db7f12c186b1c9f2` |
| seed_id | `59c5134662d28d14cfe4c66e9df3bc92eadb3612c675346edfea3f6d24011905` |
| selected_alignment_id | `2f978ae448c604ff54b1c965453a3fed543d3392b37da1efe55c9a86503dad9d` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `ebfd511c3d893a35bfdc72da2ac1180f92cccaf4f2e44d554c10fc153a36bb8b` |
| source_result_sha256 | `ffc8b8234a36c5b57d44407dd351a5c69b02401ef5bf9f8d352a99c5fc89326c` |

Atlas packet `f76ce7f439ad1c2e58308da0c34e03810f7be504e2aa60358087d59d35918001`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
