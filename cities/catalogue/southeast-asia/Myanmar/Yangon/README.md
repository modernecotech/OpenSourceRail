# Yangon — railway design and city programme

**MM · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=yangon) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=yangon) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Yangon current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 5,200,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 542.01 km / 2 trackways |
| Lines / operational platform groups | 14 / 228 |
| Original access markers / separately costed access sites | 252 / 111 |
| Explicit interchange references | 63 |
| Fleet including reserve | 636 six-car trainsets |
| Train distance | 351,220 train-km/day; 128,195,269 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 44.91 | 17 | 200 | 64.7 | 41 + 7 | 4,181 | N terminal ↔ S terminal |
| line-2 | 40.38 | 15 | 200 | 57.9 | 37 + 6 | 4,181 | S terminal ↔ N terminal |
| line-3 | 59.42 | 28 | 200 | 107.2 | 67 + 11 | 4,181 | SE terminal ↔ W terminal |
| line-4 | 52.07 | 17 | 200 | 72.7 | 46 + 7 | 4,181 | NE terminal ↔ SW terminal |
| line-5 | 48.46 | 24 | 200 | 78.3 | 49 + 8 | 4,181 | SE terminal ↔ NW terminal |
| line-6 | 38.55 | 11 | 200 | 51.1 | 33 + 5 | 4,181 | S terminal ↔ E terminal |
| line-7 | 48.34 | 20 | 200 | 86.5 | 54 + 9 | 4,181 | W terminal ↔ E terminal |
| line-8 | 56.19 | 28 | 200 | 105.0 | 65 + 10 | 4,181 | NW terminal ↔ SE terminal |
| line-9 | 102.56 | 47 | 200 | 163.3 | 98 + 15 | 4,181 | Ring / closed circuit |
| line-10 | 8.31 | 4 | 200 | 17.2 | 13 + 2 | 4,181 | NW terminal ↔ NW terminal |
| line-11 | 7.61 | 4 | 200 | 10.8 | 9 + 2 | 4,181 | NE terminal ↔ N terminal |
| line-12 | 12.28 | 5 | 200 | 17.3 | 13 + 2 | 4,181 | SW terminal ↔ W terminal |
| line-13 | 15.10 | 5 | 200 | 20.1 | 14 + 3 | 4,181 | NW terminal ↔ W terminal |
| line-14 | 7.84 | 3 | 200 | 10.0 | 8 + 2 | 4,181 | E terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 114.61 | False | Unestablished |
| 800.00 | 13.33 | 458.42 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,426,925 kWh mechanical | 520.83 GWh mechanical |
| Nominal auxiliary load | 2,067,660 kWh | 754.70 GWh |
| Auxiliary supply including scenario charging losses | 2,176,484 kWh | 794.42 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 12.93 GWh |
| Total priced grid-supply scenario | See annual budget | 1,457.46 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $93.80m | $241.30m | $718.57m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 44.91 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 40.38 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 52.07 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 48.46 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 38.55 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 102.56 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 4 / 749.2 kW | 7.61 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 4 / 749.2 kW | 12.28 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 4 / 749.2 kW | 15.10 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 7.84 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,913.7 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,502.5 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 5,894.3 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 5,809.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,442.9 m | 5,554.5 m |
| line-9 | 2 | Coast stops before receiving zone | 6,056.5 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,420.1 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 6,289.1 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 6,942.3 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 6,795.4 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 87.67 km |
| Bridge route | 36.67 km |
| Elevated route | 417.67 km |
| Tunnel route | 0.00 km |
| Precast span stock | 46,010 spans |
| Independent supports | 47,318 |
| Running rail | 2,171.54 rail-km / 130,749 t |
| Complete fastening sets | 3,800,203 |
| Protected at-grade crossing packages | 289 |
| Bridge runs / tunnel portals | 198 / 0 |
| Additional station track | 1,760 m |
| Access connector allowance | 2,063.0 m; actual accessible paths require survey |
| Pooled depot area | 443,664 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.83m | $9.43m | $59.61m |
| Civil production campaign | $12.81m | $63.47m | $380.81m |

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
| low | make | 18 | 161,035 | 1,196,260 | 1,595,013 |
| base | make | 44 | 391,085 | 3,128,680 | 4,171,573 |
| high | make | 118 | 1,058,230 | 8,649,880 | 11,533,173 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 113 | Unestablished | 816,651 | 408.3 |
| Vehicle production / low | 90 | 180 | Unestablished | Unestablished |
| Civil field / low | 167 | 334 | 1,731,659 | Unestablished |
| Civil other installation / low | 1,399 | 2,798 | 14,545,533 | Unestablished |
| Civil precast / low | 144 | 288 | 1,595,013 | Unestablished |
| Control room and access-site coverage / base | 226 | Unestablished | 1,856,025 | 928.0 |
| Vehicle production / base | 255 | 510 | Unestablished | Unestablished |
| Civil field / base | 619 | 1,238 | 5,440,363 | Unestablished |
| Civil other installation / base | 9,981 | 19,962 | 87,831,157 | Unestablished |
| Civil precast / base | 352 | 704 | 4,171,573 | Unestablished |
| Control room and access-site coverage / high | 452 | Unestablished | 4,454,460 | 2,227.2 |
| Vehicle production / high | 699 | 1,398 | Unestablished | Unestablished |
| Civil field / high | 2,693 | 5,386 | 15,080,203 | Unestablished |
| Civil other installation / high | 99,972 | 199,944 | 559,841,920 | Unestablished |
| Civil precast / high | 944 | 1,888 | 11,533,173 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 222 | 911.6 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.592bn | $9.409bn | $57.244bn |
| Installed capital / route-km | $4.78m | $17.36m | $105.61m |
| 30-year whole-life NPV | $5.236bn | $18.535bn | $106.510bn |
| Annual operating provision | $124.87m | $408.27m | $2.052bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.921bn | $1.921bn |
| Guideway | $714.65m | $714.65m |
| Stations power | $1.462bn | $1.462bn |
| Factory tooling | $72.90m | $72.90m |
| Construction | $4.491bn | $4.491bn |
| Land utilities depot | $507.14m | $507.14m |
| Fleet | $178.46m | $178.46m |
| Energy | $0 | $4.173bn |
| Operations | $0 | $251.07m |
| Maintenance | $0 | $2.389bn |
| Renewals | $0 | $1.979bn |
| Recovery | $61.26m | $124.82m |
| Reliability | $0 | $183.51m |
| Disposal | $0 | $87.03m |

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
| City project risk contingency | $1.882bn | 20.0% |
| Network delivered assembled fleet | $1.550bn | 16.5% |
| Bridge special foundations deck temporary | $1.096bn | 11.6% |
| Design prototypes independent review | $556.21m | 5.9% |
| Shared access and transfer complexes | $364.39m | 3.9% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.592bn | $9.409bn | $57.244bn |
| Water-evidence alternative capital | $2.533bn | $9.062bn | $54.420bn |
| Alternative capital / route-km | $4.67m | $16.72m | $100.41m |
| Alternative whole-life NPV | $5.177bn | $18.186bn | $103.629bn |
| Included non-water obstruction reserve | $1.26m | $8.42m | $58.93m |

16.84 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 118 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-370.55m | $-17.882bn | -0.61 |
| 50% | 150.91m | 0.50 | $75.45m | $-332.82m | $-17.230bn | -0.55 |
| 50% | 150.91m | 1.00 | $150.91m | $-257.37m | $-15.925bn | -0.42 |
| 75% | 226.36m | 0.25 | $56.59m | $-351.69m | $-17.556bn | -0.58 |
| 75% | 226.36m | 0.50 | $113.18m | $-295.10m | $-16.578bn | -0.48 |
| 75% | 226.36m | 1.00 | $226.36m | $-181.92m | $-14.621bn | -0.30 |
| 100% | 301.81m | 0.25 | $75.45m | $-332.82m | $-17.230bn | -0.55 |
| 100% | 301.81m | 0.50 | $150.91m | $-257.37m | $-15.925bn | -0.42 |
| 100% | 301.81m | 1.00 | $301.81m | $-106.46m | $-13.316bn | -0.17 |

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
| low | $1.814bn | $777.57m | $167.76m |
| base | $6.586bn | $2.823bn | $608.97m |
| high | $40.071bn | $17.173bn | $3.705bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/yangon.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/southeast-asia/Myanmar/Yangon) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `9aa2ba26b8ac837722db6cbbc58a7ed5300c5dc506df48d881a613e102615111` |
| cost_evaluation_id | `82cc5bcac4e8e86967013e99954d674f17ad65cbcac7101922e570dfd3ffa6fe` |
| outline_evaluation_id | `cbf0dc376c78b9fd897bbb5ec7c06b9b07107b00ce4452eddc71780078e6e02f` |
| research_configuration_id | `63dc7804318b8bf05157680cb2f3fcf3e454ad7f74333ff80f9fc56c09bd965a` |
| seed_id | `728f80575f32081a1a21c4eec29355a71cb10d7a63329138314f07fe7f2e1144` |
| selected_alignment_id | `4c584a26e8126598fea18305fd441a98cff8e72e20587e432bf62d73443335be` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `f0a4529e859560ec19400c3c45078e8c3b2192c1ab6b6d0a90a0309882ceb158` |
| source_result_sha256 | `e6071f34bae346ff9336f52341ef471ece91f8dfa9c27786cc2e50d233ed4518` |

Atlas packet `3aad4889165925930832bef06592d7a4c6705db9c9e6d1e7dc5fbf9dea25f40b`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
