# Baghdad — railway design and city programme

**IQ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=baghdad) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=baghdad) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Baghdad current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 9,780,429 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 494.43 km / 2 trackways |
| Lines / operational platform groups | 14 / 157 |
| Original access markers / separately costed access sites | 159 / 110 |
| Explicit interchange references | 45 |
| Fleet including reserve | 533 six-car trainsets |
| Train distance | 320,391 train-km/day; 116,942,834 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 48.41 | 17 | 200 | 80.9 | 51 + 8 | 4,181 | S terminal ↔ N terminal |
| line-2 | 49.66 | 14 | 200 | 66.9 | 42 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-3 | 47.53 | 16 | 200 | 67.0 | 43 + 7 | 4,181 | S terminal ↔ NE terminal |
| line-4 | 38.73 | 12 | 200 | 52.8 | 34 + 6 | 4,181 | NW terminal ↔ E terminal |
| line-5 | 45.42 | 15 | 200 | 63.3 | 40 + 6 | 4,181 | W terminal ↔ E terminal |
| line-6 | 50.00 | 16 | 200 | 69.3 | 44 + 7 | 4,181 | SW terminal ↔ NE terminal |
| line-7 | 38.07 | 13 | 200 | 54.1 | 35 + 6 | 4,181 | E terminal ↔ SW terminal |
| line-8 | 45.49 | 15 | 200 | 75.5 | 48 + 8 | 4,181 | SE terminal ↔ W terminal |
| line-9 | 96.79 | 26 | 200 | 135.1 | 82 + 13 | 4,181 | Ring / closed circuit |
| line-10 | 6.80 | 3 | 200 | 8.8 | 8 + 2 | 4,181 | N terminal ↔ NE terminal |
| line-11 | 6.88 | 2 | 200 | 6.8 | 6 + 1 | 4,181 | NE terminal ↔ N terminal |
| line-12 | 6.58 | 3 | 200 | 9.4 | 8 + 2 | 4,181 | NW terminal ↔ W terminal |
| line-13 | 8.04 | 3 | 200 | 12.8 | 10 + 2 | 4,181 | SW terminal ↔ W terminal |
| line-14 | 6.04 | 2 | 200 | 6.1 | 6 + 1 | 4,181 | NE terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 78.92 | False | Unestablished |
| 800.00 | 13.33 | 315.67 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,242,020 kWh mechanical | 453.34 GWh mechanical |
| Nominal auxiliary load | 1,727,460 kWh | 630.52 GWh |
| Auxiliary supply including scenario charging losses | 1,818,379 kWh | 663.71 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 11.04 GWh |
| Total priced grid-supply scenario | See annual budget | 1,242.12 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $79.60m | $205.65m | $617.77m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Station launch reference | 0 kg | 250 kg |
| line-13 | Station launch reference | 0 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 49.66 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 47.53 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 38.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 45.42 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 50.00 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 38.07 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 96.79 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 4 / 749.2 kW | 6.80 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 4 / 749.2 kW | 6.88 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-13 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-14 | 4 / 749.2 kW | 6.04 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 5,809.2 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,920.9 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,134.8 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,125.8 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,950.2 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,569.5 m | 5,554.5 m |
| line-9 | 5 | Coast stops before receiving zone | 6,932.9 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 5,697.5 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,879.6 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 6,041.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 188.70 km |
| Bridge route | 31.09 km |
| Elevated route | 274.64 km |
| Tunnel route | 0.00 km |
| Precast span stock | 31,446 spans |
| Independent supports | 33,000 |
| Running rail | 1,977.72 rail-km / 119,079 t |
| Complete fastening sets | 3,461,018 |
| Protected at-grade crossing packages | 497 |
| Bridge runs / tunnel portals | 216 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 199.9 m; actual accessible paths require survey |
| Pooled depot area | 372,268 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.58m | $8.27m | $49.97m |
| Civil production campaign | $8.96m | $44.00m | $263.36m |

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
| low | make | 13 | 110,061 | 817,596 | 1,090,128 |
| base | make | 30 | 267,291 | 2,138,328 | 2,851,104 |
| high | make | 81 | 723,258 | 5,911,848 | 7,882,464 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 112 | Unestablished | 809,424 | 404.7 |
| Vehicle production / low | 75 | 150 | Unestablished | Unestablished |
| Civil field / low | 115 | 230 | 1,190,560 | Unestablished |
| Civil other installation / low | 1,251 | 2,502 | 13,006,736 | Unestablished |
| Civil precast / low | 104 | 208 | 1,090,128 | Unestablished |
| Control room and access-site coverage / base | 224 | Unestablished | 1,839,600 | 919.8 |
| Vehicle production / base | 214 | 428 | Unestablished | Unestablished |
| Civil field / base | 425 | 850 | 3,739,392 | Unestablished |
| Civil other installation / base | 9,626 | 19,252 | 84,707,005 | Unestablished |
| Civil precast / base | 240 | 480 | 2,851,104 | Unestablished |
| Control room and access-site coverage / high | 448 | Unestablished | 4,415,040 | 2,207.5 |
| Vehicle production / high | 586 | 1,172 | Unestablished | Unestablished |
| Civil field / high | 1,851 | 3,702 | 10,363,040 | Unestablished |
| Civil other installation / high | 101,024 | 202,048 | 565,731,731 | Unestablished |
| Civil precast / high | 648 | 1,296 | 7,882,464 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 220 | 903.4 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.224bn | $8.355bn | $52.030bn |
| Installed capital / route-km | $4.50m | $16.90m | $105.23m |
| 30-year whole-life NPV | $4.443bn | $16.026bn | $93.901bn |
| Annual operating provision | $105.50m | $344.91m | $1.740bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.661bn | $1.661bn |
| Guideway | $542.74m | $542.74m |
| Stations power | $1.081bn | $1.081bn |
| Factory tooling | $52.28m | $52.28m |
| Construction | $4.365bn | $4.365bn |
| Land utilities depot | $446.10m | $446.10m |
| Fleet | $152.59m | $152.59m |
| Energy | $0 | $3.556bn |
| Operations | $0 | $248.85m |
| Maintenance | $0 | $1.935bn |
| Renewals | $0 | $1.630bn |
| Recovery | $54.64m | $111.32m |
| Reliability | $0 | $167.40m |
| Disposal | $0 | $77.28m |

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
| City project risk contingency | $1.671bn | 20.0% |
| Network delivered assembled fleet | $1.299bn | 15.5% |
| Bridge special foundations deck temporary | $1.017bn | 12.2% |
| Design prototypes independent review | $494.08m | 5.9% |
| Shared access and transfer complexes | $343.68m | 4.1% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.224bn | $8.355bn | $52.030bn |
| Water-evidence alternative capital | $2.099bn | $7.629bn | $46.137bn |
| Alternative capital / route-km | $4.25m | $15.43m | $93.31m |
| Alternative whole-life NPV | $4.317bn | $15.292bn | $87.853bn |
| Included non-water obstruction reserve | $1.33m | $8.86m | $62.02m |

17.72 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 32 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-307.19m | $-15.374bn | -0.57 |
| 50% | 150.91m | 0.50 | $75.45m | $-269.46m | $-14.721bn | -0.50 |
| 50% | 150.91m | 1.00 | $150.91m | $-194.01m | $-13.416bn | -0.36 |
| 75% | 226.36m | 0.25 | $56.59m | $-288.32m | $-15.047bn | -0.53 |
| 75% | 226.36m | 0.50 | $113.18m | $-231.73m | $-14.069bn | -0.43 |
| 75% | 226.36m | 1.00 | $226.36m | $-118.55m | $-12.112bn | -0.22 |
| 100% | 301.81m | 0.25 | $75.45m | $-269.46m | $-14.721bn | -0.50 |
| 100% | 301.81m | 0.50 | $150.91m | $-194.01m | $-13.416bn | -0.36 |
| 100% | 301.81m | 1.00 | $301.81m | $-43.10m | $-10.807bn | -0.08 |

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
| low | $1.557bn | $667.21m | $143.95m |
| base | $5.848bn | $2.506bn | $540.74m |
| high | $36.421bn | $15.609bn | $3.368bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/baghdad.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Baghdad) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `e1e98bb414daa1ae18bf49a6ef1c491e885c11e8c05140b3ba40d3eb6b3f12d5` |
| cost_evaluation_id | `bebebf7c846f67e4456ca4aa559b17f61ff2eff018bac0edf8e20a603d00ceca` |
| outline_evaluation_id | `f1715c1fc8212bb0d107a0e06cf8fbb8fbada7fe7889b5aa8182d8e21c585561` |
| research_configuration_id | `5bfa6163f630d7b15e8aed4734369cdc0c8261ea00191185dd5ccbd45e2015d2` |
| seed_id | `53f0cc845e2e67e8c164885829e3d4e3cf4e782ba08a02d92fdf75453e3dc649` |
| selected_alignment_id | `e2ed6966088ef33bdfa6086eefcd37ecb7d6becf015784fc442221ea5144a500` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `3dea297fcdd28329a3bebf3cece2d7f9a558414c3ad0ba1ca8c7fa0cd63c88e3` |
| source_result_sha256 | `40a9872d77c1764acfd98ac37b5a5694ee5bc8e57d4b69bb96e9010f7dd7851c` |

Atlas packet `8c40db24d5e93ad0ee68d16da582828547dd444048338cc403176fd7d16d6b1a`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
