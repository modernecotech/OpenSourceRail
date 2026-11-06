# Dammam — railway design and city programme

**SA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=dammam) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=dammam) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Dammam current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,500,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 306.00 km / 2 trackways |
| Lines / operational platform groups | 9 / 93 |
| Original access markers / separately costed access sites | 96 / 58 |
| Explicit interchange references | 24 |
| Fleet including reserve | 320 six-car trainsets |
| Train distance | 198,291 train-km/day; 72,376,108 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 45.16 | 13 | 200 | 62.7 | 40 + 6 | 4,181 | SE terminal ↔ NW terminal |
| line-2 | 39.33 | 12 | 200 | 53.4 | 34 + 6 | 4,181 | NW terminal ↔ SE terminal |
| line-3 | 31.37 | 10 | 200 | 43.9 | 29 + 5 | 4,181 | E terminal ↔ SW terminal |
| line-4 | 32.23 | 10 | 200 | 44.0 | 29 + 5 | 4,181 | SW terminal ↔ E terminal |
| line-5 | 43.70 | 15 | 200 | 61.3 | 39 + 6 | 4,181 | N terminal ↔ S terminal |
| line-6 | 91.75 | 25 | 200 | 126.7 | 78 + 12 | 4,181 | Ring / closed circuit |
| line-7 | 6.97 | 3 | 200 | 11.2 | 9 + 2 | 4,181 | NW terminal ↔ SW terminal |
| line-8 | 9.36 | 3 | 200 | 15.2 | 11 + 2 | 4,181 | E terminal ↔ NE terminal |
| line-9 | 6.14 | 2 | 200 | 6.2 | 6 + 1 | 4,181 | NW terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 46.75 | False | Unestablished |
| 800.00 | 13.33 | 186.99 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 783,215 kWh mechanical | 285.87 GWh mechanical |
| Nominal auxiliary load | 1,039,500 kWh | 379.42 GWh |
| Auxiliary supply including scenario charging losses | 1,094,211 kWh | 399.39 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $48.10m | $124.62m | $376.81m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 45.16 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 39.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 31.37 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 32.23 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 43.70 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 91.75 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 6.14 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,166.5 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 6,018.1 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,597.9 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,179.6 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,006.9 m | 5,554.5 m |
| line-6 | 4 | Coast stops before receiving zone | 6,974.8 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,138.6 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 59.63 km |
| Bridge route | 2.29 km |
| Elevated route | 244.08 km |
| Tunnel route | 0.00 km |
| Precast span stock | 24,948 spans |
| Independent supports | 25,838 |
| Running rail | 1,224.02 rail-km / 73,698 t |
| Complete fastening sets | 2,142,030 |
| Protected at-grade crossing packages | 427 |
| Bridge runs / tunnel portals | 16 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 256.6 m; actual accessible paths require survey |
| Pooled depot area | 222,976 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.14m | $4.80m | $30.38m |
| Civil production campaign | $7.22m | $35.30m | $210.45m |

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
| low | make | 10 | 87,318 | 648,648 | 864,864 |
| base | make | 24 | 212,058 | 1,696,464 | 2,261,952 |
| high | make | 64 | 573,804 | 4,690,224 | 6,253,632 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 60 | Unestablished | 433,620 | 216.8 |
| Vehicle production / low | 45 | 90 | Unestablished | Unestablished |
| Civil field / low | 91 | 182 | 940,885 | Unestablished |
| Civil other installation / low | 490 | 980 | 5,090,082 | Unestablished |
| Civil precast / low | 80 | 160 | 864,864 | Unestablished |
| Control room and access-site coverage / base | 120 | Unestablished | 985,500 | 492.8 |
| Vehicle production / base | 128 | 256 | Unestablished | Unestablished |
| Civil field / base | 336 | 672 | 2,955,712 | Unestablished |
| Civil other installation / base | 3,570 | 7,140 | 31,413,588 | Unestablished |
| Civil precast / base | 192 | 384 | 2,261,952 | Unestablished |
| Control room and access-site coverage / high | 240 | Unestablished | 2,365,200 | 1,182.6 |
| Vehicle production / high | 352 | 704 | Unestablished | Unestablished |
| Civil field / high | 1,463 | 2,926 | 8,192,363 | Unestablished |
| Civil other installation / high | 36,331 | 72,662 | 203,452,401 | Unestablished |
| Civil precast / high | 512 | 1,024 | 6,253,632 | Unestablished |

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
| Installed capital | $1.227bn | $4.262bn | $25.156bn |
| Installed capital / route-km | $4.01m | $13.93m | $82.21m |
| 30-year whole-life NPV | $2.569bn | $8.878bn | $50.009bn |
| Annual operating provision | $63.90m | $208.96m | $1.052bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.049bn | $1.049bn |
| Guideway | $392.62m | $392.62m |
| Stations power | $568.58m | $568.58m |
| Factory tooling | $40.10m | $40.10m |
| Construction | $1.807bn | $1.807bn |
| Land utilities depot | $274.59m | $274.59m |
| Fleet | $94.74m | $94.74m |
| Energy | $0 | $2.155bn |
| Operations | $0 | $133.31m |
| Maintenance | $0 | $1.185bn |
| Renewals | $0 | $963.99m |
| Recovery | $34.77m | $70.84m |
| Reliability | $0 | $103.60m |
| Disposal | $0 | $39.42m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-184.70m | $-8.459bn | -0.67 |
| 50% | 97.01m | 0.50 | $48.51m | $-160.45m | $-8.040bn | -0.58 |
| 50% | 97.01m | 1.00 | $97.01m | $-111.95m | $-7.201bn | -0.41 |
| 75% | 145.52m | 0.25 | $36.38m | $-172.58m | $-8.249bn | -0.63 |
| 75% | 145.52m | 0.50 | $72.76m | $-136.20m | $-7.620bn | -0.49 |
| 75% | 145.52m | 1.00 | $145.52m | $-63.44m | $-6.362bn | -0.23 |
| 100% | 194.02m | 0.25 | $48.51m | $-160.45m | $-8.040bn | -0.58 |
| 100% | 194.02m | 0.50 | $97.01m | $-111.95m | $-7.201bn | -0.41 |
| 100% | 194.02m | 1.00 | $194.02m | $-14.93m | $-5.523bn | -0.05 |

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
| low | $859.02m | $368.15m | $79.43m |
| base | $2.983bn | $1.278bn | $275.83m |
| high | $17.609bn | $7.547bn | $1.628bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/dammam.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Saudi%20Arabia/Dammam) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `1545da249c6a7aa0304b4c1fcde3d745ceed3bac0826fbe37fc6425a22038020` |
| cost_evaluation_id | `3bfb6c022fbe0c90970ac1edc7e590ae11d224e6d1d7ef74d0b641afc0b8a10b` |
| outline_evaluation_id | `64ecd77247d28b92e23f781d18d3456726e689c88999dfaae5b5ec64bd8cc080` |
| research_configuration_id | `29825e6ee85418802898163d54be2107b4ed8264a5fdf55b6d5dfe077f115685` |
| seed_id | `92706504cc4ce54fbb3c7c29b5e42bd8ca53b1ba8fbb984e5814bf962ad60ced` |
| selected_alignment_id | `059da9a01da94135ffb9c7409ae63efb3faf74087e6a83d82e6ab22bd0ec7b9a` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `194b2811f70c2cf9fedfaa166e628c87657241382679741e5f3a393bc7198509` |
| source_result_sha256 | `277f717cab2c7fca8daba7239263cd37be63c0ca757c6b05e0c3627aa2f5df8a` |

Atlas packet `195b3a38727bf8ceb4147f3cc49ccfdaf6c917f8cbcdd6ebfdcf97e56f50495c`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
