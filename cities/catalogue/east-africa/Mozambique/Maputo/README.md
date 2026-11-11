# Maputo — railway design and city programme

**MZ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=maputo) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=maputo) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Maputo current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,530,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 198.48 km / 2 trackways |
| Lines / operational platform groups | 9 / 79 |
| Original access markers / separately costed access sites | 92 / 43 |
| Explicit interchange references | 21 |
| Fleet including reserve | 252 six-car trainsets |
| Train distance | 128,616 train-km/day; 46,944,804 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 25.03 | 14 | 200 | 41.4 | 27 + 5 | 4,181 | S terminal ↔ NE terminal |
| line-2 | 22.63 | 11 | 200 | 39.0 | 26 + 4 | 4,181 | SE terminal ↔ N terminal |
| line-3 | 22.43 | 6 | 200 | 29.1 | 20 + 3 | 4,181 | NE terminal ↔ SW terminal |
| line-4 | 24.00 | 8 | 200 | 38.5 | 25 + 4 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 22.77 | 9 | 200 | 39.6 | 26 + 4 | 4,181 | E terminal ↔ W terminal |
| line-6 | 54.90 | 20 | 200 | 100.1 | 62 + 10 | 4,181 | Ring / closed circuit |
| line-7 | 6.83 | 3 | 200 | 9.9 | 8 + 2 | 4,181 | SW terminal ↔ SW terminal |
| line-8 | 8.96 | 5 | 200 | 15.6 | 12 + 2 | 4,181 | SW terminal ↔ SW terminal |
| line-9 | 10.92 | 3 | 200 | 12.4 | 10 + 2 | 4,181 | N terminal ↔ N terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 39.71 | False | Unestablished |
| 800.00 | 13.33 | 158.84 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 406,124 kWh mechanical | 148.24 GWh mechanical |
| Nominal auxiliary load | 816,480 kWh | 298.02 GWh |
| Auxiliary supply including scenario charging losses | 859,453 kWh | 313.70 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.23 GWh |
| Total priced grid-supply scenario | See annual budget | 511.03 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $33.18m | $84.61m | $246.82m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 25.03 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 22.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 10.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,839.2 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,956.8 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 5,570.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 50.28 km |
| Bridge route | 1.86 km |
| Elevated route | 146.34 km |
| Tunnel route | 0.00 km |
| Precast span stock | 15,032 spans |
| Independent supports | 15,650 |
| Running rail | 793.93 rail-km / 47,802 t |
| Complete fastening sets | 1,389,370 |
| Protected at-grade crossing packages | 286 |
| Bridge runs / tunnel portals | 23 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,007.1 m; actual accessible paths require survey |
| Pooled depot area | 176,592 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $25.93m |
| Civil production campaign | $4.59m | $22.08m | $130.45m |

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
| low | make | 6 | 52,612 | 390,832 | 521,109 |
| base | make | 15 | 127,772 | 1,022,176 | 1,362,901 |
| high | make | 39 | 345,736 | 2,826,016 | 3,768,021 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 45 | Unestablished | 325,215 | 162.6 |
| Vehicle production / low | 36 | 72 | Unestablished | Unestablished |
| Civil field / low | 55 | 110 | 567,787 | Unestablished |
| Civil other installation / low | 521 | 1,042 | 5,413,694 | Unestablished |
| Civil precast / low | 48 | 96 | 521,109 | Unestablished |
| Control room and access-site coverage / base | 90 | Unestablished | 739,125 | 369.6 |
| Vehicle production / base | 101 | 202 | Unestablished | Unestablished |
| Civil field / base | 203 | 406 | 1,783,531 | Unestablished |
| Civil other installation / base | 3,372 | 6,744 | 29,670,050 | Unestablished |
| Civil precast / base | 120 | 240 | 1,362,901 | Unestablished |
| Control room and access-site coverage / high | 180 | Unestablished | 1,773,900 | 887.0 |
| Vehicle production / high | 277 | 554 | Unestablished | Unestablished |
| Civil field / high | 883 | 1,766 | 4,943,147 | Unestablished |
| Civil other installation / high | 31,324 | 62,648 | 175,412,916 | Unestablished |
| Civil precast / high | 312 | 624 | 3,768,021 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 86 | 353.1 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $906.22m | $3.229bn | $18.938bn |
| Installed capital / route-km | $4.57m | $16.27m | $95.42m |
| 30-year whole-life NPV | $1.861bn | $6.574bn | $37.276bn |
| Annual operating provision | $44.72m | $147.56m | $753.69m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $677.84m | $677.84m |
| Guideway | $242.78m | $242.78m |
| Stations power | $611.50m | $611.50m |
| Factory tooling | $26.30m | $26.30m |
| Construction | $1.384bn | $1.384bn |
| Land utilities depot | $197.60m | $197.60m |
| Fleet | $65.70m | $65.70m |
| Energy | $0 | $1.463bn |
| Operations | $0 | $99.98m |
| Maintenance | $0 | $897.31m |
| Renewals | $0 | $763.81m |
| Recovery | $23.18m | $47.23m |
| Reliability | $0 | $67.20m |
| Disposal | $0 | $29.86m |

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
| City project risk contingency | $645.72m | 20.0% |
| Network delivered assembled fleet | $613.99m | 19.0% |
| Design prototypes independent review | $190.76m | 5.9% |
| Shared access and transfer complexes | $137.75m | 4.3% |
| Surface formation drainage crossings | $137.74m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $906.22m | $3.229bn | $18.938bn |
| Water-evidence alternative capital | $897.14m | $3.176bn | $18.507bn |
| Alternative capital / route-km | $4.52m | $16.00m | $93.24m |
| Alternative whole-life NPV | $1.852bn | $6.520bn | $36.835bn |
| Included non-water obstruction reserve | $121,653 | $811,023 | $5.68m |

1.62 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 9 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-123.31m | $-6.154bn | -0.59 |
| 50% | 97.01m | 0.50 | $48.51m | $-99.05m | $-5.735bn | -0.47 |
| 50% | 97.01m | 1.00 | $97.01m | $-50.55m | $-4.896bn | -0.24 |
| 75% | 145.52m | 0.25 | $36.38m | $-111.18m | $-5.945bn | -0.53 |
| 75% | 145.52m | 0.50 | $72.76m | $-74.80m | $-5.316bn | -0.36 |
| 75% | 145.52m | 1.00 | $145.52m | $-2.04m | $-4.058bn | -0.01 |
| 100% | 194.02m | 0.25 | $48.51m | $-99.05m | $-5.735bn | -0.47 |
| 100% | 194.02m | 0.50 | $97.01m | $-50.55m | $-4.896bn | -0.24 |
| 100% | 194.02m | 1.00 | $194.02m | $46.46m | $-3.219bn | 0.22 |

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
| low | $634.35m | $271.87m | $58.65m |
| base | $2.260bn | $968.58m | $208.97m |
| high | $13.257bn | $5.682bn | $1.226bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/maputo.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Mozambique/Maputo) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `47e556157779834e5900a9cc122680c83a2f91c691aa404b17959e242e66204a` |
| cost_evaluation_id | `19243f3ef1253ec01e93c63047af2bcfc16b93c14c914e965667289b9d6f71dd` |
| outline_evaluation_id | `195784a06b23826438998cc14e8f3aeb6408368012ed60910d553b6fc35b396b` |
| research_configuration_id | `2454fefab1b8d12f070496128cbe6878f890633ada9bcde68eebbb6119a4d677` |
| seed_id | `37b1e4c35ff1b69f81817a30f2b494d74984f7acf303f584c0ef20c5cf350a83` |
| selected_alignment_id | `ae25bd947ffd79d3964a209c8500e248c7d6f75f5fdbcbeff5d8ce4b128d060f` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `b73c458dfc12b92232c7d51ee838ab16547453f4c5fb368c4267a005a7bc13b6` |
| source_result_sha256 | `48265959a5032529b3b17790613e817104a070bdb847e00ec95b85bce14e3c3c` |

Atlas packet `44c836df8658587b456503b539ab1d509e9436666941f83080b2ab020ebbf933`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
