# Gujranwala — railway design and city programme

**PK · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=gujranwala) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=gujranwala) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Gujranwala current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,300,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 202.36 km / 2 trackways |
| Lines / operational platform groups | 8 / 60 |
| Original access markers / separately costed access sites | 63 / 43 |
| Explicit interchange references | 15 |
| Fleet including reserve | 225 six-car trainsets |
| Train distance | 131,132 train-km/day; 47,863,140 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 44.03 | 12 | 200 | 74.2 | 47 + 8 | 4,181 | N terminal ↔ SE terminal |
| line-2 | 31.43 | 10 | 200 | 43.0 | 28 + 5 | 4,181 | NE terminal ↔ W terminal |
| line-3 | 21.54 | 7 | 200 | 29.3 | 20 + 3 | 4,181 | NW terminal ↔ S terminal |
| line-4 | 28.68 | 9 | 200 | 38.0 | 25 + 4 | 4,181 | NW terminal ↔ E terminal |
| line-5 | 62.33 | 16 | 200 | 85.5 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-6 | 5.23 | 2 | 200 | 8.4 | 7 + 2 | 4,181 | S terminal ↔ S terminal |
| line-7 | 4.06 | 2 | 200 | 5.5 | 6 + 1 | 4,181 | S terminal ↔ SW terminal |
| line-8 | 5.07 | 2 | 200 | 7.9 | 7 + 2 | 4,181 | S terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 30.16 | False | Unestablished |
| 800.00 | 13.33 | 120.64 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 460,305 kWh mechanical | 168.01 GWh mechanical |
| Nominal auxiliary load | 725,760 kWh | 264.90 GWh |
| Auxiliary supply including scenario charging losses | 763,958 kWh | 278.84 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.79 GWh |
| Total priced grid-supply scenario | See annual budget | 495.48 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $31.79m | $82.03m | $245.69m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
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
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 31.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 21.54 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 28.68 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 62.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 6,884.3 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,825.9 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,816.0 m | 5,554.5 m |
| line-5 | 6 | Coast stops before receiving zone | 6,870.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 41.10 km |
| Bridge route | 4.00 km |
| Elevated route | 157.26 km |
| Tunnel route | 0.00 km |
| Precast span stock | 16,286 spans |
| Independent supports | 16,560 |
| Running rail | 809.46 rail-km / 48,737 t |
| Complete fastening sets | 1,416,549 |
| Protected at-grade crossing packages | 100 |
| Bridge runs / tunnel portals | 30 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 228.3 m; actual accessible paths require survey |
| Pooled depot area | 157,404 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $888,450 | $3.81m | $21.51m |
| Civil production campaign | $4.92m | $23.74m | $140.44m |

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
| low | make | 7 | 57,001 | 423,436 | 564,581 |
| base | make | 16 | 138,431 | 1,107,448 | 1,476,597 |
| high | make | 42 | 374,578 | 3,061,768 | 4,082,357 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 45 | Unestablished | 325,215 | 162.6 |
| Vehicle production / low | 32 | 64 | Unestablished | Unestablished |
| Civil field / low | 59 | 118 | 610,933 | Unestablished |
| Civil other installation / low | 362 | 724 | 3,755,652 | Unestablished |
| Civil precast / low | 56 | 112 | 564,581 | Unestablished |
| Control room and access-site coverage / base | 90 | Unestablished | 739,125 | 369.6 |
| Vehicle production / base | 90 | 180 | Unestablished | Unestablished |
| Civil field / base | 219 | 438 | 1,919,659 | Unestablished |
| Civil other installation / base | 2,565 | 5,130 | 22,570,820 | Unestablished |
| Civil precast / base | 128 | 256 | 1,476,597 | Unestablished |
| Control room and access-site coverage / high | 180 | Unestablished | 1,773,900 | 887.0 |
| Vehicle production / high | 248 | 496 | Unestablished | Unestablished |
| Civil field / high | 951 | 1,902 | 5,321,760 | Unestablished |
| Civil other installation / high | 25,943 | 51,886 | 145,276,530 | Unestablished |
| Civil precast / high | 336 | 672 | 4,082,357 | Unestablished |

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
| Installed capital | $818.12m | $2.890bn | $17.267bn |
| Installed capital / route-km | $4.04m | $14.28m | $85.33m |
| 30-year whole-life NPV | $1.712bn | $5.997bn | $34.285bn |
| Annual operating provision | $42.47m | $139.68m | $712.62m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $681.29m | $681.29m |
| Guideway | $257.45m | $257.45m |
| Stations power | $422.24m | $422.24m |
| Factory tooling | $27.54m | $27.54m |
| Construction | $1.226bn | $1.226bn |
| Land utilities depot | $189.37m | $189.37m |
| Fleet | $63.23m | $63.23m |
| Energy | $0 | $1.419bn |
| Operations | $0 | $99.98m |
| Maintenance | $0 | $804.26m |
| Renewals | $0 | $664.63m |
| Recovery | $23.18m | $47.23m |
| Reliability | $0 | $68.51m |
| Disposal | $0 | $26.73m |

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
| City project risk contingency | $578.05m | 20.0% |
| Network delivered assembled fleet | $548.21m | 19.0% |
| Design prototypes independent review | $170.88m | 5.9% |
| Bridge special foundations deck temporary | $137.21m | 4.7% |
| Shared access and transfer complexes | $131.75m | 4.6% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $818.12m | $2.890bn | $17.267bn |
| Water-evidence alternative capital | $812.63m | $2.858bn | $17.006bn |
| Alternative capital / route-km | $4.02m | $14.12m | $84.04m |
| Alternative whole-life NPV | $1.706bn | $5.965bn | $34.019bn |
| Included non-water obstruction reserve | $159,878 | $1.07m | $7.46m |

2.13 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-118.12m | $-5.624bn | -0.63 |
| 50% | 86.23m | 0.50 | $43.12m | $-96.56m | $-5.251bn | -0.52 |
| 50% | 86.23m | 1.00 | $86.23m | $-53.45m | $-4.506bn | -0.29 |
| 75% | 129.35m | 0.25 | $32.34m | $-107.34m | $-5.438bn | -0.57 |
| 75% | 129.35m | 0.50 | $64.67m | $-75.01m | $-4.879bn | -0.40 |
| 75% | 129.35m | 1.00 | $129.35m | $-10.33m | $-3.760bn | -0.06 |
| 100% | 172.46m | 0.25 | $43.12m | $-96.56m | $-5.251bn | -0.52 |
| 100% | 172.46m | 0.50 | $86.23m | $-53.45m | $-4.506bn | -0.29 |
| 100% | 172.46m | 1.00 | $172.46m | $32.78m | $-3.015bn | 0.18 |

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
| low | $572.68m | $245.43m | $52.95m |
| base | $2.023bn | $867.07m | $187.07m |
| high | $12.087bn | $5.180bn | $1.118bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/gujranwala.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Pakistan/Gujranwala) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `52a9800c072c13275076f6e15284a2fd56be7835d85ed0436838deb56bf4faf9` |
| cost_evaluation_id | `d4aca8f73363e3a608dd323a344560f1eccad18f20851fe3a2d6fd48c6670710` |
| outline_evaluation_id | `ffed9f8cddeeafde5b1218434904ebfd82ac3f1ab7bfd5c6e067067413a5106c` |
| research_configuration_id | `fd0c5bcf576141d1095631a59b84701caf7cb8f037a643d7b451a1ce6f8d2eb1` |
| seed_id | `ccadbbf21ae3944473caf72a05d775c8f2b33ea15e902d860fa4bde06ea6fc38` |
| selected_alignment_id | `e45e8d57bfc62271e134a658a5597d1ad360b94699ebc81e9a3d3282bc6cc74e` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `9089536de3847b55430d014ad2b4fe4fb1e17be82432e829df9567584970beeb` |
| source_result_sha256 | `bb08c1e058614c6c076487e1f393636b0da08a7e6f5aa6640e97674514c2e372` |

Atlas packet `70302550b1ceb0de4d055db19490929b7c86f5151f851baf3a22af5028d0074d`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
