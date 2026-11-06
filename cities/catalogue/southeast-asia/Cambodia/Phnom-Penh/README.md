# Phnom Penh — railway design and city programme

**KH · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=phnom-penh) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=phnom-penh) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Phnom Penh current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,281,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 293.38 km / 2 trackways |
| Lines / operational platform groups | 9 / 139 |
| Original access markers / separately costed access sites | 159 / 64 |
| Explicit interchange references | 32 |
| Fleet including reserve | 351 six-car trainsets |
| Train distance | 190,110 train-km/day; 69,390,241 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 30.80 | 12 | 200 | 44.6 | 29 + 5 | 4,181 | SE terminal ↔ N terminal |
| line-2 | 32.77 | 22 | 200 | 57.7 | 37 + 6 | 4,181 | W terminal ↔ E terminal |
| line-3 | 58.36 | 26 | 200 | 90.7 | 57 + 9 | 4,181 | SW terminal ↔ NE terminal |
| line-4 | 35.33 | 19 | 200 | 58.2 | 37 + 6 | 4,181 | NE terminal ↔ S terminal |
| line-5 | 38.93 | 24 | 200 | 66.0 | 42 + 7 | 4,181 | NW terminal ↔ SE terminal |
| line-6 | 65.71 | 21 | 200 | 94.5 | 58 + 9 | 4,181 | Ring / closed circuit |
| line-7 | 6.47 | 3 | 200 | 9.2 | 8 + 2 | 4,181 | S terminal ↔ SW terminal |
| line-8 | 5.30 | 2 | 200 | 8.8 | 8 + 2 | 4,181 | W terminal ↔ W terminal |
| line-9 | 19.72 | 10 | 200 | 38.0 | 25 + 4 | 4,181 | E terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 69.87 | False | Unestablished |
| 800.00 | 13.33 | 279.48 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 843,791 kWh mechanical | 307.98 GWh mechanical |
| Nominal auxiliary load | 1,137,780 kWh | 415.29 GWh |
| Auxiliary supply including scenario charging losses | 1,197,663 kWh | 437.15 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $52.37m | $135.54m | $408.92m |

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
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 30.80 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 32.77 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 58.36 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 35.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 38.93 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 65.71 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 5,984.0 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,555.4 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 5,827.4 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,821.7 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,194.7 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,772.2 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 41.47 km |
| Bridge route | 57.47 km |
| Elevated route | 194.44 km |
| Tunnel route | 0.00 km |
| Precast span stock | 25,910 spans |
| Independent supports | 27,232 |
| Running rail | 1,182.32 rail-km / 71,187 t |
| Complete fastening sets | 2,069,061 |
| Protected at-grade crossing packages | 135 |
| Bridge runs / tunnel portals | 281 / 0 |
| Additional station track | 4,400 m |
| Access connector allowance | 1,463.5 m; actual accessible paths require survey |
| Pooled depot area | 245,700 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.16m | $5.38m | $34.81m |
| Civil production campaign | $7.52m | $36.64m | $218.44m |

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
| low | make | 11 | 90,692 | 673,712 | 898,283 |
| base | make | 25 | 220,252 | 1,762,016 | 2,349,355 |
| high | make | 67 | 595,976 | 4,871,456 | 6,495,275 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 66 | Unestablished | 476,982 | 238.5 |
| Vehicle production / low | 50 | 100 | Unestablished | Unestablished |
| Civil field / low | 95 | 190 | 981,408 | Unestablished |
| Civil other installation / low | 1,064 | 2,128 | 11,064,344 | Unestablished |
| Civil precast / low | 88 | 176 | 898,283 | Unestablished |
| Control room and access-site coverage / base | 132 | Unestablished | 1,084,050 | 542.0 |
| Vehicle production / base | 141 | 282 | Unestablished | Unestablished |
| Civil field / base | 351 | 702 | 3,082,411 | Unestablished |
| Civil other installation / base | 8,640 | 17,280 | 76,028,277 | Unestablished |
| Civil precast / base | 200 | 400 | 2,349,355 | Unestablished |
| Control room and access-site coverage / high | 264 | Unestablished | 2,601,720 | 1,300.9 |
| Vehicle production / high | 386 | 772 | Unestablished | Unestablished |
| Civil field / high | 1,526 | 3,052 | 8,542,197 | Unestablished |
| Civil other installation / high | 93,380 | 186,760 | 522,926,584 | Unestablished |
| Civil precast / high | 536 | 1,072 | 6,495,275 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 128 | 525.6 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.714bn | $6.767bn | $44.200bn |
| Installed capital / route-km | $5.84m | $23.06m | $150.66m |
| 30-year whole-life NPV | $3.198bn | $11.882bn | $72.142bn |
| Annual operating provision | $69.84m | $228.73m | $1.152bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.131bn | $1.131bn |
| Guideway | $397.98m | $397.98m |
| Stations power | $756.63m | $756.63m |
| Factory tooling | $42.02m | $42.02m |
| Construction | $4.023bn | $4.023bn |
| Land utilities depot | $280.59m | $280.59m |
| Fleet | $102.70m | $102.70m |
| Energy | $0 | $2.344bn |
| Operations | $0 | $146.64m |
| Maintenance | $0 | $1.331bn |
| Renewals | $0 | $1.098bn |
| Recovery | $33.11m | $67.47m |
| Reliability | $0 | $99.33m |
| Disposal | $0 | $62.59m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-204.47m | $-11.463bn | -0.47 |
| 50% | 97.01m | 0.50 | $48.51m | $-180.22m | $-11.044bn | -0.41 |
| 50% | 97.01m | 1.00 | $97.01m | $-131.71m | $-10.205bn | -0.30 |
| 75% | 145.52m | 0.25 | $36.38m | $-192.35m | $-11.253bn | -0.44 |
| 75% | 145.52m | 0.50 | $72.76m | $-155.97m | $-10.624bn | -0.36 |
| 75% | 145.52m | 1.00 | $145.52m | $-83.21m | $-9.366bn | -0.19 |
| 100% | 194.02m | 0.25 | $48.51m | $-180.22m | $-11.044bn | -0.41 |
| 100% | 194.02m | 0.50 | $97.01m | $-131.71m | $-10.205bn | -0.30 |
| 100% | 194.02m | 1.00 | $194.02m | $-34.70m | $-8.527bn | -0.08 |

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
| low | $1.200bn | $514.31m | $110.96m |
| base | $4.737bn | $2.030bn | $437.96m |
| high | $30.940bn | $13.260bn | $2.861bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/phnom-penh.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/southeast-asia/Cambodia/Phnom-Penh) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `9c002bd4c19c7cafd515cf3a49523e28a8561bad59d00eb3b7b6ce8ee0c30e7c` |
| cost_evaluation_id | `e3c768fef3073601ee1d961511433c39bd5f865f885a2954c0eb7319732735f8` |
| outline_evaluation_id | `a1992850988a6262240781eac16c2d2de45cb1556173d92b04d611ee153ccae7` |
| research_configuration_id | `8e59d9fe1cf271136cd4e461e24f648fb1badd450b8e354add35c87643ea8f8a` |
| seed_id | `3bc48042a0773ebdf26770a56b4fe3fc47d859eba14811c628ec610191974938` |
| selected_alignment_id | `98cc04f0054024774aaa5497b26fa21793cfcb070315a722238ce73f2dd9cc94` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `da91a37eab4910eb7f18bf9fbbf002f773ca44fbb59e1375cc8b5c480bc23ca3` |
| source_result_sha256 | `5ed701908169f0181a8ad6c822aea9f53e9e5a11df85f54a822f13812d09a974` |

Atlas packet `fc8d5f0f289f257c525e6f88bd0b55019f3f15652f6ae9847da8916e3a4b6805`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
