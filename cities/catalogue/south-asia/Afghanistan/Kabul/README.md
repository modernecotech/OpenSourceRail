# Kabul — railway design and city programme

**AF · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kabul) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kabul) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kabul current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 4,601,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 256.93 km / 2 trackways |
| Lines / operational platform groups | 11 / 152 |
| Original access markers / separately costed access sites | 205 / 58 |
| Explicit interchange references | 30 |
| Fleet including reserve | 341 six-car trainsets |
| Train distance | 166,492 train-km/day; 60,769,434 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 29.92 | 13 | 200 | 44.3 | 29 + 5 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 34.07 | 28 | 200 | 66.4 | 42 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-3 | 24.67 | 15 | 200 | 46.6 | 30 + 5 | 4,181 | W terminal ↔ NE terminal |
| line-4 | 29.97 | 15 | 200 | 46.6 | 30 + 5 | 4,181 | SW terminal ↔ E terminal |
| line-5 | 31.24 | 25 | 200 | 59.7 | 38 + 6 | 4,181 | NW terminal ↔ E terminal |
| line-6 | 22.17 | 11 | 200 | 35.1 | 23 + 4 | 4,181 | E terminal ↔ NE terminal |
| line-7 | 55.94 | 33 | 200 | 98.0 | 60 + 9 | 4,181 | Ring / closed circuit |
| line-8 | 5.55 | 3 | 200 | 11.7 | 9 + 2 | 4,181 | W terminal ↔ W terminal |
| line-9 | 5.36 | 2 | 200 | 9.0 | 8 + 2 | 4,181 | SW terminal ↔ S terminal |
| line-10 | 4.85 | 2 | 200 | 7.2 | 7 + 2 | 4,181 | N terminal ↔ NW terminal |
| line-11 | 13.21 | 5 | 200 | 20.6 | 15 + 3 | 4,181 | NW terminal ↔ W terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 76.40 | False | Unestablished |
| 800.00 | 13.33 | 305.61 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 679,032 kWh mechanical | 247.85 GWh mechanical |
| Nominal auxiliary load | 1,099,980 kWh | 401.49 GWh |
| Auxiliary supply including scenario charging losses | 1,157,874 kWh | 422.62 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.26 GWh |
| Total priced grid-supply scenario | See annual budget | 739.75 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $47.50m | $122.48m | $366.36m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 29.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 34.07 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 29.97 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 31.24 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 22.17 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 55.94 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,989.5 m | 5,554.5 m |
| line-2 | 3 | Coast stops before receiving zone | 6,405.0 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,558.0 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,600.1 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,454.4 m | 5,554.5 m |
| line-7 | 2 | Coast stops before receiving zone | 6,788.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 23.44 km |
| Bridge route | 4.57 km |
| Elevated route | 228.93 km |
| Tunnel route | 0.00 km |
| Precast span stock | 23,588 spans |
| Independent supports | 24,226 |
| Running rail | 1,027.73 rail-km / 61,879 t |
| Complete fastening sets | 1,798,521 |
| Protected at-grade crossing packages | 209 |
| Bridge runs / tunnel portals | 54 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 3,706.9 m; actual accessible paths require survey |
| Pooled depot area | 238,732 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.15m | $5.16m | $33.80m |
| Civil production campaign | $6.87m | $33.52m | $199.72m |

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
| low | make | 10 | 82,558 | 613,288 | 817,717 |
| base | make | 23 | 200,498 | 1,603,984 | 2,138,645 |
| high | make | 61 | 542,524 | 4,434,544 | 5,912,725 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 60 | Unestablished | 433,620 | 216.8 |
| Vehicle production / low | 48 | 96 | Unestablished | Unestablished |
| Civil field / low | 86 | 172 | 887,424 | Unestablished |
| Civil other installation / low | 594 | 1,188 | 6,173,549 | Unestablished |
| Civil precast / low | 80 | 160 | 817,717 | Unestablished |
| Control room and access-site coverage / base | 120 | Unestablished | 985,500 | 492.8 |
| Vehicle production / base | 137 | 274 | Unestablished | Unestablished |
| Civil field / base | 317 | 634 | 2,788,075 | Unestablished |
| Civil other installation / base | 4,098 | 8,196 | 36,058,107 | Unestablished |
| Civil precast / base | 184 | 368 | 2,138,645 | Unestablished |
| Control room and access-site coverage / high | 240 | Unestablished | 2,365,200 | 1,182.6 |
| Vehicle production / high | 375 | 750 | Unestablished | Unestablished |
| Civil field / high | 1,381 | 2,762 | 7,728,405 | Unestablished |
| Civil other installation / high | 40,079 | 80,158 | 224,442,112 | Unestablished |
| Civil precast / high | 488 | 976 | 5,912,725 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 116 | 476.3 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.272bn | $4.453bn | $26.127bn |
| Installed capital / route-km | $4.95m | $17.33m | $101.69m |
| 30-year whole-life NPV | $2.633bn | $9.151bn | $51.670bn |
| Annual operating provision | $63.61m | $209.00m | $1.059bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.067bn | $1.067bn |
| Guideway | $356.96m | $356.96m |
| Stations power | $716.20m | $716.20m |
| Factory tooling | $38.68m | $38.68m |
| Construction | $1.887bn | $1.887bn |
| Land utilities depot | $260.05m | $260.05m |
| Fleet | $97.88m | $97.88m |
| Energy | $0 | $2.118bn |
| Operations | $0 | $133.31m |
| Maintenance | $0 | $1.245bn |
| Renewals | $0 | $1.042bn |
| Recovery | $29.80m | $60.72m |
| Reliability | $0 | $86.99m |
| Disposal | $0 | $41.19m |

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
| City project risk contingency | $890.65m | 20.0% |
| Network delivered assembled fleet | $830.84m | 18.7% |
| Design prototypes independent review | $263.23m | 5.9% |
| Shared access and transfer complexes | $187.48m | 4.2% |
| Bridge special foundations deck temporary | $179.65m | 4.0% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.272bn | $4.453bn | $26.127bn |
| Water-evidence alternative capital | $1.255bn | $4.354bn | $25.317bn |
| Alternative capital / route-km | $4.88m | $16.94m | $98.54m |
| Alternative whole-life NPV | $2.616bn | $9.050bn | $50.842bn |
| Included non-water obstruction reserve | $256,487 | $1.71m | $11.97m |

3.42 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 118.57m | 0.25 | $29.64m | $-179.36m | $-8.638bn | -0.62 |
| 50% | 118.57m | 0.50 | $59.28m | $-149.72m | $-8.126bn | -0.52 |
| 50% | 118.57m | 1.00 | $118.57m | $-90.43m | $-7.100bn | -0.31 |
| 75% | 177.85m | 0.25 | $44.46m | $-164.54m | $-8.382bn | -0.57 |
| 75% | 177.85m | 0.50 | $88.93m | $-120.07m | $-7.613bn | -0.42 |
| 75% | 177.85m | 1.00 | $177.85m | $-31.15m | $-6.075bn | -0.11 |
| 100% | 237.14m | 0.25 | $59.28m | $-149.72m | $-8.126bn | -0.52 |
| 100% | 237.14m | 0.50 | $118.57m | $-90.43m | $-7.100bn | -0.31 |
| 100% | 237.14m | 1.00 | $237.14m | $28.14m | $-5.050bn | 0.10 |

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
| low | $890.22m | $381.52m | $82.31m |
| base | $3.117bn | $1.336bn | $288.23m |
| high | $18.289bn | $7.838bn | $1.691bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kabul.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Afghanistan/Kabul) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `f165acf07a8abd840f71fd67f477d1651dd2e2c5d5635e7fc936aeb1ed339b95` |
| cost_evaluation_id | `bdc241e986b8e2a63f80c57a3ce28b63838a051d20cecb0dcf67154100b2a8fa` |
| outline_evaluation_id | `c158072d4fb607ae0319a5e610695e3eb0213dfbb03c26d8854d7ae39a9ea33f` |
| research_configuration_id | `9a0b28be4d45c35b775913b234d0429bba46cff1cadbc048c6df041e43f9d427` |
| seed_id | `9b0a8bd397e26559cb4d8e22a1d56f585e90662b8fbe3674fd9820505a4709e6` |
| selected_alignment_id | `0360e9948cab083d1680dcdba803e5ad3ed5c913f3ba121a53192cac31278fa4` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `a42d1ce21b08d667b411669431ba70518ba7b214c35783f132e8856ecce2524a` |
| source_result_sha256 | `700057063f6a8877c02068c290451816f3112e11aa19ee2960e825e241aa20bb` |

Atlas packet `90353c3a8cf4357624137bcc2ab1d865eb136e85a40ad9c92cd139173b7d7c5f`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
