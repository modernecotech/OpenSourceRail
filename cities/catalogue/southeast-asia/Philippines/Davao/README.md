# Davao — railway design and city programme

**PH · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=davao) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=davao) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Davao current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,827,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 298.18 km / 2 trackways |
| Lines / operational platform groups | 9 / 94 |
| Original access markers / separately costed access sites | 97 / 62 |
| Explicit interchange references | 25 |
| Fleet including reserve | 331 six-car trainsets |
| Train distance | 193,221 train-km/day; 70,525,518 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 44.11 | 13 | 200 | 79.6 | 50 + 8 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 37.73 | 14 | 200 | 55.2 | 35 + 6 | 4,181 | NW terminal ↔ SE terminal |
| line-3 | 39.91 | 12 | 200 | 54.2 | 35 + 6 | 4,181 | E terminal ↔ W terminal |
| line-4 | 41.18 | 13 | 200 | 57.3 | 37 + 6 | 4,181 | W terminal ↔ E terminal |
| line-5 | 29.22 | 10 | 200 | 40.5 | 27 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-6 | 85.71 | 22 | 200 | 117.9 | 72 + 11 | 4,181 | Ring / closed circuit |
| line-7 | 7.46 | 4 | 200 | 11.6 | 9 + 2 | 4,181 | S terminal ↔ SW terminal |
| line-8 | 6.50 | 3 | 200 | 10.5 | 9 + 2 | 4,181 | NE terminal ↔ E terminal |
| line-9 | 6.35 | 3 | 200 | 10.7 | 9 + 2 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 47.25 | False | Unestablished |
| 800.00 | 13.33 | 189.00 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 722,240 kWh mechanical | 263.62 GWh mechanical |
| Nominal auxiliary load | 1,069,740 kWh | 390.46 GWh |
| Auxiliary supply including scenario charging losses | 1,126,042 kWh | 411.01 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 6.97 GWh |
| Total priced grid-supply scenario | See annual budget | 747.86 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $47.97m | $123.82m | $371.21m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 37.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 39.91 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 41.18 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 29.22 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 85.71 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 6,026.2 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 5,918.2 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,864.1 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,787.1 m | 5,554.5 m |
| line-6 | 6 | Coast stops before receiving zone | 6,712.6 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 42.51 km |
| Bridge route | 7.53 km |
| Elevated route | 248.15 km |
| Tunnel route | 0.00 km |
| Precast span stock | 25,840 spans |
| Independent supports | 26,938 |
| Running rail | 1,192.72 rail-km / 71,814 t |
| Complete fastening sets | 2,087,260 |
| Protected at-grade crossing packages | 397 |
| Bridge runs / tunnel portals | 88 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 244.8 m; actual accessible paths require survey |
| Pooled depot area | 231,764 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.15m | $5.02m | $31.40m |
| Civil production campaign | $7.47m | $36.52m | $218.03m |

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
| low | make | 11 | 90,440 | 671,840 | 895,787 |
| base | make | 25 | 219,640 | 1,757,120 | 2,342,827 |
| high | make | 67 | 594,320 | 4,857,920 | 6,477,227 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 64 | Unestablished | 462,528 | 231.3 |
| Vehicle production / low | 47 | 94 | Unestablished | Unestablished |
| Civil field / low | 94 | 188 | 976,405 | Unestablished |
| Civil other installation / low | 589 | 1,178 | 6,124,839 | Unestablished |
| Civil precast / low | 88 | 176 | 895,787 | Unestablished |
| Control room and access-site coverage / base | 128 | Unestablished | 1,051,200 | 525.6 |
| Vehicle production / base | 133 | 266 | Unestablished | Unestablished |
| Civil field / base | 349 | 698 | 3,067,029 | Unestablished |
| Civil other installation / base | 4,345 | 8,690 | 38,231,700 | Unestablished |
| Civil precast / base | 200 | 400 | 2,342,827 | Unestablished |
| Control room and access-site coverage / high | 256 | Unestablished | 2,522,880 | 1,261.4 |
| Vehicle production / high | 364 | 728 | Unestablished | Unestablished |
| Civil field / high | 1,518 | 3,036 | 8,500,309 | Unestablished |
| Civil other installation / high | 44,529 | 89,058 | 249,357,614 | Unestablished |
| Civil precast / high | 536 | 1,072 | 6,477,227 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 124 | 509.2 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.284bn | $4.614bn | $28.008bn |
| Installed capital / route-km | $4.31m | $15.47m | $93.93m |
| 30-year whole-life NPV | $2.630bn | $9.273bn | $53.376bn |
| Annual operating provision | $63.96m | $209.75m | $1.064bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.026bn | $1.026bn |
| Guideway | $398.40m | $398.40m |
| Stations power | $628.63m | $628.63m |
| Factory tooling | $41.53m | $41.53m |
| Construction | $2.115bn | $2.115bn |
| Land utilities depot | $276.22m | $276.22m |
| Fleet | $94.45m | $94.45m |
| Energy | $0 | $2.141bn |
| Operations | $0 | $142.20m |
| Maintenance | $0 | $1.208bn |
| Renewals | $0 | $989.19m |
| Recovery | $33.11m | $67.47m |
| Reliability | $0 | $100.95m |
| Disposal | $0 | $42.67m |

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
| City project risk contingency | $922.75m | 20.0% |
| Network delivered assembled fleet | $806.48m | 17.5% |
| Bridge special foundations deck temporary | $293.29m | 6.4% |
| Design prototypes independent review | $272.82m | 5.9% |
| Shared access and transfer complexes | $193.34m | 4.2% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.284bn | $4.614bn | $28.008bn |
| Water-evidence alternative capital | $1.278bn | $4.576bn | $27.698bn |
| Alternative capital / route-km | $4.28m | $15.35m | $92.89m |
| Alternative whole-life NPV | $2.623bn | $9.235bn | $53.063bn |
| Included non-water obstruction reserve | $271,276 | $1.81m | $12.66m |

3.62 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 16 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-185.49m | $-8.853bn | -0.62 |
| 50% | 97.01m | 0.50 | $48.51m | $-161.24m | $-8.434bn | -0.54 |
| 50% | 97.01m | 1.00 | $97.01m | $-112.74m | $-7.595bn | -0.38 |
| 75% | 145.52m | 0.25 | $36.38m | $-173.37m | $-8.643bn | -0.58 |
| 75% | 145.52m | 0.50 | $72.76m | $-136.99m | $-8.014bn | -0.46 |
| 75% | 145.52m | 1.00 | $145.52m | $-64.23m | $-6.756bn | -0.22 |
| 100% | 194.02m | 0.25 | $48.51m | $-161.24m | $-8.434bn | -0.54 |
| 100% | 194.02m | 0.50 | $97.01m | $-112.74m | $-7.595bn | -0.38 |
| 100% | 194.02m | 1.00 | $194.02m | $-15.72m | $-5.918bn | -0.05 |

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
| low | $898.76m | $385.18m | $83.10m |
| base | $3.230bn | $1.384bn | $298.62m |
| high | $19.606bn | $8.402bn | $1.813bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/davao.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/southeast-asia/Philippines/Davao) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `e4045d6063239972574001f55b49f977473f45cb3ced15919f00381c10be27c1` |
| cost_evaluation_id | `1eb247df5b7bc72dfa4133597ea75c4b3b3a34f173b66ad20b48f0327b349d7b` |
| outline_evaluation_id | `cf8f26ecec10b20070f8f3dcb4d73e2d0eb0274e5fd042bb2068e14119debc3e` |
| research_configuration_id | `be1b096c55604bbcad5d2385067940bad86b001d4ec05be1b41e4894bfd3f232` |
| seed_id | `f0210fa74ee8bec5196487e1e573f5df470dc713ba9212eb4968289b1b20c958` |
| selected_alignment_id | `b646add1a25bc0dc1fedc38a43f98cf63ba97fec3a8a767f4269ee4895f0f60b` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `3a02e6396b79133b1ed9edf4440daf55792b270f135540801a4793f552bb6e82` |
| source_result_sha256 | `2c8f916da2e7601e36f3b4ac05c4f3afee60319558404d4bf03e0483e6b374ae` |

Atlas packet `95bbb50e7319136f4e234e08ab7e4e76d391fd420a46a90fad9916bc53a0b032`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
