# Mwanza — railway design and city programme

**TZ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=mwanza) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=mwanza) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Mwanza current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,100,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 199.50 km / 2 trackways |
| Lines / operational platform groups | 9 / 84 |
| Original access markers / separately costed access sites | 88 / 40 |
| Explicit interchange references | 22 |
| Fleet including reserve | 240 six-car trainsets |
| Train distance | 129,278 train-km/day; 47,186,325 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 17.83 | 8 | 200 | 27.2 | 19 + 3 | 4,181 | S terminal ↔ N terminal |
| line-2 | 24.18 | 11 | 200 | 42.1 | 28 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-3 | 27.44 | 11 | 200 | 39.4 | 26 + 4 | 4,181 | SW terminal ↔ NW terminal |
| line-4 | 18.96 | 10 | 200 | 29.6 | 20 + 3 | 4,181 | NE terminal ↔ W terminal |
| line-5 | 26.00 | 10 | 200 | 36.9 | 24 + 4 | 4,181 | NW terminal ↔ SE terminal |
| line-6 | 56.07 | 20 | 200 | 84.1 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 4.86 | 2 | 200 | 7.2 | 7 + 2 | 4,181 | SE terminal ↔ NE terminal |
| line-8 | 18.67 | 10 | 200 | 30.4 | 21 + 4 | 4,181 | NE terminal ↔ NW terminal |
| line-9 | 5.50 | 2 | 200 | 10.0 | 8 + 2 | 4,181 | S terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 42.22 | False | Unestablished |
| 800.00 | 13.33 | 168.89 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 538,897 kWh mechanical | 196.70 GWh mechanical |
| Nominal auxiliary load | 774,900 kWh | 282.84 GWh |
| Auxiliary supply including scenario charging losses | 815,684 kWh | 297.72 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $34.75m | $89.75m | $269.58m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 17.83 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 27.44 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 18.96 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 26.00 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 56.07 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 18.67 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,568.9 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 5,723.2 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,025.8 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,669.0 m | 5,554.5 m |
| line-6 | 2 | Coast stops before receiving zone | 6,503.8 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,742.6 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 9.49 km |
| Bridge route | 1.74 km |
| Elevated route | 188.28 km |
| Tunnel route | 0.00 km |
| Precast span stock | 19,072 spans |
| Independent supports | 19,294 |
| Running rail | 798.01 rail-km / 48,048 t |
| Complete fastening sets | 1,396,518 |
| Protected at-grade crossing packages | 83 |
| Bridge runs / tunnel portals | 14 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 296.6 m; actual accessible paths require survey |
| Pooled depot area | 167,232 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $956,219 | $4.00m | $24.51m |
| Civil production campaign | $5.66m | $27.52m | $163.09m |

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
| low | make | 8 | 66,752 | 495,872 | 661,163 |
| base | make | 19 | 162,112 | 1,296,896 | 1,729,195 |
| high | make | 49 | 438,656 | 3,585,536 | 4,780,715 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 42 | Unestablished | 303,534 | 151.8 |
| Vehicle production / low | 34 | 68 | Unestablished | Unestablished |
| Civil field / low | 69 | 138 | 714,389 | Unestablished |
| Civil other installation / low | 358 | 716 | 3,722,970 | Unestablished |
| Civil precast / low | 64 | 128 | 661,163 | Unestablished |
| Control room and access-site coverage / base | 84 | Unestablished | 689,850 | 344.9 |
| Vehicle production / base | 96 | 192 | Unestablished | Unestablished |
| Civil field / base | 256 | 512 | 2,244,885 | Unestablished |
| Civil other installation / base | 2,446 | 4,892 | 21,523,767 | Unestablished |
| Civil precast / base | 152 | 304 | 1,729,195 | Unestablished |
| Control room and access-site coverage / high | 168 | Unestablished | 1,655,640 | 827.8 |
| Vehicle production / high | 264 | 528 | Unestablished | Unestablished |
| Civil field / high | 1,112 | 2,224 | 6,223,701 | Unestablished |
| Civil other installation / high | 23,898 | 47,796 | 133,828,760 | Unestablished |
| Civil precast / high | 392 | 784 | 4,780,715 | Unestablished |

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
| Installed capital | $881.58m | $3.030bn | $17.682bn |
| Installed capital / route-km | $4.42m | $15.19m | $88.63m |
| 30-year whole-life NPV | $1.860bn | $6.400bn | $35.879bn |
| Annual operating provision | $46.23m | $151.41m | $764.30m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $756.48m | $756.48m |
| Guideway | $285.00m | $285.00m |
| Stations power | $463.81m | $463.81m |
| Factory tooling | $31.52m | $31.52m |
| Construction | $1.208bn | $1.208bn |
| Land utilities depot | $193.54m | $193.54m |
| Fleet | $69.23m | $69.23m |
| Energy | $0 | $1.552bn |
| Operations | $0 | $93.32m |
| Maintenance | $0 | $881.28m |
| Renewals | $0 | $722.90m |
| Recovery | $23.18m | $47.23m |
| Reliability | $0 | $67.55m |
| Disposal | $0 | $28.03m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-127.16m | $-5.980bn | -0.65 |
| 50% | 97.01m | 0.50 | $48.51m | $-102.91m | $-5.561bn | -0.52 |
| 50% | 97.01m | 1.00 | $97.01m | $-54.40m | $-4.722bn | -0.28 |
| 75% | 145.52m | 0.25 | $36.38m | $-115.03m | $-5.770bn | -0.59 |
| 75% | 145.52m | 0.50 | $72.76m | $-78.65m | $-5.141bn | -0.40 |
| 75% | 145.52m | 1.00 | $145.52m | $-5.89m | $-3.883bn | -0.03 |
| 100% | 194.02m | 0.25 | $48.51m | $-102.91m | $-5.561bn | -0.52 |
| 100% | 194.02m | 0.50 | $97.01m | $-54.40m | $-4.722bn | -0.28 |
| 100% | 194.02m | 1.00 | $194.02m | $42.61m | $-3.044bn | 0.22 |

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
| low | $617.11m | $264.47m | $57.06m |
| base | $2.121bn | $909.12m | $196.14m |
| high | $12.377bn | $5.305bn | $1.144bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/mwanza.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Tanzania/Mwanza) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `0043d74701a01fa388d3e5797dd8f1379d805539d61c1eec9d0fa70e5187e68d` |
| cost_evaluation_id | `475b67b63667224f71c650ab247187c3ea3c63b229fdae6b513741118670a9c1` |
| outline_evaluation_id | `38b43b9c5d80a23807598b1117b57614d60f24e944e424ef43b4344908d3a6d0` |
| research_configuration_id | `f2ea6e1fdbadbc243fc41005244d96e25cf37ff92108936f7e2f4c6ff7299678` |
| seed_id | `832245cd68387be22b9ee5c22928424154bbce543db317f3c812f03a045ab546` |
| selected_alignment_id | `621f9c450781a18ad90913526463d86da9c3a4d44642fa9bb0798e2c426718fa` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `b199cdbf63e3fc43fac470e4a5d618167b20bc38292f80297008b3659ffca642` |
| source_result_sha256 | `e447af1947e258a3d13c4ac56bbd6d01e266abd3f104cb8030108daf01bcd3d3` |

Atlas packet `fa8c67e936038e20622530813006a8d4bb59968f93203c0f80ee2536afe26b4e`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
