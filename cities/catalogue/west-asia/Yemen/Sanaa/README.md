# Sanaa — railway design and city programme

**YE · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=sanaa) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=sanaa) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Sanaa current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,937,500 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 285.82 km / 2 trackways |
| Lines / operational platform groups | 11 / 135 |
| Original access markers / separately costed access sites | 160 / 71 |
| Explicit interchange references | 32 |
| Fleet including reserve | 375 six-car trainsets |
| Train distance | 185,209 train-km/day; 67,601,164 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 43.97 | 27 | 200 | 75.9 | 48 + 8 | 4,181 | NW terminal ↔ SE terminal |
| line-2 | 22.72 | 13 | 200 | 44.5 | 29 + 5 | 4,181 | N terminal ↔ SE terminal |
| line-3 | 32.59 | 8 | 200 | 61.9 | 39 + 6 | 4,181 | NW terminal ↔ SE terminal |
| line-4 | 20.65 | 8 | 200 | 35.0 | 23 + 4 | 4,181 | S terminal ↔ NE terminal |
| line-5 | 34.37 | 13 | 200 | 50.1 | 32 + 5 | 4,181 | E terminal ↔ W terminal |
| line-6 | 23.24 | 14 | 200 | 47.2 | 31 + 5 | 4,181 | W terminal ↔ SE terminal |
| line-7 | 62.66 | 25 | 200 | 97.0 | 60 + 9 | 4,181 | Ring / closed circuit |
| line-8 | 5.13 | 2 | 200 | 8.0 | 7 + 2 | 4,181 | S terminal ↔ S terminal |
| line-9 | 4.98 | 2 | 200 | 7.6 | 7 + 2 | 4,181 | N terminal ↔ N terminal |
| line-10 | 14.87 | 8 | 200 | 26.1 | 18 + 3 | 4,181 | S terminal ↔ S terminal |
| line-11 | 20.64 | 15 | 200 | 40.3 | 27 + 5 | 4,181 | W terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 67.86 | False | Unestablished |
| 800.00 | 13.33 | 271.43 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 672,321 kWh mechanical | 245.40 GWh mechanical |
| Nominal auxiliary load | 1,213,380 kWh | 442.88 GWh |
| Auxiliary supply including scenario charging losses | 1,277,242 kWh | 466.19 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.84 GWh |
| Total priced grid-supply scenario | See annual budget | 787.93 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $50.87m | $130.45m | $385.50m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 43.97 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 34.37 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 4 / 749.2 kW | 62.66 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,676.6 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,081.1 m | 5,554.5 m |
| line-7 | 3 | Coast stops before receiving zone | 6,575.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 26.63 km |
| Bridge route | 0.00 km |
| Elevated route | 259.19 km |
| Tunnel route | 0.00 km |
| Precast span stock | 26,000 spans |
| Independent supports | 26,208 |
| Running rail | 1,143.26 rail-km / 68,836 t |
| Complete fastening sets | 2,000,711 |
| Protected at-grade crossing packages | 106 |
| Bridge runs / tunnel portals | 0 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,805.8 m; actual accessible paths require survey |
| Pooled depot area | 261,924 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.30m | $5.55m | $36.41m |
| Civil production campaign | $7.53m | $36.77m | $219.19m |

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
| low | make | 11 | 91,000 | 676,000 | 901,333 |
| base | make | 25 | 221,000 | 1,768,000 | 2,357,333 |
| high | make | 67 | 598,000 | 4,888,000 | 6,517,333 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 73 | Unestablished | 527,571 | 263.8 |
| Vehicle production / low | 53 | 106 | Unestablished | Unestablished |
| Civil field / low | 94 | 188 | 972,885 | Unestablished |
| Civil other installation / low | 662 | 1,324 | 6,880,848 | Unestablished |
| Civil precast / low | 88 | 176 | 901,333 | Unestablished |
| Control room and access-site coverage / base | 146 | Unestablished | 1,199,025 | 599.5 |
| Vehicle production / base | 150 | 300 | Unestablished | Unestablished |
| Civil field / base | 348 | 696 | 3,057,323 | Unestablished |
| Civil other installation / base | 4,112 | 8,224 | 36,183,003 | Unestablished |
| Civil precast / base | 200 | 400 | 2,357,333 | Unestablished |
| Control room and access-site coverage / high | 292 | Unestablished | 2,877,660 | 1,438.8 |
| Vehicle production / high | 412 | 824 | Unestablished | Unestablished |
| Civil field / high | 1,514 | 3,028 | 8,476,416 | Unestablished |
| Civil other installation / high | 37,193 | 74,386 | 208,276,426 | Unestablished |
| Civil precast / high | 536 | 1,072 | 6,517,333 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 142 | 583.1 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.327bn | $4.560bn | $26.175bn |
| Installed capital / route-km | $4.64m | $15.95m | $91.58m |
| 30-year whole-life NPV | $2.793bn | $9.685bn | $54.325bn |
| Annual operating provision | $68.70m | $226.99m | $1.163bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.064bn | $1.064bn |
| Guideway | $394.61m | $394.61m |
| Stations power | $908.14m | $908.14m |
| Factory tooling | $42.32m | $42.32m |
| Construction | $1.731bn | $1.731bn |
| Land utilities depot | $285.51m | $285.51m |
| Fleet | $101.11m | $101.11m |
| Energy | $0 | $2.256bn |
| Operations | $0 | $162.20m |
| Maintenance | $0 | $1.376bn |
| Renewals | $0 | $1.158bn |
| Recovery | $33.11m | $67.47m |
| Reliability | $0 | $96.77m |
| Disposal | $0 | $42.18m |

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
| Network delivered assembled fleet | $913.68m | 20.0% |
| City project risk contingency | $912.00m | 20.0% |
| Design prototypes independent review | $269.38m | 5.9% |
| Shared access and transfer complexes | $224.78m | 4.9% |
| Repeat box beams | $191.33m | 4.2% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.327bn | $4.560bn | $26.175bn |
| Water-evidence alternative capital | $1.327bn | $4.560bn | $26.175bn |
| Alternative capital / route-km | $4.64m | $15.95m | $91.58m |
| Alternative whole-life NPV | $2.793bn | $9.685bn | $54.325bn |
| Included non-water obstruction reserve | $0 | $0 | $0 |

0.00 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 118.57m | 0.25 | $29.64m | $-197.35m | $-9.173bn | -0.67 |
| 50% | 118.57m | 0.50 | $59.28m | $-167.71m | $-8.660bn | -0.57 |
| 50% | 118.57m | 1.00 | $118.57m | $-108.42m | $-7.635bn | -0.37 |
| 75% | 177.85m | 0.25 | $44.46m | $-182.53m | $-8.917bn | -0.62 |
| 75% | 177.85m | 0.50 | $88.93m | $-138.07m | $-8.148bn | -0.47 |
| 75% | 177.85m | 1.00 | $177.85m | $-49.14m | $-6.610bn | -0.17 |
| 100% | 237.14m | 0.25 | $59.28m | $-167.71m | $-8.660bn | -0.57 |
| 100% | 237.14m | 0.50 | $118.57m | $-108.42m | $-7.635bn | -0.37 |
| 100% | 237.14m | 1.00 | $237.14m | $10.15m | $-5.585bn | 0.03 |

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
| low | $928.66m | $398.00m | $85.87m |
| base | $3.192bn | $1.368bn | $295.14m |
| high | $18.322bn | $7.852bn | $1.694bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/sanaa.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Yemen/Sanaa) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `926a0cc32286cb7f6b15e59cc466da83e6cd703940f4a73d2c26210cac456492` |
| cost_evaluation_id | `fe82b98bc07bf21a7689b727d7d1f8fdad0d9efd07ed5eaa00d14f2076045ab9` |
| outline_evaluation_id | `9ad77eca6076b4c9487581777f6ff548fe2a72c83feeb50830058ac8f5246652` |
| research_configuration_id | `a5a6fd49ee7a204d500fcbc2ee03a22a77296f7ad58f9596855175313ab5a534` |
| seed_id | `b694407ab24f2daaaff39a83c5bfc511c26fcbbe0c02b89c25412d9b88ae5593` |
| selected_alignment_id | `163cb64155e48649973815c993d668ae38448a4517311157144a8a67f5fb34e8` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `024b6f315a5da4b0093781cf4529b9fce75fc4af5640ddbfa8729b138257a856` |
| source_result_sha256 | `c5afc21db787841f302f3ac849290ce7fa56f101dc84cdb558926e634ad19381` |

Atlas packet `d7896cfa4aeb17692541f02bb72132316e15b04ab10ebd8e495ea122c866e21a`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
