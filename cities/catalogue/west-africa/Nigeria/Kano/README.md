# Kano — railway design and city programme

**NG · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kano) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kano) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kano current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 4,200,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 455.59 km / 2 trackways |
| Lines / operational platform groups | 14 / 165 |
| Original access markers / separately costed access sites | 168 / 103 |
| Explicit interchange references | 44 |
| Fleet including reserve | 491 six-car trainsets |
| Train distance | 295,222 train-km/day; 107,756,001 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 46.01 | 17 | 200 | 68.1 | 43 + 7 | 4,181 | W terminal ↔ E terminal |
| line-2 | 49.27 | 17 | 200 | 69.5 | 44 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-3 | 47.52 | 18 | 200 | 69.1 | 44 + 7 | 4,181 | SW terminal ↔ NE terminal |
| line-4 | 32.84 | 13 | 200 | 48.3 | 31 + 5 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 33.58 | 13 | 200 | 48.4 | 31 + 5 | 4,181 | NE terminal ↔ S terminal |
| line-6 | 28.72 | 12 | 200 | 42.2 | 28 + 5 | 4,181 | N terminal ↔ SE terminal |
| line-7 | 46.30 | 17 | 200 | 66.2 | 42 + 7 | 4,181 | NE terminal ↔ S terminal |
| line-8 | 41.28 | 16 | 200 | 59.8 | 38 + 6 | 4,181 | SE terminal ↔ NW terminal |
| line-9 | 82.22 | 23 | 200 | 115.3 | 70 + 11 | 4,181 | Ring / closed circuit |
| line-10 | 10.22 | 4 | 200 | 14.2 | 11 + 2 | 4,181 | W terminal ↔ NW terminal |
| line-11 | 6.84 | 3 | 200 | 10.0 | 8 + 2 | 4,181 | SW terminal ↔ S terminal |
| line-12 | 9.94 | 4 | 200 | 13.6 | 10 + 2 | 4,181 | SW terminal ↔ SW terminal |
| line-13 | 9.59 | 4 | 200 | 12.9 | 10 + 2 | 4,181 | W terminal ↔ W terminal |
| line-14 | 11.25 | 4 | 200 | 14.3 | 11 + 2 | 4,181 | S terminal ↔ SW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 82.94 | False | Unestablished |
| 800.00 | 13.33 | 331.75 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,302,511 kWh mechanical | 475.42 GWh mechanical |
| Nominal auxiliary load | 1,591,380 kWh | 580.85 GWh |
| Auxiliary supply including scenario charging losses | 1,675,137 kWh | 611.42 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 10.17 GWh |
| Total priced grid-supply scenario | See annual budget | 1,209.51 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $77.12m | $200.25m | $608.13m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 46.01 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 49.27 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 47.52 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 32.84 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 33.58 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 28.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 46.30 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 41.28 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 82.22 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 4 / 749.2 kW | 10.22 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-12 | 4 / 749.2 kW | 9.94 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-13 | 4 / 749.2 kW | 9.59 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 11.25 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,995.0 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,686.7 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,747.3 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,707.0 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,353.1 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,388.4 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,636.6 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,076.3 m | 5,554.5 m |
| line-9 | 3 | Coast stops before receiving zone | 6,707.4 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 6,383.2 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 6,069.7 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 6,653.6 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 5,792.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 50.36 km |
| Bridge route | 31.23 km |
| Elevated route | 374.00 km |
| Tunnel route | 0.00 km |
| Precast span stock | 41,034 spans |
| Independent supports | 41,992 |
| Running rail | 1,822.36 rail-km / 109,724 t |
| Complete fastening sets | 3,189,126 |
| Protected at-grade crossing packages | 181 |
| Bridge runs / tunnel portals | 163 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 169.7 m; actual accessible paths require survey |
| Pooled depot area | 343,252 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.48m | $7.69m | $47.12m |
| Civil production campaign | $11.47m | $56.80m | $340.55m |

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
| low | make | 16 | 143,619 | 1,066,884 | 1,422,512 |
| base | make | 39 | 348,789 | 2,790,312 | 3,720,416 |
| high | make | 105 | 943,782 | 7,714,392 | 10,285,856 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 105 | Unestablished | 758,835 | 379.4 |
| Vehicle production / low | 69 | 138 | Unestablished | Unestablished |
| Civil field / low | 149 | 298 | 1,542,155 | Unestablished |
| Civil other installation / low | 1,025 | 2,050 | 10,657,189 | Unestablished |
| Civil precast / low | 128 | 256 | 1,422,512 | Unestablished |
| Control room and access-site coverage / base | 210 | Unestablished | 1,724,625 | 862.3 |
| Vehicle production / base | 197 | 394 | Unestablished | Unestablished |
| Civil field / base | 551 | 1,102 | 4,845,312 | Unestablished |
| Civil other installation / base | 8,110 | 16,220 | 71,365,345 | Unestablished |
| Civil precast / base | 312 | 624 | 3,720,416 | Unestablished |
| Control room and access-site coverage / high | 420 | Unestablished | 4,139,100 | 2,069.6 |
| Vehicle production / high | 540 | 1,080 | Unestablished | Unestablished |
| Civil field / high | 2,399 | 4,798 | 13,431,477 | Unestablished |
| Civil other installation / high | 86,599 | 173,198 | 484,952,735 | Unestablished |
| Civil precast / high | 840 | 1,680 | 10,285,856 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 206 | 845.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.131bn | $7.867bn | $49.168bn |
| Installed capital / route-km | $4.68m | $17.27m | $107.92m |
| 30-year whole-life NPV | $4.273bn | $15.232bn | $89.314bn |
| Annual operating provision | $102.22m | $333.97m | $1.686bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.634bn | $1.634bn |
| Guideway | $624.78m | $624.78m |
| Stations power | $933.81m | $933.81m |
| Factory tooling | $64.49m | $64.49m |
| Construction | $3.997bn | $3.997bn |
| Land utilities depot | $415.17m | $415.17m |
| Fleet | $146.80m | $146.80m |
| Energy | $0 | $3.463bn |
| Operations | $0 | $233.30m |
| Maintenance | $0 | $1.871bn |
| Renewals | $0 | $1.518bn |
| Recovery | $51.32m | $104.57m |
| Reliability | $0 | $154.25m |
| Disposal | $0 | $72.76m |

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
| City project risk contingency | $1.573bn | 20.0% |
| Network delivered assembled fleet | $1.196bn | 15.2% |
| Bridge special foundations deck temporary | $931.44m | 11.8% |
| Design prototypes independent review | $465.32m | 5.9% |
| Shared access and transfer complexes | $323.67m | 4.1% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.131bn | $7.867bn | $49.168bn |
| Water-evidence alternative capital | $1.946bn | $6.799bn | $40.494bn |
| Alternative capital / route-km | $4.27m | $14.92m | $88.88m |
| Alternative whole-life NPV | $4.088bn | $14.153bn | $80.414bn |
| Included non-water obstruction reserve | $2.11m | $14.06m | $98.39m |

28.11 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 7 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-296.24m | $-14.580bn | -0.58 |
| 50% | 150.91m | 0.50 | $75.45m | $-258.51m | $-13.928bn | -0.51 |
| 50% | 150.91m | 1.00 | $150.91m | $-183.06m | $-12.623bn | -0.36 |
| 75% | 226.36m | 0.25 | $56.59m | $-277.38m | $-14.254bn | -0.54 |
| 75% | 226.36m | 0.50 | $113.18m | $-220.79m | $-13.275bn | -0.43 |
| 75% | 226.36m | 1.00 | $226.36m | $-107.61m | $-11.318bn | -0.21 |
| 100% | 301.81m | 0.25 | $75.45m | $-258.51m | $-13.928bn | -0.51 |
| 100% | 301.81m | 0.50 | $150.91m | $-183.06m | $-12.623bn | -0.36 |
| 100% | 301.81m | 1.00 | $301.81m | $-32.15m | $-10.013bn | -0.06 |

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
| low | $1.492bn | $639.23m | $137.91m |
| base | $5.507bn | $2.360bn | $509.17m |
| high | $34.417bn | $14.750bn | $3.182bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kano.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-africa/Nigeria/Kano) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `fee33732dff3871faa979612b1f05566594edeb80b6e8f06bf1f57a1b94367a9` |
| cost_evaluation_id | `f5e2757acda1737fab2a7583b7bcd657b093c16cd626a82aa516513fc1d73580` |
| outline_evaluation_id | `85e94f58515407f431c4882c05a0e4fd766bcdf11e3d62e3c977637c8dd6f378` |
| research_configuration_id | `645517f97ce6c05bdbd5cb3bf8a0c36e922c034c6f6f522444d776006e1fe182` |
| seed_id | `dcbdaaa48794203e18df25839f6ef5f5a930eeac55af5192b60ad472ec3c32f7` |
| selected_alignment_id | `35e7ee57753c57579d82ae217d7443779a511d6cf347c6956ef2173595b57f1d` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `074fe4e0fa34a65c55c8091de41fcd064efcf9510775d93d43e657d1c5a74dce` |
| source_result_sha256 | `037c4a80e0657b753f6ccdacdd7a3a1e449382bb08b2ff67836dbd8dc94275a8` |

Atlas packet `4dbeff0b4c4679c2e02da4abe0956ea33c2e0518498a209ffdfec58a9a529d82`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
