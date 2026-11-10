# Aleppo — railway design and city programme

**SY · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=aleppo) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=aleppo) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Aleppo current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,639,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 205.15 km / 2 trackways |
| Lines / operational platform groups | 9 / 123 |
| Original access markers / separately costed access sites | 163 / 44 |
| Explicit interchange references | 26 |
| Fleet including reserve | 264 six-car trainsets |
| Train distance | 132,939 train-km/day; 48,522,767 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 28.66 | 30 | 200 | 62.0 | 39 + 6 | 4,181 | SW terminal ↔ E terminal |
| line-2 | 27.93 | 13 | 200 | 42.2 | 28 + 5 | 4,181 | SE terminal ↔ NW terminal |
| line-3 | 15.70 | 13 | 200 | 33.2 | 22 + 4 | 4,181 | NE terminal ↔ SW terminal |
| line-4 | 27.35 | 22 | 200 | 51.4 | 33 + 5 | 4,181 | W terminal ↔ E terminal |
| line-5 | 29.20 | 20 | 200 | 52.0 | 33 + 5 | 4,181 | N terminal ↔ S terminal |
| line-6 | 59.43 | 19 | 200 | 85.7 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 4.40 | 2 | 200 | 6.1 | 6 + 1 | 4,181 | E terminal ↔ E terminal |
| line-8 | 6.98 | 2 | 200 | 6.9 | 6 + 1 | 4,181 | NE terminal ↔ NE terminal |
| line-9 | 5.50 | 2 | 200 | 10.0 | 8 + 2 | 4,181 | N terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 61.83 | False | Unestablished |
| 800.00 | 13.33 | 247.31 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 552,494 kWh mechanical | 201.66 GWh mechanical |
| Nominal auxiliary load | 858,060 kWh | 313.19 GWh |
| Auxiliary supply including scenario charging losses | 903,221 kWh | 329.68 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.37 GWh |
| Total priced grid-supply scenario | See annual budget | 586.19 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $37.60m | $97.05m | $291.04m |

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
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 28.66 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 27.93 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 27.35 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 29.20 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 59.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 6.98 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,055.5 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,822.9 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,796.4 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,456.7 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,395.6 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,975.2 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 13.17 km |
| Bridge route | 0.30 km |
| Elevated route | 191.69 km |
| Tunnel route | 0.00 km |
| Precast span stock | 19,296 spans |
| Independent supports | 19,550 |
| Running rail | 820.61 rail-km / 49,409 t |
| Complete fastening sets | 1,436,071 |
| Protected at-grade crossing packages | 98 |
| Bridge runs / tunnel portals | 12 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 3,195.7 m; actual accessible paths require survey |
| Pooled depot area | 184,704 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $26.35m |
| Civil production campaign | $5.73m | $27.80m | $165.09m |

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
| low | make | 8 | 67,536 | 501,696 | 668,928 |
| base | make | 19 | 164,016 | 1,312,128 | 1,749,504 |
| high | make | 50 | 443,808 | 3,627,648 | 4,836,864 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 46 | Unestablished | 332,442 | 166.2 |
| Vehicle production / low | 38 | 76 | Unestablished | Unestablished |
| Civil field / low | 70 | 140 | 723,093 | Unestablished |
| Civil other installation / low | 411 | 822 | 4,269,004 | Unestablished |
| Civil precast / low | 64 | 128 | 668,928 | Unestablished |
| Control room and access-site coverage / base | 92 | Unestablished | 755,550 | 377.8 |
| Vehicle production / base | 106 | 212 | Unestablished | Unestablished |
| Civil field / base | 259 | 518 | 2,272,192 | Unestablished |
| Civil other installation / base | 2,703 | 5,406 | 23,784,355 | Unestablished |
| Civil precast / base | 152 | 304 | 1,749,504 | Unestablished |
| Control room and access-site coverage / high | 184 | Unestablished | 1,813,320 | 906.7 |
| Vehicle production / high | 290 | 580 | Unestablished | Unestablished |
| Civil field / high | 1,125 | 2,250 | 6,299,307 | Unestablished |
| Civil other installation / high | 25,611 | 51,222 | 143,419,439 | Unestablished |
| Civil precast / high | 400 | 800 | 4,836,864 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 88 | 361.4 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $971.36m | $3.292bn | $18.818bn |
| Installed capital / route-km | $4.73m | $16.05m | $91.73m |
| 30-year whole-life NPV | $2.049bn | $7.001bn | $38.904bn |
| Annual operating provision | $50.38m | $165.43m | $837.06m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $844.81m | $844.81m |
| Guideway | $289.80m | $289.80m |
| Stations power | $561.94m | $561.94m |
| Factory tooling | $32.02m | $32.02m |
| Construction | $1.258bn | $1.258bn |
| Land utilities depot | $205.45m | $205.45m |
| Fleet | $76.91m | $76.91m |
| Energy | $0 | $1.678bn |
| Operations | $0 | $102.21m |
| Maintenance | $0 | $986.68m |
| Renewals | $0 | $817.50m |
| Recovery | $23.18m | $47.23m |
| Reliability | $0 | $69.46m |
| Disposal | $0 | $30.45m |

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
| City project risk contingency | $658.45m | 20.0% |
| Network delivered assembled fleet | $643.23m | 19.5% |
| Design prototypes independent review | $194.58m | 5.9% |
| Shared access and transfer complexes | $145.47m | 4.4% |
| Repeat box beams | $141.99m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $971.36m | $3.292bn | $18.818bn |
| Water-evidence alternative capital | $971.62m | $3.294bn | $18.830bn |
| Alternative capital / route-km | $4.74m | $16.06m | $91.79m |
| Alternative whole-life NPV | $2.049bn | $7.002bn | $38.916bn |
| Included non-water obstruction reserve | $12,172 | $81,145 | $568,012 |

0.16 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-141.18m | $-6.581bn | -0.66 |
| 50% | 97.01m | 0.50 | $48.51m | $-116.92m | $-6.162bn | -0.55 |
| 50% | 97.01m | 1.00 | $97.01m | $-68.42m | $-5.323bn | -0.32 |
| 75% | 145.52m | 0.25 | $36.38m | $-129.05m | $-6.372bn | -0.61 |
| 75% | 145.52m | 0.50 | $72.76m | $-92.67m | $-5.743bn | -0.43 |
| 75% | 145.52m | 1.00 | $145.52m | $-19.91m | $-4.485bn | -0.09 |
| 100% | 194.02m | 0.25 | $48.51m | $-116.92m | $-6.162bn | -0.55 |
| 100% | 194.02m | 0.50 | $97.01m | $-68.42m | $-5.323bn | -0.32 |
| 100% | 194.02m | 1.00 | $194.02m | $28.59m | $-3.646bn | 0.13 |

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
| low | $679.95m | $291.41m | $62.87m |
| base | $2.305bn | $987.68m | $213.09m |
| high | $13.173bn | $5.645bn | $1.218bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/aleppo.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Syria/Aleppo) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `7f6a956e467de5eb28b96d54a12ceac6bbe4e9188bc3e4c66968bf6eaf3827e3` |
| cost_evaluation_id | `acb1b61c7a5cad3ae4d5f74f86b9727179ac522f6719ff824768eb6ba8a64758` |
| outline_evaluation_id | `37f797965477adc9b53151ff86254bb998271c16d11df55c17d360bc8af3090f` |
| research_configuration_id | `54ea3dfba83378711cac6e99bf3f3fc9c397bb1577ae6e6b1c8e92b6ca898478` |
| seed_id | `b083f9f267cc772cb820b94f290a4a748a3e8873d06b382c5c76ae8bd21bc566` |
| selected_alignment_id | `9438e9cae00bc776813d7a9534bbab13b2a4bab3c3adb46756a0fa327fbf0b28` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `2e7ac525ec16a95c1377dc9cf2a8d934e2f3ae08156a2a0ad9f0ed28be9144a4` |
| source_result_sha256 | `9dd6fd8be3e88eda8f3cd374dcb164baa09ed0eaff1bdc18d33ee8474f0f972d` |

Atlas packet `dc0863b83edbc2f903b03059217a36c333d81e7a8d1c3b89252a885a5bd69cfa`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
