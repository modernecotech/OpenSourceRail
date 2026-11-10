# Tabuk — railway design and city programme

**SA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=tabuk) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=tabuk) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Tabuk current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 650,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 74.15 km / 2 trackways |
| Lines / operational platform groups | 5 / 26 |
| Original access markers / separately costed access sites | 27 / 21 |
| Explicit interchange references | 5 |
| Fleet including reserve | 95 six-car trainsets |
| Train distance | 48,052 train-km/day; 17,538,915 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 18.99 | 7 | 200 | 26.8 | 18 + 3 | 4,181 | NE terminal ↔ W terminal |
| line-2 | 18.17 | 7 | 200 | 27.9 | 19 + 3 | 4,181 | NW terminal ↔ S terminal |
| line-3 | 25.20 | 7 | 200 | 42.8 | 28 + 5 | 4,181 | E terminal ↔ SW terminal |
| line-4 | 4.59 | 2 | 200 | 6.5 | 6 + 1 | 4,181 | E terminal ↔ SE terminal |
| line-5 | 7.20 | 3 | 200 | 12.9 | 10 + 2 | 4,181 | NE terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 13.07 | False | Unestablished |
| 800.00 | 13.33 | 52.28 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 138,383 kWh mechanical | 50.51 GWh mechanical |
| Nominal auxiliary load | 306,180 kWh | 111.76 GWh |
| Auxiliary supply including scenario charging losses | 322,295 kWh | 117.64 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 2.03 GWh |
| Total priced grid-supply scenario | See annual budget | 187.61 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $12.11m | $31.06m | $91.59m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 18.99 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,114.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 11.50 km |
| Bridge route | 3.15 km |
| Elevated route | 59.51 km |
| Tunnel route | 0.00 km |
| Precast span stock | 6,358 spans |
| Independent supports | 6,570 |
| Running rail | 296.62 rail-km / 17,859 t |
| Complete fastening sets | 519,079 |
| Protected at-grade crossing packages | 49 |
| Bridge runs / tunnel portals | 31 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 79.9 m; actual accessible paths require survey |
| Pooled depot area | 66,820 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $636,311 | $2.12m | $10.03m |
| Civil production campaign | $2.29m | $10.52m | $60.45m |

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
| low | make | 3 | 22,253 | 165,308 | 220,411 |
| base | make | 7 | 54,043 | 432,344 | 576,459 |
| high | make | 17 | 146,234 | 1,195,304 | 1,593,739 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 23 | Unestablished | 166,221 | 83.1 |
| Vehicle production / low | 14 | 28 | Unestablished | Unestablished |
| Civil field / low | 24 | 48 | 239,627 | Unestablished |
| Civil other installation / low | 191 | 382 | 1,984,153 | Unestablished |
| Civil precast / low | 24 | 48 | 220,411 | Unestablished |
| Control room and access-site coverage / base | 46 | Unestablished | 377,775 | 188.9 |
| Vehicle production / base | 38 | 76 | Unestablished | Unestablished |
| Civil field / base | 86 | 172 | 752,789 | Unestablished |
| Civil other installation / base | 1,342 | 2,684 | 11,804,831 | Unestablished |
| Civil precast / base | 56 | 112 | 576,459 | Unestablished |
| Control room and access-site coverage / high | 92 | Unestablished | 906,660 | 453.3 |
| Vehicle production / high | 105 | 210 | Unestablished | Unestablished |
| Civil field / high | 373 | 746 | 2,086,560 | Unestablished |
| Civil other installation / high | 13,466 | 26,932 | 75,408,117 | Unestablished |
| Civil precast / high | 136 | 272 | 1,593,739 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 42 | 172.5 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $340.97m | $1.267bn | $7.831bn |
| Installed capital / route-km | $4.60m | $17.09m | $105.61m |
| 30-year whole-life NPV | $691.94m | $2.515bn | $14.958bn |
| Annual operating provision | $16.52m | $55.22m | $290.92m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $251.73m | $251.73m |
| Guideway | $98.37m | $98.37m |
| Stations power | $213.89m | $213.89m |
| Factory tooling | $12.63m | $12.63m |
| Construction | $579.83m | $579.83m |
| Land utilities depot | $77.67m | $77.67m |
| Fleet | $24.54m | $24.54m |
| Energy | $0 | $537.12m |
| Operations | $0 | $51.10m |
| Maintenance | $0 | $332.87m |
| Renewals | $0 | $281.28m |
| Recovery | $8.28m | $16.87m |
| Reliability | $0 | $25.11m |
| Disposal | $0 | $11.72m |

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
| City project risk contingency | $253.39m | 20.0% |
| Network delivered assembled fleet | $231.47m | 18.3% |
| Bridge special foundations deck temporary | $116.12m | 9.2% |
| Design prototypes independent review | $74.88m | 5.9% |
| Shared access and transfer complexes | $62.02m | 4.9% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $340.97m | $1.267bn | $7.831bn |
| Water-evidence alternative capital | $320.57m | $1.149bn | $6.871bn |
| Alternative capital / route-km | $4.32m | $15.49m | $92.67m |
| Alternative whole-life NPV | $671.43m | $2.395bn | $13.972bn |
| Included non-water obstruction reserve | $183,451 | $1.22m | $8.56m |

2.45 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 53.89m | 0.25 | $13.47m | $-41.74m | $-2.282bn | -0.51 |
| 50% | 53.89m | 0.50 | $26.95m | $-28.27m | $-2.049bn | -0.34 |
| 50% | 53.89m | 1.00 | $53.89m | $-1.32m | $-1.583bn | -0.02 |
| 75% | 80.84m | 0.25 | $20.21m | $-35.00m | $-2.165bn | -0.43 |
| 75% | 80.84m | 0.50 | $40.42m | $-14.79m | $-1.816bn | -0.18 |
| 75% | 80.84m | 1.00 | $80.84m | $25.63m | $-1.117bn | 0.31 |
| 100% | 107.79m | 0.25 | $26.95m | $-28.27m | $-2.049bn | -0.34 |
| 100% | 107.79m | 0.50 | $53.89m | $-1.32m | $-1.583bn | -0.02 |
| 100% | 107.79m | 1.00 | $107.79m | $52.57m | $-650.84m | 0.64 |

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
| low | $238.68m | $102.29m | $22.07m |
| base | $886.87m | $380.09m | $82.00m |
| high | $5.482bn | $2.349bn | $506.88m |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/tabuk.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Saudi%20Arabia/Tabuk) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `9a9f6318eca1677dc61a5a57bcf82a9f843d819cd8a83e8ceac7cd22d49b134b` |
| cost_evaluation_id | `08b7873e99467312343648898ad35428aeaa528d6b3329d74a9690f03c0337ca` |
| outline_evaluation_id | `d123e514e2cc36f8e4bc2729549bd323d38cc4d45c4b04fed5b06b8888ecb4c8` |
| research_configuration_id | `a102f49c5fdca43dd21bcf3472ffb6e6dbcdc7b98617677749a001c3e04bcb28` |
| seed_id | `0621d35c90c1960d39ed2cce5498cfd4d8b30a64815e286e1ed2a97fa44a4a94` |
| selected_alignment_id | `815c8eaaee37d4dac76c14870cb6fbe8f1cb8799473c3ae48afbf4e91f95dedc` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `3771cfb3b85ec81749c3ccafb1ef86a8b767344b5443d612875837519432f219` |
| source_result_sha256 | `1d745211420f448cf230a2584f12f8acfb18d272579c070b242d275168669721` |

Atlas packet `d356f25944c36a9ef2e5ab9434916bd74d4f9cc8931c040e6e1a38e6505c3abc`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
