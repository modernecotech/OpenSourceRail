# Beirut — railway design and city programme

**LB · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=beirut) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=beirut) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Beirut current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,200,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 164.72 km / 2 trackways |
| Lines / operational platform groups | 9 / 69 |
| Original access markers / separately costed access sites | 75 / 39 |
| Explicit interchange references | 20 |
| Fleet including reserve | 202 six-car trainsets |
| Train distance | 106,740 train-km/day; 38,960,150 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 32.92 | 13 | 200 | 47.6 | 31 + 5 | 4,181 | SW terminal ↔ NE terminal |
| line-2 | 13.72 | 7 | 200 | 22.2 | 16 + 3 | 4,181 | W terminal ↔ S terminal |
| line-3 | 21.07 | 8 | 200 | 29.4 | 20 + 3 | 4,181 | W terminal ↔ NE terminal |
| line-4 | 17.37 | 9 | 200 | 32.3 | 22 + 4 | 4,181 | E terminal ↔ W terminal |
| line-5 | 18.49 | 8 | 200 | 31.9 | 21 + 4 | 4,181 | W terminal ↔ SE terminal |
| line-6 | 36.73 | 14 | 200 | 55.5 | 34 + 6 | 4,181 | Ring / closed circuit |
| line-7 | 5.60 | 3 | 200 | 8.3 | 7 + 2 | 4,181 | SW terminal ↔ SW terminal |
| line-8 | 12.77 | 5 | 200 | 19.6 | 14 + 3 | 4,181 | NE terminal ↔ NE terminal |
| line-9 | 6.04 | 2 | 200 | 6.1 | 6 + 1 | 4,181 | S terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 34.68 | False | Unestablished |
| 800.00 | 13.33 | 138.73 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 405,366 kWh mechanical | 147.96 GWh mechanical |
| Nominal auxiliary load | 646,380 kWh | 235.93 GWh |
| Auxiliary supply including scenario charging losses | 680,400 kWh | 248.35 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.50 GWh |
| Total priced grid-supply scenario | See annual budget | 441.23 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $28.41m | $73.05m | $217.05m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 32.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 21.07 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 36.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 6.04 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,775.2 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,351.7 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,244.8 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,038.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 3.36 km |
| Bridge route | 0.81 km |
| Elevated route | 160.55 km |
| Tunnel route | 0.00 km |
| Precast span stock | 16,438 spans |
| Independent supports | 16,702 |
| Running rail | 666.81 rail-km / 40,149 t |
| Complete fastening sets | 1,166,918 |
| Protected at-grade crossing packages | 72 |
| Bridge runs / tunnel portals | 23 / 0 |
| Additional station track | 3,960 m |
| Access connector allowance | 553.0 m; actual accessible paths require survey |
| Pooled depot area | 141,752 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $888,450 | $3.64m | $19.91m |
| Civil production campaign | $4.98m | $23.99m | $142.03m |

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
| low | make | 7 | 57,533 | 427,388 | 569,851 |
| base | make | 16 | 139,723 | 1,117,784 | 1,490,379 |
| high | make | 43 | 378,074 | 3,090,344 | 4,120,459 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 41 | Unestablished | 296,307 | 148.2 |
| Vehicle production / low | 29 | 58 | Unestablished | Unestablished |
| Civil field / low | 60 | 120 | 616,501 | Unestablished |
| Civil other installation / low | 393 | 786 | 4,084,016 | Unestablished |
| Civil precast / low | 56 | 112 | 569,851 | Unestablished |
| Control room and access-site coverage / base | 82 | Unestablished | 673,425 | 336.7 |
| Vehicle production / base | 81 | 162 | Unestablished | Unestablished |
| Civil field / base | 221 | 442 | 1,937,173 | Unestablished |
| Civil other installation / base | 2,490 | 4,980 | 21,905,470 | Unestablished |
| Civil precast / base | 128 | 256 | 1,490,379 | Unestablished |
| Control room and access-site coverage / high | 164 | Unestablished | 1,616,220 | 808.1 |
| Vehicle production / high | 222 | 444 | Unestablished | Unestablished |
| Civil field / high | 959 | 1,918 | 5,370,357 | Unestablished |
| Civil other installation / high | 22,789 | 45,578 | 127,615,165 | Unestablished |
| Civil precast / high | 344 | 688 | 4,120,459 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 78 | 320.3 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $782.55m | $2.697bn | $15.688bn |
| Installed capital / route-km | $4.75m | $16.37m | $95.24m |
| 30-year whole-life NPV | $1.610bn | $5.594bn | $31.704bn |
| Annual operating provision | $38.72m | $128.50m | $662.77m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $590.05m | $590.05m |
| Guideway | $243.33m | $243.33m |
| Stations power | $531.06m | $531.06m |
| Factory tooling | $27.63m | $27.63m |
| Construction | $1.067bn | $1.067bn |
| Land utilities depot | $164.33m | $164.33m |
| Fleet | $55.47m | $55.47m |
| Energy | $0 | $1.263bn |
| Operations | $0 | $91.10m |
| Maintenance | $0 | $793.07m |
| Renewals | $0 | $649.61m |
| Recovery | $18.21m | $37.11m |
| Reliability | $0 | $55.77m |
| Disposal | $0 | $24.95m |

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
| City project risk contingency | $539.42m | 20.0% |
| Network delivered assembled fleet | $492.17m | 18.2% |
| Design prototypes independent review | $159.34m | 5.9% |
| Shared access and transfer complexes | $125.89m | 4.7% |
| Repeat box beams | $120.96m | 4.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $782.55m | $2.697bn | $15.688bn |
| Water-evidence alternative capital | $784.10m | $2.706bn | $15.758bn |
| Alternative capital / route-km | $4.76m | $16.43m | $95.66m |
| Alternative whole-life NPV | $1.611bn | $5.603bn | $31.777bn |
| Included non-water obstruction reserve | $31,722 | $211,477 | $1.48m |

0.42 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-104.25m | $-5.174bn | -0.60 |
| 50% | 97.01m | 0.50 | $48.51m | $-79.99m | $-4.755bn | -0.46 |
| 50% | 97.01m | 1.00 | $97.01m | $-31.49m | $-3.916bn | -0.18 |
| 75% | 145.52m | 0.25 | $36.38m | $-92.12m | $-4.965bn | -0.53 |
| 75% | 145.52m | 0.50 | $72.76m | $-55.74m | $-4.336bn | -0.32 |
| 75% | 145.52m | 1.00 | $145.52m | $17.02m | $-3.077bn | 0.10 |
| 100% | 194.02m | 0.25 | $48.51m | $-79.99m | $-4.755bn | -0.46 |
| 100% | 194.02m | 0.50 | $97.01m | $-31.49m | $-3.916bn | -0.18 |
| 100% | 194.02m | 1.00 | $194.02m | $65.52m | $-2.239bn | 0.38 |

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
| low | $547.78m | $234.76m | $50.65m |
| base | $1.888bn | $809.13m | $174.57m |
| high | $10.982bn | $4.707bn | $1.015bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/beirut.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Lebanon/Beirut) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `18985501d67d6b78fde47ceba5fb31a042c408459a2db2329f503a801135721a` |
| cost_evaluation_id | `ac2ea073c91cdfc17fc26f68f2c1a4ee4421e8aa3fb2cde1f80d255a04d11b92` |
| outline_evaluation_id | `6dee546aa5d72dfe4bb210666e1c174a71548eeac5204e013d9b319be36f23c6` |
| research_configuration_id | `1441d1fc58bfd31905881e6d03b3f5d03ebcabb3ea868e7f280473abf36fdc7f` |
| seed_id | `b268c0f5a570a458aa15b6082e88c3857d8be9fec07b367331be09437d46b7f6` |
| selected_alignment_id | `c865f680f9c29f19babf1095ff7e31aed6823413cf763cb512e1ede60841e6ff` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `4b090c5c2412eb2e0d5f7b3817fd2710fb0cfed746e36b6ceeae9bca0ffd8827` |
| source_result_sha256 | `7f8be36d122b87ca759c1c087180d0dcbb7509d81296d2d205aeca96c156707b` |

Atlas packet `0cf41e80060bbac004509b221baf5f9c97eb14736100a800f4771b7e74b70226`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
