# Jeddah — railway design and city programme

**SA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=jeddah) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=jeddah) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Jeddah current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 4,700,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 408.32 km / 2 trackways |
| Lines / operational platform groups | 14 / 148 |
| Original access markers / separately costed access sites | 159 / 88 |
| Explicit interchange references | 38 |
| Fleet including reserve | 462 six-car trainsets |
| Train distance | 264,595 train-km/day; 96,576,996 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 47.30 | 16 | 200 | 66.3 | 42 + 7 | 4,181 | S terminal ↔ NW terminal |
| line-2 | 26.90 | 9 | 200 | 38.0 | 25 + 4 | 4,181 | S terminal ↔ NW terminal |
| line-3 | 49.24 | 18 | 200 | 70.3 | 44 + 7 | 4,181 | N terminal ↔ SE terminal |
| line-4 | 44.46 | 13 | 200 | 60.7 | 39 + 6 | 4,181 | N terminal ↔ S terminal |
| line-5 | 33.16 | 12 | 200 | 46.9 | 30 + 5 | 4,181 | E terminal ↔ W terminal |
| line-6 | 33.87 | 11 | 200 | 62.3 | 40 + 6 | 4,181 | SE terminal ↔ SW terminal |
| line-7 | 29.65 | 11 | 200 | 49.8 | 32 + 5 | 4,181 | NE terminal ↔ S terminal |
| line-8 | 29.15 | 13 | 200 | 56.8 | 36 + 6 | 4,181 | NE terminal ↔ SW terminal |
| line-9 | 74.16 | 27 | 200 | 109.9 | 66 + 10 | 4,181 | Ring / closed circuit |
| line-10 | 7.35 | 6 | 200 | 12.8 | 10 + 2 | 4,181 | N terminal ↔ NW terminal |
| line-11 | 6.17 | 2 | 200 | 6.2 | 6 + 1 | 4,181 | SE terminal ↔ SE terminal |
| line-12 | 14.21 | 5 | 200 | 19.4 | 14 + 3 | 4,181 | NW terminal ↔ N terminal |
| line-13 | 6.32 | 3 | 200 | 8.3 | 7 + 2 | 4,181 | S terminal ↔ S terminal |
| line-14 | 6.38 | 2 | 200 | 6.4 | 6 + 1 | 4,181 | NW terminal ↔ W terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 74.39 | False | Unestablished |
| 800.00 | 13.33 | 297.57 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,049,417 kWh mechanical | 383.04 GWh mechanical |
| Nominal auxiliary load | 1,500,660 kWh | 547.74 GWh |
| Auxiliary supply including scenario charging losses | 1,579,642 kWh | 576.57 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 9.44 GWh |
| Total priced grid-supply scenario | See annual budget | 1,064.45 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $68.29m | $176.23m | $528.20m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 47.30 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 26.90 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 49.24 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 44.46 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 33.16 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 74.16 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 4 / 749.2 kW | 7.35 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 4 / 749.2 kW | 6.17 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 4 / 749.2 kW | 14.21 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 4 / 749.2 kW | 6.32 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 6.38 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,695.0 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 6,582.1 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,013.6 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,786.3 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,276.3 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 5,870.0 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 6,247.1 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,170.0 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 5,775.1 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 6,042.5 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 6,375.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 48.28 km |
| Bridge route | 5.05 km |
| Elevated route | 354.99 km |
| Tunnel route | 0.00 km |
| Precast span stock | 36,524 spans |
| Independent supports | 37,074 |
| Running rail | 1,644.74 rail-km / 99,030 t |
| Complete fastening sets | 2,878,295 |
| Protected at-grade crossing packages | 224 |
| Bridge runs / tunnel portals | 22 / 0 |
| Additional station track | 5,720 m |
| Access connector allowance | 918.1 m; actual accessible paths require survey |
| Pooled depot area | 322,920 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.41m | $7.33m | $44.87m |
| Civil production campaign | $10.31m | $50.80m | $304.36m |

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
| low | make | 15 | 127,834 | 949,624 | 1,266,165 |
| base | make | 35 | 310,454 | 2,483,632 | 3,311,509 |
| high | make | 94 | 840,052 | 6,866,512 | 9,155,349 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 90 | Unestablished | 650,430 | 325.2 |
| Vehicle production / low | 65 | 130 | Unestablished | Unestablished |
| Civil field / low | 132 | 264 | 1,369,429 | Unestablished |
| Civil other installation / low | 797 | 1,594 | 8,283,485 | Unestablished |
| Civil precast / low | 120 | 240 | 1,266,165 | Unestablished |
| Control room and access-site coverage / base | 180 | Unestablished | 1,478,250 | 739.1 |
| Vehicle production / base | 185 | 370 | Unestablished | Unestablished |
| Civil field / base | 489 | 978 | 4,303,083 | Unestablished |
| Civil other installation / base | 5,334 | 10,668 | 46,931,595 | Unestablished |
| Civil precast / base | 280 | 560 | 3,311,509 | Unestablished |
| Control room and access-site coverage / high | 360 | Unestablished | 3,547,800 | 1,773.9 |
| Vehicle production / high | 508 | 1,016 | Unestablished | Unestablished |
| Civil field / high | 2,131 | 4,262 | 11,929,408 | Unestablished |
| Civil other installation / high | 51,239 | 102,478 | 286,935,003 | Unestablished |
| Civil precast / high | 752 | 1,504 | 9,155,349 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 176 | 722.7 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.773bn | $6.107bn | $35.671bn |
| Installed capital / route-km | $4.34m | $14.96m | $87.36m |
| 30-year whole-life NPV | $3.708bn | $12.803bn | $72.054bn |
| Annual operating provision | $91.51m | $300.57m | $1.525bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.434bn | $1.434bn |
| Guideway | $558.60m | $558.60m |
| Stations power | $1.026bn | $1.026bn |
| Factory tooling | $58.13m | $58.13m |
| Construction | $2.470bn | $2.470bn |
| Land utilities depot | $380.76m | $380.76m |
| Fleet | $131.93m | $131.93m |
| Energy | $0 | $3.047bn |
| Operations | $0 | $199.97m |
| Maintenance | $0 | $1.764bn |
| Renewals | $0 | $1.443bn |
| Recovery | $46.36m | $94.45m |
| Reliability | $0 | $138.25m |
| Disposal | $0 | $56.48m |

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
| City project risk contingency | $1.221bn | 20.0% |
| Network delivered assembled fleet | $1.126bn | 18.4% |
| Design prototypes independent review | $360.93m | 5.9% |
| Shared access and transfer complexes | $276.94m | 4.5% |
| Repeat box beams | $268.77m | 4.4% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.773bn | $6.107bn | $35.671bn |
| Water-evidence alternative capital | $1.777bn | $6.128bn | $35.843bn |
| Alternative capital / route-km | $4.35m | $15.01m | $87.78m |
| Alternative whole-life NPV | $3.712bn | $12.825bn | $72.233bn |
| Included non-water obstruction reserve | $31,397 | $209,314 | $1.47m |

0.42 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 1 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-262.84m | $-12.151bn | -0.67 |
| 50% | 150.91m | 0.50 | $75.45m | $-225.12m | $-11.499bn | -0.57 |
| 50% | 150.91m | 1.00 | $150.91m | $-149.66m | $-10.194bn | -0.38 |
| 75% | 226.36m | 0.25 | $56.59m | $-243.98m | $-11.825bn | -0.62 |
| 75% | 226.36m | 0.50 | $113.18m | $-187.39m | $-10.846bn | -0.47 |
| 75% | 226.36m | 1.00 | $226.36m | $-74.21m | $-8.889bn | -0.19 |
| 100% | 301.81m | 0.25 | $75.45m | $-225.12m | $-11.499bn | -0.57 |
| 100% | 301.81m | 0.50 | $150.91m | $-149.66m | $-10.194bn | -0.38 |
| 100% | 301.81m | 1.00 | $301.81m | $1.24m | $-7.584bn | 0.00 |

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
| low | $1.241bn | $531.84m | $114.74m |
| base | $4.275bn | $1.832bn | $395.24m |
| high | $24.970bn | $10.701bn | $2.309bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/jeddah.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Saudi%20Arabia/Jeddah) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `fd898358a48ab5957e2cad4ddc592517248bd44ec51e827449fc7a9d3b0320c1` |
| cost_evaluation_id | `c1a8ef6e1d80871fa0cc16f34a957cf3e7ea92c78a26f01ed3fbfb87bf764d60` |
| outline_evaluation_id | `3487ff30cb2ef09c22e98161bf46e5adb8fa6f01671fcd844566e78e75cea526` |
| research_configuration_id | `2e7909932fdbbea9d5041cb7b0325f0506e4341f30f14e624b03f85110539bca` |
| seed_id | `92aad5ed956b51882fd7ecba36a9bdec7c310a8c036c92fd501a0c78f224647a` |
| selected_alignment_id | `1fd38267bc5a040e56af601b56155d0b3d38e91d8b5210818702afe9e4baf832` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `4744e3a9056e1a1b7f2b6a8dd473af698f917a28e2f322000a8fc002585765f2` |
| source_result_sha256 | `752a6278daf8ac8b6381d4ac3be78fa34bc166c6598f26c3c0310c71e8b68b57` |

Atlas packet `964e0557986d6d756a34a031f10674870a62dbe93ab91502bd558aca56a023da`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
