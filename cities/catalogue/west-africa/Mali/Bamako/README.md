# Bamako — railway design and city programme

**ML · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=bamako) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=bamako) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Bamako current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,929,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 307.50 km / 2 trackways |
| Lines / operational platform groups | 9 / 146 |
| Original access markers / separately costed access sites | 173 / 70 |
| Explicit interchange references | 37 |
| Fleet including reserve | 365 six-car trainsets |
| Train distance | 199,257 train-km/day; 72,728,905 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 46.43 | 24 | 200 | 74.2 | 47 + 8 | 4,181 | NW terminal ↔ SE terminal |
| line-2 | 29.66 | 12 | 200 | 43.5 | 28 + 5 | 4,181 | SW terminal ↔ NE terminal |
| line-3 | 15.11 | 8 | 200 | 25.0 | 17 + 3 | 4,181 | SW terminal ↔ NE terminal |
| line-4 | 53.10 | 26 | 200 | 84.3 | 53 + 8 | 4,181 | W terminal ↔ SE terminal |
| line-5 | 19.51 | 11 | 200 | 36.3 | 24 + 4 | 4,181 | N terminal ↔ S terminal |
| line-6 | 110.51 | 48 | 200 | 172.5 | 104 + 16 | 4,181 | Ring / closed circuit |
| line-7 | 7.95 | 3 | 200 | 12.5 | 10 + 2 | 4,181 | SE terminal ↔ E terminal |
| line-8 | 10.50 | 4 | 200 | 16.4 | 12 + 2 | 4,181 | S terminal ↔ SE terminal |
| line-9 | 14.74 | 10 | 200 | 27.1 | 19 + 3 | 4,181 | SW terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 73.39 | False | Unestablished |
| 800.00 | 13.33 | 293.55 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 870,371 kWh mechanical | 317.69 GWh mechanical |
| Nominal auxiliary load | 1,186,920 kWh | 433.23 GWh |
| Auxiliary supply including scenario charging losses | 1,249,389 kWh | 456.03 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $54.69m | $141.17m | $423.35m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 46.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 29.66 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 53.10 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 110.51 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,355.5 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,586.4 m | 5,554.5 m |
| line-4 | 3 | Coast stops before receiving zone | 6,457.9 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,762.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 10.78 km |
| Bridge route | 76.95 km |
| Elevated route | 219.76 km |
| Tunnel route | 0.00 km |
| Precast span stock | 30,714 spans |
| Independent supports | 33,810 |
| Running rail | 1,229.98 rail-km / 74,057 t |
| Complete fastening sets | 2,152,471 |
| Protected at-grade crossing packages | 55 |
| Bridge runs / tunnel portals | 747 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 2,121.4 m; actual accessible paths require survey |
| Pooled depot area | 254,956 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.22m | $5.38m | $35.99m |
| Civil production campaign | $8.76m | $43.14m | $257.37m |

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
| low | make | 12 | 107,499 | 798,564 | 1,064,752 |
| base | make | 30 | 261,069 | 2,088,552 | 2,784,736 |
| high | make | 79 | 706,422 | 5,774,232 | 7,698,976 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 72 | Unestablished | 520,344 | 260.2 |
| Vehicle production / low | 52 | 104 | Unestablished | Unestablished |
| Civil field / low | 114 | 228 | 1,179,680 | Unestablished |
| Civil other installation / low | 1,419 | 2,838 | 14,752,120 | Unestablished |
| Civil precast / low | 96 | 192 | 1,064,752 | Unestablished |
| Control room and access-site coverage / base | 144 | Unestablished | 1,182,600 | 591.3 |
| Vehicle production / base | 146 | 292 | Unestablished | Unestablished |
| Civil field / base | 421 | 842 | 3,702,848 | Unestablished |
| Civil other installation / base | 12,018 | 24,036 | 105,753,265 | Unestablished |
| Civil precast / base | 240 | 480 | 2,784,736 | Unestablished |
| Control room and access-site coverage / high | 288 | Unestablished | 2,838,240 | 1,419.1 |
| Vehicle production / high | 401 | 802 | Unestablished | Unestablished |
| Civil field / high | 1,832 | 3,664 | 10,256,480 | Unestablished |
| Civil other installation / high | 132,685 | 265,370 | 743,032,140 | Unestablished |
| Civil precast / high | 632 | 1,264 | 7,698,976 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 140 | 574.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.035bn | $8.523bn | $58.242bn |
| Installed capital / route-km | $6.62m | $27.72m | $189.41m |
| 30-year whole-life NPV | $3.581bn | $13.881bn | $87.932bn |
| Annual operating provision | $73.03m | $239.41m | $1.213bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.135bn | $1.135bn |
| Guideway | $452.89m | $452.89m |
| Stations power | $815.32m | $815.32m |
| Factory tooling | $48.52m | $48.52m |
| Construction | $5.639bn | $5.639bn |
| Land utilities depot | $292.50m | $292.50m |
| Fleet | $104.38m | $104.38m |
| Energy | $0 | $2.441bn |
| Operations | $0 | $159.97m |
| Maintenance | $0 | $1.399bn |
| Renewals | $0 | $1.140bn |
| Recovery | $34.77m | $70.84m |
| Reliability | $0 | $104.11m |
| Disposal | $0 | $78.83m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-215.15m | $-13.462bn | -0.39 |
| 50% | 97.01m | 0.50 | $48.51m | $-190.90m | $-13.043bn | -0.35 |
| 50% | 97.01m | 1.00 | $97.01m | $-142.39m | $-12.204bn | -0.26 |
| 75% | 145.52m | 0.25 | $36.38m | $-203.03m | $-13.252bn | -0.37 |
| 75% | 145.52m | 0.50 | $72.76m | $-166.65m | $-12.623bn | -0.30 |
| 75% | 145.52m | 1.00 | $145.52m | $-93.89m | $-11.365bn | -0.17 |
| 100% | 194.02m | 0.25 | $48.51m | $-190.90m | $-13.043bn | -0.35 |
| 100% | 194.02m | 0.50 | $97.01m | $-142.39m | $-12.204bn | -0.26 |
| 100% | 194.02m | 1.00 | $194.02m | $-45.38m | $-10.526bn | -0.08 |

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
| low | $1.424bn | $610.47m | $131.71m |
| base | $5.966bn | $2.557bn | $551.62m |
| high | $40.770bn | $17.473bn | $3.770bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/bamako.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-africa/Mali/Bamako) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `57ba430076c97177ea19a35ca9aef99f85724f0c88eda3d2ffef0f3379bcb1ce` |
| cost_evaluation_id | `210097f0877408ecd2868e5dbd720f3e15b905b51996c5f1349519ec3e97658a` |
| outline_evaluation_id | `3b9939b561ed022164c087bf1015a67384a29c5bbed5193597f77041fe0abb91` |
| research_configuration_id | `9bd225a43bb6b9d791ace026367ce9da7fcdb646de69ebdb22a4ba8756a64ef3` |
| seed_id | `4c0dbbb92242d0a99b449ceec44a2d7d3e33a992bdf9e11a118f559c0e4a4f37` |
| selected_alignment_id | `ba5240dd9c329e7c689c23ff54a2b37e92e1ef9f2c470a966a35cc0da89fa1bc` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `4d57d41a2c5922685ceb6a68cfb5d812ccea56ab7bdb101f717742cf1a2c122b` |
| source_result_sha256 | `6a0709ad6ad4ca835bf1a2385a02599cadf24350a26a905507ae95484e0e340d` |

Atlas packet `db3f50e784fc81344bd3f9a690b58fc7adc16b7952af04294cafa038630886a3`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
