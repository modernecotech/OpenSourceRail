# Kigali — railway design and city programme

**RW · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kigali) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kigali) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kigali current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,208,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 194.88 km / 2 trackways |
| Lines / operational platform groups | 9 / 62 |
| Original access markers / separately costed access sites | 64 / 40 |
| Explicit interchange references | 17 |
| Fleet including reserve | 220 six-car trainsets |
| Train distance | 126,284 train-km/day; 46,093,742 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 27.62 | 7 | 200 | 35.1 | 23 + 4 | 4,181 | W terminal ↔ E terminal |
| line-2 | 25.22 | 10 | 200 | 44.0 | 29 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-3 | 18.54 | 7 | 200 | 30.6 | 21 + 4 | 4,181 | S terminal ↔ N terminal |
| line-4 | 21.33 | 9 | 200 | 31.9 | 21 + 4 | 4,181 | NE terminal ↔ SW terminal |
| line-5 | 21.39 | 6 | 200 | 27.3 | 19 + 3 | 4,181 | NW terminal ↔ SE terminal |
| line-6 | 61.14 | 15 | 200 | 82.4 | 50 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 5.11 | 3 | 200 | 7.5 | 7 + 2 | 4,181 | W terminal ↔ SW terminal |
| line-8 | 8.14 | 3 | 200 | 14.5 | 11 + 2 | 4,181 | SW terminal ↔ S terminal |
| line-9 | 6.39 | 2 | 200 | 6.4 | 6 + 1 | 4,181 | NW terminal ↔ W terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 31.16 | False | Unestablished |
| 800.00 | 13.33 | 124.66 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 453,573 kWh mechanical | 165.55 GWh mechanical |
| Nominal auxiliary load | 706,860 kWh | 258.00 GWh |
| Auxiliary supply including scenario charging losses | 744,063 kWh | 271.58 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.79 GWh |
| Total priced grid-supply scenario | See annual budget | 485.03 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $31.17m | $80.30m | $239.66m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 27.62 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 21.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 21.39 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 61.14 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 6.39 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,623.2 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,904.2 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,787.7 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,889.5 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,390.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 2.56 km |
| Bridge route | 1.93 km |
| Elevated route | 190.40 km |
| Tunnel route | 0.00 km |
| Precast span stock | 19,288 spans |
| Independent supports | 19,452 |
| Running rail | 779.53 rail-km / 46,936 t |
| Complete fastening sets | 1,364,182 |
| Protected at-grade crossing packages | 36 |
| Bridge runs / tunnel portals | 21 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 176.6 m; actual accessible paths require survey |
| Pooled depot area | 153,296 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $888,450 | $3.64m | $21.10m |
| Civil production campaign | $5.73m | $27.80m | $164.75m |

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
| low | make | 8 | 67,508 | 501,488 | 668,651 |
| base | make | 19 | 163,948 | 1,311,584 | 1,748,779 |
| high | make | 50 | 443,624 | 3,626,144 | 4,834,859 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 42 | Unestablished | 303,534 | 151.8 |
| Vehicle production / low | 31 | 62 | Unestablished | Unestablished |
| Civil field / low | 70 | 140 | 721,835 | Unestablished |
| Civil other installation / low | 347 | 694 | 3,601,959 | Unestablished |
| Civil precast / low | 64 | 128 | 668,651 | Unestablished |
| Control room and access-site coverage / base | 84 | Unestablished | 689,850 | 344.9 |
| Vehicle production / base | 88 | 176 | Unestablished | Unestablished |
| Civil field / base | 258 | 516 | 2,268,373 | Unestablished |
| Civil other installation / base | 2,348 | 4,696 | 20,654,184 | Unestablished |
| Civil precast / base | 152 | 304 | 1,748,779 | Unestablished |
| Control room and access-site coverage / high | 168 | Unestablished | 1,655,640 | 827.8 |
| Vehicle production / high | 242 | 484 | Unestablished | Unestablished |
| Civil field / high | 1,124 | 2,248 | 6,289,024 | Unestablished |
| Civil other installation / high | 22,841 | 45,682 | 127,908,248 | Unestablished |
| Civil precast / high | 400 | 800 | 4,834,859 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 80 | 328.5 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $821.02m | $2.849bn | $16.881bn |
| Installed capital / route-km | $4.21m | $14.62m | $86.62m |
| 30-year whole-life NPV | $1.705bn | $5.927bn | $33.737bn |
| Annual operating provision | $41.92m | $138.18m | $707.41m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $663.67m | $663.67m |
| Guideway | $285.20m | $285.20m |
| Stations power | $445.73m | $445.73m |
| Factory tooling | $31.44m | $31.44m |
| Construction | $1.155bn | $1.155bn |
| Land utilities depot | $184.56m | $184.56m |
| Fleet | $61.67m | $61.67m |
| Energy | $0 | $1.389bn |
| Operations | $0 | $93.32m |
| Maintenance | $0 | $819.21m |
| Renewals | $0 | $661.69m |
| Recovery | $21.52m | $43.85m |
| Reliability | $0 | $65.98m |
| Disposal | $0 | $26.35m |

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
| City project risk contingency | $569.82m | 20.0% |
| Network delivered assembled fleet | $536.03m | 18.8% |
| Design prototypes independent review | $168.42m | 5.9% |
| Repeat box beams | $141.93m | 5.0% |
| Piers and foundations | $130.52m | 4.6% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $821.02m | $2.849bn | $16.881bn |
| Water-evidence alternative capital | $818.64m | $2.835bn | $16.766bn |
| Alternative capital / route-km | $4.20m | $14.55m | $86.03m |
| Alternative whole-life NPV | $1.703bn | $5.912bn | $33.621bn |
| Included non-water obstruction reserve | $62,411 | $416,072 | $2.91m |

0.83 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 2 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-113.93m | $-5.507bn | -0.62 |
| 50% | 97.01m | 0.50 | $48.51m | $-89.68m | $-5.088bn | -0.49 |
| 50% | 97.01m | 1.00 | $97.01m | $-41.17m | $-4.249bn | -0.22 |
| 75% | 145.52m | 0.25 | $36.38m | $-101.80m | $-5.298bn | -0.55 |
| 75% | 145.52m | 0.50 | $72.76m | $-65.42m | $-4.668bn | -0.35 |
| 75% | 145.52m | 1.00 | $145.52m | $7.33m | $-3.410bn | 0.04 |
| 100% | 194.02m | 0.25 | $48.51m | $-89.68m | $-5.088bn | -0.49 |
| 100% | 194.02m | 0.50 | $97.01m | $-41.17m | $-4.249bn | -0.22 |
| 100% | 194.02m | 1.00 | $194.02m | $55.84m | $-2.572bn | 0.30 |

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
| low | $574.71m | $246.31m | $53.14m |
| base | $1.994bn | $854.73m | $184.40m |
| high | $11.817bn | $5.064bn | $1.093bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kigali.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Rwanda/Kigali) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `1b9363df446b5dedcff27dcc0973e7bb6648c33277de4aa4791de8337ee8320c` |
| cost_evaluation_id | `dbe951791ff7eb61f94b381f9a6b32e8bc70a5013fbcdfff0acf9834334cde52` |
| outline_evaluation_id | `cecdb2aaed280dc78a659d8a05f3c305eb7f8cf5f3e43866ac4db302d4ce520d` |
| research_configuration_id | `7ea8b7a159ab273fa99974123af7af630d2dc01b45f594a51a150258f254ad4b` |
| seed_id | `4d237a0414e70ae970de5addb7293bb45414849edaaf447b984e88f55046bb4e` |
| selected_alignment_id | `fb50ee00e27caf7c2c4dbc05be7d3a3ec632c15a7f71f55fd5b042126822ba7d` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `1959bacaa3c929c350bd741f02da2565d09a7ca0a9aa6479f11c59992fc46738` |
| source_result_sha256 | `ba3e486885eacff4d163e641a88b77ba467215f23cfd20ad9a738487816b019f` |

Atlas packet `d3b9ed3f6517acdbe100cbc583af332aea2e34a3c6f5567ca4d74843dc29185d`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
