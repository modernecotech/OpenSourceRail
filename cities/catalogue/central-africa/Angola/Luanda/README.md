# Luanda — railway design and city programme

**AO · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=luanda) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=luanda) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Luanda current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 9,085,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 444.26 km / 2 trackways |
| Lines / operational platform groups | 14 / 200 |
| Original access markers / separately costed access sites | 234 / 109 |
| Explicit interchange references | 50 |
| Fleet including reserve | 539 six-car trainsets |
| Train distance | 287,879 train-km/day; 105,075,719 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 62.77 | 33 | 200 | 102.3 | 64 + 10 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 31.19 | 10 | 200 | 52.8 | 34 + 6 | 4,181 | W terminal ↔ N terminal |
| line-3 | 45.81 | 22 | 200 | 72.0 | 46 + 7 | 4,181 | SW terminal ↔ NE terminal |
| line-4 | 55.81 | 25 | 200 | 85.2 | 53 + 8 | 4,181 | NW terminal ↔ SE terminal |
| line-5 | 42.02 | 17 | 200 | 73.6 | 46 + 7 | 4,181 | SE terminal ↔ W terminal |
| line-6 | 31.61 | 12 | 200 | 45.6 | 30 + 5 | 4,181 | N terminal ↔ S terminal |
| line-7 | 34.42 | 16 | 200 | 60.8 | 39 + 6 | 4,181 | E terminal ↔ NW terminal |
| line-8 | 33.02 | 19 | 200 | 64.4 | 41 + 7 | 4,181 | NE terminal ↔ W terminal |
| line-9 | 62.65 | 21 | 200 | 91.4 | 56 + 9 | 4,181 | Ring / closed circuit |
| line-10 | 8.93 | 10 | 200 | 21.3 | 15 + 3 | 4,181 | NE terminal ↔ N terminal |
| line-11 | 7.98 | 5 | 200 | 12.5 | 10 + 2 | 4,181 | SE terminal ↔ N terminal |
| line-12 | 6.11 | 2 | 200 | 6.1 | 6 + 1 | 4,181 | SW terminal ↔ SW terminal |
| line-13 | 15.34 | 5 | 200 | 19.9 | 14 + 3 | 4,181 | S terminal ↔ W terminal |
| line-14 | 6.60 | 3 | 200 | 10.5 | 9 + 2 | 4,181 | SE terminal ↔ E terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 100.53 | False | Unestablished |
| 800.00 | 13.33 | 402.12 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,164,110 kWh mechanical | 424.90 GWh mechanical |
| Nominal auxiliary load | 1,750,140 kWh | 638.80 GWh |
| Auxiliary supply including scenario charging losses | 1,842,253 kWh | 672.42 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 11.04 GWh |
| Total priced grid-supply scenario | See annual budget | 1,219.67 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $78.44m | $201.93m | $601.81m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 62.77 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 45.81 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 55.81 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 31.61 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 62.65 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 4 / 749.2 kW | 7.98 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 4 / 749.2 kW | 6.11 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 4 / 749.2 kW | 15.34 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,356.0 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,206.8 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,597.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,559.3 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 5,613.1 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,353.6 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 6,107.0 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 6,719.2 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 47.23 km |
| Bridge route | 0.69 km |
| Elevated route | 396.34 km |
| Tunnel route | 0.00 km |
| Precast span stock | 39,818 spans |
| Independent supports | 40,210 |
| Running rail | 1,777.03 rail-km / 106,995 t |
| Complete fastening sets | 3,109,801 |
| Protected at-grade crossing packages | 174 |
| Bridge runs / tunnel portals | 27 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 2,565.8 m; actual accessible paths require survey |
| Pooled depot area | 375,700 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.58m | $8.27m | $50.74m |
| Civil production campaign | $11.18m | $55.17m | $330.63m |

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
| low | make | 16 | 139,363 | 1,035,268 | 1,380,357 |
| base | make | 38 | 338,453 | 2,707,624 | 3,610,165 |
| high | make | 102 | 915,814 | 7,485,784 | 9,981,045 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 111 | Unestablished | 802,197 | 401.1 |
| Vehicle production / low | 76 | 152 | Unestablished | Unestablished |
| Civil field / low | 144 | 288 | 1,490,720 | Unestablished |
| Civil other installation / low | 966 | 1,932 | 10,043,780 | Unestablished |
| Civil precast / low | 128 | 256 | 1,380,357 | Unestablished |
| Control room and access-site coverage / base | 222 | Unestablished | 1,823,175 | 911.6 |
| Vehicle production / base | 216 | 432 | Unestablished | Unestablished |
| Civil field / base | 533 | 1,066 | 4,684,523 | Unestablished |
| Civil other installation / base | 6,278 | 12,556 | 55,246,187 | Unestablished |
| Civil precast / base | 304 | 608 | 3,610,165 | Unestablished |
| Control room and access-site coverage / high | 444 | Unestablished | 4,375,620 | 2,187.8 |
| Vehicle production / high | 592 | 1,184 | Unestablished | Unestablished |
| Civil field / high | 2,320 | 4,640 | 12,987,573 | Unestablished |
| Civil other installation / high | 58,855 | 117,710 | 329,584,047 | Unestablished |
| Civil precast / high | 816 | 1,632 | 9,981,045 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 218 | 895.2 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.012bn | $6.943bn | $40.309bn |
| Installed capital / route-km | $4.53m | $15.63m | $90.73m |
| 30-year whole-life NPV | $4.241bn | $14.674bn | $82.561bn |
| Annual operating provision | $105.15m | $345.56m | $1.758bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.611bn | $1.611bn |
| Guideway | $607.22m | $607.22m |
| Stations power | $1.280bn | $1.280bn |
| Factory tooling | $63.44m | $63.44m |
| Construction | $2.757bn | $2.757bn |
| Land utilities depot | $424.01m | $424.01m |
| Fleet | $150.22m | $150.22m |
| Energy | $0 | $3.492bn |
| Operations | $0 | $246.63m |
| Maintenance | $0 | $2.035bn |
| Renewals | $0 | $1.691bn |
| Recovery | $49.67m | $101.20m |
| Reliability | $0 | $150.41m |
| Disposal | $0 | $64.22m |

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
| City project risk contingency | $1.389bn | 20.0% |
| Network delivered assembled fleet | $1.313bn | 18.9% |
| Design prototypes independent review | $410.26m | 5.9% |
| Shared access and transfer complexes | $345.96m | 5.0% |
| Repeat box beams | $293.01m | 4.2% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.012bn | $6.943bn | $40.309bn |
| Water-evidence alternative capital | $2.024bn | $7.012bn | $40.866bn |
| Alternative capital / route-km | $4.56m | $15.78m | $91.99m |
| Alternative whole-life NPV | $4.253bn | $14.744bn | $83.137bn |
| Included non-water obstruction reserve | $35,261 | $235,074 | $1.65m |

0.47 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 25 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-307.83m | $-14.022bn | -0.69 |
| 50% | 150.91m | 0.50 | $75.45m | $-270.11m | $-13.369bn | -0.60 |
| 50% | 150.91m | 1.00 | $150.91m | $-194.65m | $-12.065bn | -0.43 |
| 75% | 226.36m | 0.25 | $56.59m | $-288.97m | $-13.695bn | -0.64 |
| 75% | 226.36m | 0.50 | $113.18m | $-232.38m | $-12.717bn | -0.52 |
| 75% | 226.36m | 1.00 | $226.36m | $-119.20m | $-10.760bn | -0.27 |
| 100% | 301.81m | 0.25 | $75.45m | $-270.11m | $-13.369bn | -0.60 |
| 100% | 301.81m | 0.50 | $150.91m | $-194.65m | $-12.065bn | -0.43 |
| 100% | 301.81m | 1.00 | $301.81m | $-43.75m | $-9.455bn | -0.10 |

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
| low | $1.408bn | $603.57m | $130.22m |
| base | $4.860bn | $2.083bn | $449.38m |
| high | $28.217bn | $12.093bn | $2.609bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/luanda.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/central-africa/Angola/Luanda) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `28ef15d526953ba6c257f5d2d727170c6d21d47e61f29bc1612d526fe36bbe28` |
| cost_evaluation_id | `ce25c83f6825694a069bcac7ba95e80b3ec819abf5355d5670772cc4a890bad0` |
| outline_evaluation_id | `78e6637912adad1709bbfbd61e726852ba52938ae76a4684e0baf01ab3016819` |
| research_configuration_id | `b8549253c00e1861752bc17db7e8454a88c000a6189b4f989887460775d2c60a` |
| seed_id | `4fc07bfb95c6fec2f035a9f973a822f55adcdf7b802133383d8a05d46b11dd8f` |
| selected_alignment_id | `94123c2439dab12914f2e6158c9b085f2ff205c59c3f3f7640886f09ae87ef24` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `76fc85c8d34395b708fac271b88853b334fcae037fa0b1d69851db50ebd9739d` |
| source_result_sha256 | `01095923e200d739edf18294d60a3b2e922d1db7445cb35f26a637bf48552af3` |

Atlas packet `13806bd42eabb5a18b97cd7fd54a90fb0c1e5084aa1d0ea9db178c3b9b9073ac`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
