# Damascus — railway design and city programme

**SY · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=damascus) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=damascus) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Damascus current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,503,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 225.77 km / 2 trackways |
| Lines / operational platform groups | 9 / 90 |
| Original access markers / separately costed access sites | 111 / 45 |
| Explicit interchange references | 20 |
| Fleet including reserve | 260 six-car trainsets |
| Train distance | 146,300 train-km/day; 53,399,371 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 27.71 | 13 | 200 | 42.8 | 28 + 5 | 4,181 | NE terminal ↔ W terminal |
| line-2 | 28.43 | 9 | 200 | 38.4 | 25 + 4 | 4,181 | SE terminal ↔ W terminal |
| line-3 | 29.33 | 10 | 200 | 40.6 | 27 + 5 | 4,181 | S terminal ↔ N terminal |
| line-4 | 26.63 | 11 | 200 | 48.0 | 31 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-5 | 29.62 | 16 | 200 | 47.7 | 31 + 5 | 4,181 | NE terminal ↔ SW terminal |
| line-6 | 67.31 | 24 | 200 | 99.2 | 60 + 9 | 4,181 | Ring / closed circuit |
| line-7 | 5.51 | 3 | 200 | 8.6 | 7 + 2 | 4,181 | SE terminal ↔ E terminal |
| line-8 | 4.93 | 2 | 200 | 7.4 | 7 + 2 | 4,181 | S terminal ↔ S terminal |
| line-9 | 6.30 | 2 | 200 | 6.3 | 6 + 1 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 45.24 | False | Unestablished |
| 800.00 | 13.33 | 180.96 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 561,865 kWh mechanical | 205.08 GWh mechanical |
| Nominal auxiliary load | 839,160 kWh | 306.29 GWh |
| Auxiliary supply including scenario charging losses | 883,326 kWh | 322.41 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $37.06m | $95.70m | $287.36m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 27.71 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 28.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 29.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 29.62 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 67.31 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 6.30 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,032.9 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,293.8 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,032.0 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,269.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,744.6 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,299.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 14.39 km |
| Bridge route | 0.88 km |
| Elevated route | 210.50 km |
| Tunnel route | 0.00 km |
| Precast span stock | 21,214 spans |
| Independent supports | 21,482 |
| Running rail | 903.08 rail-km / 54,375 t |
| Complete fastening sets | 1,580,398 |
| Protected at-grade crossing packages | 86 |
| Bridge runs / tunnel portals | 26 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,473.7 m; actual accessible paths require survey |
| Pooled depot area | 181,168 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $26.35m |
| Civil production campaign | $6.25m | $30.37m | $180.59m |

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
| low | make | 9 | 74,249 | 551,564 | 735,419 |
| base | make | 21 | 180,319 | 1,442,552 | 1,923,403 |
| high | make | 55 | 487,922 | 3,988,232 | 5,317,643 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 47 | Unestablished | 339,669 | 169.8 |
| Vehicle production / low | 37 | 74 | Unestablished | Unestablished |
| Civil field / low | 77 | 154 | 794,848 | Unestablished |
| Civil other installation / low | 397 | 794 | 4,127,580 | Unestablished |
| Civil precast / low | 72 | 144 | 735,419 | Unestablished |
| Control room and access-site coverage / base | 94 | Unestablished | 771,975 | 386.0 |
| Vehicle production / base | 104 | 208 | Unestablished | Unestablished |
| Civil field / base | 284 | 568 | 2,497,685 | Unestablished |
| Civil other installation / base | 2,718 | 5,436 | 23,916,006 | Unestablished |
| Civil precast / base | 168 | 336 | 1,923,403 | Unestablished |
| Control room and access-site coverage / high | 188 | Unestablished | 1,852,740 | 926.4 |
| Vehicle production / high | 286 | 572 | Unestablished | Unestablished |
| Civil field / high | 1,237 | 2,474 | 6,924,491 | Unestablished |
| Civil other installation / high | 26,575 | 53,150 | 148,819,626 | Unestablished |
| Civil precast / high | 440 | 880 | 5,317,643 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 90 | 369.6 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $972.50m | $3.343bn | $19.550bn |
| Installed capital / route-km | $4.31m | $14.81m | $86.59m |
| 30-year whole-life NPV | $2.026bn | $6.989bn | $39.355bn |
| Annual operating provision | $49.72m | $163.58m | $831.62m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $821.60m | $821.60m |
| Guideway | $318.70m | $318.70m |
| Stations power | $506.69m | $506.69m |
| Factory tooling | $34.59m | $34.59m |
| Construction | $1.346bn | $1.346bn |
| Land utilities depot | $213.77m | $213.77m |
| Fleet | $75.12m | $75.12m |
| Energy | $0 | $1.655bn |
| Operations | $0 | $104.43m |
| Maintenance | $0 | $965.29m |
| Renewals | $0 | $786.41m |
| Recovery | $26.49m | $53.97m |
| Reliability | $0 | $76.44m |
| Disposal | $0 | $30.92m |

[Full capital and lifecycle ledger](engineering/outline/costs.csv)

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-139.32m | $-6.570bn | -0.64 |
| 50% | 97.01m | 0.50 | $48.51m | $-115.07m | $-6.150bn | -0.53 |
| 50% | 97.01m | 1.00 | $97.01m | $-66.57m | $-5.311bn | -0.31 |
| 75% | 145.52m | 0.25 | $36.38m | $-127.20m | $-6.360bn | -0.59 |
| 75% | 145.52m | 0.50 | $72.76m | $-90.82m | $-5.731bn | -0.42 |
| 75% | 145.52m | 1.00 | $145.52m | $-18.06m | $-4.473bn | -0.08 |
| 100% | 194.02m | 0.25 | $48.51m | $-115.07m | $-6.150bn | -0.53 |
| 100% | 194.02m | 0.50 | $97.01m | $-66.57m | $-5.311bn | -0.31 |
| 100% | 194.02m | 1.00 | $194.02m | $30.44m | $-3.634bn | 0.14 |

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
| low | $680.75m | $291.75m | $62.94m |
| base | $2.340bn | $1.003bn | $216.37m |
| high | $13.685bn | $5.865bn | $1.265bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/damascus.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Syria/Damascus) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `1b48ae17295fb420bf392ead18fecbf8f35156971995bc0ee4149784bbe9fb3a` |
| cost_evaluation_id | `96ba99a09109bd95afbe0b1a6e7721e3f3851ee12b628933ec0b1e0a0a1ea69f` |
| outline_evaluation_id | `b77d8c92bb25703c2b0b6a7f2ae7a1088d59756b7a316de6b1d6fafd07ffc91e` |
| research_configuration_id | `797e5b95ef4b0cee366bed73c9a2adc0748128f6de64a1be2df155637e6e7978` |
| seed_id | `27f7fe0321fea225eea1d0cace66bf75f07725357346b748168ae8160b5ae5be` |
| selected_alignment_id | `8a362f2a8a884797e18eca3697766e54fd68f9f5a180ec1a389854ac2a05bb1d` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `768397a8c0df52042d560ac995a19a5238beeff8ccecfb367372014ac1435c3e` |
| source_result_sha256 | `50beb63bafafcdea355eae1aa101fc5b2c557f92693b00bfc38f95ffdcc66b08` |

Atlas packet `3021b16205cabe4d967fe7976659cc0dcc4631446a5ca59cd42cb4bb0acff3c4`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
