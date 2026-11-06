# Lubumbashi — railway design and city programme

**CD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=lubumbashi) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=lubumbashi) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Lubumbashi current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,829,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 156.94 km / 2 trackways |
| Lines / operational platform groups | 8 / 61 |
| Original access markers / separately costed access sites | 65 / 42 |
| Explicit interchange references | 16 |
| Fleet including reserve | 183 six-car trainsets |
| Train distance | 101,694 train-km/day; 37,118,397 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 24.30 | 11 | 200 | 37.4 | 25 + 4 | 4,181 | NE terminal ↔ S terminal |
| line-2 | 23.52 | 10 | 200 | 34.6 | 23 + 4 | 4,181 | W terminal ↔ E terminal |
| line-3 | 13.71 | 5 | 200 | 18.5 | 13 + 2 | 4,181 | NE terminal ↔ W terminal |
| line-4 | 27.97 | 9 | 200 | 37.9 | 25 + 4 | 4,181 | SE terminal ↔ N terminal |
| line-5 | 43.76 | 13 | 200 | 62.0 | 38 + 6 | 4,181 | Ring / closed circuit |
| line-6 | 7.44 | 5 | 200 | 15.5 | 12 + 2 | 4,181 | S terminal ↔ SE terminal |
| line-7 | 5.86 | 4 | 200 | 9.8 | 8 + 2 | 4,181 | E terminal ↔ E terminal |
| line-8 | 10.37 | 4 | 200 | 18.0 | 13 + 2 | 4,181 | SE terminal ↔ SW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 30.66 | False | Unestablished |
| 800.00 | 13.33 | 122.65 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 433,386 kWh mechanical | 158.19 GWh mechanical |
| Nominal auxiliary load | 593,460 kWh | 216.61 GWh |
| Auxiliary supply including scenario charging losses | 624,695 kWh | 228.01 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $27.29m | $70.77m | $214.07m |

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

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 24.30 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 23.52 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 13.71 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 27.97 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 43.76 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 5,687.5 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,825.9 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,609.9 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,906.2 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,599.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 11.95 km |
| Bridge route | 0.54 km |
| Elevated route | 144.45 km |
| Tunnel route | 0.00 km |
| Precast span stock | 14,540 spans |
| Independent supports | 14,678 |
| Running rail | 627.74 rail-km / 37,796 t |
| Complete fastening sets | 1,098,549 |
| Protected at-grade crossing packages | 55 |
| Bridge runs / tunnel portals | 11 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 388.2 m; actual accessible paths require survey |
| Pooled depot area | 128,388 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $801,232 | $3.28m | $18.49m |
| Civil production campaign | $4.46m | $21.42m | $126.53m |

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
| low | make | 6 | 50,890 | 378,040 | 504,053 |
| base | make | 14 | 123,590 | 988,720 | 1,318,293 |
| high | make | 38 | 334,420 | 2,733,520 | 3,644,693 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 44 | Unestablished | 317,988 | 159.0 |
| Vehicle production / low | 26 | 52 | Unestablished | Unestablished |
| Civil field / low | 53 | 106 | 544,299 | Unestablished |
| Civil other installation / low | 281 | 562 | 2,920,665 | Unestablished |
| Civil precast / low | 48 | 96 | 504,053 | Unestablished |
| Control room and access-site coverage / base | 88 | Unestablished | 722,700 | 361.4 |
| Vehicle production / base | 74 | 148 | Unestablished | Unestablished |
| Civil field / base | 195 | 390 | 1,710,443 | Unestablished |
| Civil other installation / base | 1,934 | 3,868 | 17,018,249 | Unestablished |
| Civil precast / base | 112 | 224 | 1,318,293 | Unestablished |
| Control room and access-site coverage / high | 176 | Unestablished | 1,734,480 | 867.2 |
| Vehicle production / high | 201 | 402 | Unestablished | Unestablished |
| Civil field / high | 847 | 1,694 | 4,742,123 | Unestablished |
| Civil other installation / high | 19,144 | 38,288 | 107,205,655 | Unestablished |
| Civil precast / high | 304 | 608 | 3,644,693 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 84 | 344.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $680.87m | $2.349bn | $13.804bn |
| Installed capital / route-km | $4.34m | $14.97m | $87.96m |
| 30-year whole-life NPV | $1.453bn | $5.031bn | $28.659bn |
| Annual operating provision | $36.63m | $120.79m | $620.47m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $577.40m | $577.40m |
| Guideway | $219.40m | $219.40m |
| Stations power | $390.45m | $390.45m |
| Factory tooling | $24.69m | $24.69m |
| Construction | $912.87m | $912.87m |
| Land utilities depot | $152.73m | $152.73m |
| Fleet | $52.82m | $52.82m |
| Energy | $0 | $1.224bn |
| Operations | $0 | $97.76m |
| Maintenance | $0 | $695.13m |
| Renewals | $0 | $571.87m |
| Recovery | $18.21m | $37.11m |
| Reliability | $0 | $53.13m |
| Disposal | $0 | $21.72m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-99.23m | $-4.658bn | -0.65 |
| 50% | 86.23m | 0.50 | $43.12m | $-77.68m | $-4.285bn | -0.51 |
| 50% | 86.23m | 1.00 | $86.23m | $-34.56m | $-3.540bn | -0.23 |
| 75% | 129.35m | 0.25 | $32.34m | $-88.45m | $-4.472bn | -0.58 |
| 75% | 129.35m | 0.50 | $64.67m | $-56.12m | $-3.913bn | -0.37 |
| 75% | 129.35m | 1.00 | $129.35m | $8.56m | $-2.794bn | 0.06 |
| 100% | 172.46m | 0.25 | $43.12m | $-77.68m | $-4.285bn | -0.51 |
| 100% | 172.46m | 0.50 | $86.23m | $-34.56m | $-3.540bn | -0.23 |
| 100% | 172.46m | 1.00 | $172.46m | $51.67m | $-2.049bn | 0.34 |

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
| low | $476.61m | $204.26m | $44.07m |
| base | $1.644bn | $704.57m | $152.01m |
| high | $9.663bn | $4.141bn | $893.46m |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/lubumbashi.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/central-africa/DR%20Congo/Lubumbashi) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `6609693a6426f37fc61eb6215a0bea246c056bf34c6192e11b92ec49dff91716` |
| cost_evaluation_id | `9426a45cdc59199c7655612f2324b413f691fdb3e3614db2926b330015762aa5` |
| outline_evaluation_id | `eff3498eb3d0b57a155fe886268ba2be9f31e6aa82350c4881e1245f1d4272b1` |
| research_configuration_id | `0be2cf67579508217d88f45e7aa8483827f11c29bd7471bc083b51d428defc39` |
| seed_id | `e39746d430f0f840ceccc33b8cb9e3193cca9356d6219964c8a4d5d488a75d07` |
| selected_alignment_id | `1669ca7793573adceddbc0cbfc62494a79c92ec327b9ff9748a948fe97eb8a15` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `d8a8276025164c7310ccd8fc6bde8babfcdf8bf1bc1cc1139fe9ed15608e7d25` |
| source_result_sha256 | `8135c19a8b2bf64d5a66f4e39ebeb554e769cdeffe92b2a4daddc575118bda0d` |

Atlas packet `db671e589831541c0de0d1f39d96e67a819bde1a00e66f3b07dcc4dcb5457dc6`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
