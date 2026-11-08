# Surabaya — railway design and city programme

**ID · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=surabaya) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=surabaya) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Surabaya current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,009,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 311.72 km / 2 trackways |
| Lines / operational platform groups | 9 / 160 |
| Original access markers / separately costed access sites | 184 / 66 |
| Explicit interchange references | 39 |
| Fleet including reserve | 398 six-car trainsets |
| Train distance | 201,993 train-km/day; 73,727,573 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 43.75 | 24 | 200 | 91.6 | 57 + 9 | 4,181 | N terminal ↔ SE terminal |
| line-2 | 41.27 | 19 | 200 | 65.3 | 41 + 7 | 4,181 | NE terminal ↔ S terminal |
| line-3 | 40.78 | 16 | 200 | 60.5 | 39 + 6 | 4,181 | NE terminal ↔ SW terminal |
| line-4 | 33.83 | 20 | 200 | 57.1 | 37 + 6 | 4,181 | N terminal ↔ S terminal |
| line-5 | 36.28 | 22 | 200 | 73.4 | 46 + 7 | 4,181 | E terminal ↔ NW terminal |
| line-6 | 19.79 | 9 | 200 | 29.8 | 20 + 3 | 4,181 | SW terminal ↔ E terminal |
| line-7 | 19.72 | 12 | 200 | 38.1 | 25 + 4 | 4,181 | NW terminal ↔ E terminal |
| line-8 | 18.05 | 9 | 200 | 27.2 | 19 + 3 | 4,181 | E terminal ↔ W terminal |
| line-9 | 58.26 | 29 | 200 | 98.1 | 60 + 9 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 80.42 | False | Unestablished |
| 800.00 | 13.33 | 321.70 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 865,286 kWh mechanical | 315.83 GWh mechanical |
| Nominal auxiliary load | 1,300,320 kWh | 474.62 GWh |
| Auxiliary supply including scenario charging losses | 1,368,758 kWh | 499.60 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.84 GWh |
| Total priced grid-supply scenario | See annual budget | 901.78 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $58.06m | $149.30m | $444.24m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 41.27 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 40.78 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 33.83 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 19.79 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 18.05 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 58.26 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 2 | Coast stops before receiving zone | 5,852.6 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 5,852.6 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,468.5 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,695.3 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 5,708.1 m | 5,554.5 m |
| line-9 | 4 | Coast stops before receiving zone | 6,697.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 40.56 km |
| Bridge route | 33.09 km |
| Elevated route | 238.07 km |
| Tunnel route | 0.00 km |
| Precast span stock | 28,010 spans |
| Independent supports | 29,764 |
| Running rail | 1,267.99 rail-km / 76,346 t |
| Complete fastening sets | 2,218,987 |
| Protected at-grade crossing packages | 233 |
| Bridge runs / tunnel portals | 363 / 0 |
| Additional station track | 10,560 m |
| Access connector allowance | 2,051.5 m; actual accessible paths require survey |
| Pooled depot area | 277,576 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.31m | $6.70m | $37.83m |
| Civil production campaign | $8.03m | $39.39m | $235.17m |

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
| low | make | 11 | 98,035 | 728,260 | 971,013 |
| base | make | 27 | 238,085 | 1,904,680 | 2,539,573 |
| high | make | 72 | 644,230 | 5,265,880 | 7,021,173 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 68 | Unestablished | 491,436 | 245.7 |
| Vehicle production / low | 56 | 112 | Unestablished | Unestablished |
| Civil field / low | 103 | 206 | 1,064,416 | Unestablished |
| Civil other installation / low | 1,170 | 2,340 | 12,165,346 | Unestablished |
| Civil precast / low | 88 | 176 | 971,013 | Unestablished |
| Control room and access-site coverage / base | 136 | Unestablished | 1,116,900 | 558.5 |
| Vehicle production / base | 160 | 320 | Unestablished | Unestablished |
| Civil field / base | 380 | 760 | 3,342,635 | Unestablished |
| Civil other installation / base | 8,449 | 16,898 | 74,347,391 | Unestablished |
| Civil precast / base | 216 | 432 | 2,539,573 | Unestablished |
| Control room and access-site coverage / high | 272 | Unestablished | 2,680,560 | 1,340.3 |
| Vehicle production / high | 437 | 874 | Unestablished | Unestablished |
| Civil field / high | 1,654 | 3,308 | 9,262,261 | Unestablished |
| Civil other installation / high | 84,555 | 169,110 | 473,503,047 | Unestablished |
| Civil precast / high | 576 | 1,152 | 7,021,173 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 132 | 542.0 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.837bn | $6.876bn | $42.655bn |
| Installed capital / route-km | $5.89m | $22.06m | $136.84m |
| 30-year whole-life NPV | $3.519bn | $12.704bn | $74.138bn |
| Annual operating provision | $78.34m | $257.48m | $1.295bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.199bn | $1.199bn |
| Guideway | $429.12m | $429.12m |
| Stations power | $1.108bn | $1.108bn |
| Factory tooling | $46.09m | $46.09m |
| Construction | $3.642bn | $3.642bn |
| Land utilities depot | $304.84m | $304.84m |
| Fleet | $111.50m | $111.50m |
| Energy | $0 | $2.582bn |
| Operations | $0 | $151.09m |
| Maintenance | $0 | $1.578bn |
| Renewals | $0 | $1.312bn |
| Recovery | $34.77m | $70.84m |
| Reliability | $0 | $105.54m |
| Disposal | $0 | $63.60m |

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
| City project risk contingency | $1.375bn | 20.0% |
| Bridge special foundations deck temporary | $1.246bn | 18.1% |
| Network delivered assembled fleet | $969.72m | 14.1% |
| Design prototypes independent review | $406.45m | 5.9% |
| Shared access and transfer complexes | $218.21m | 3.2% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.837bn | $6.876bn | $42.655bn |
| Water-evidence alternative capital | $1.799bn | $6.647bn | $40.789bn |
| Alternative capital / route-km | $5.77m | $21.33m | $130.85m |
| Alternative whole-life NPV | $3.481bn | $12.476bn | $72.254bn |
| Included non-water obstruction reserve | $1.10m | $7.35m | $51.47m |

14.71 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 68 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-233.23m | $-12.284bn | -0.52 |
| 50% | 97.01m | 0.50 | $48.51m | $-208.97m | $-11.865bn | -0.47 |
| 50% | 97.01m | 1.00 | $97.01m | $-160.47m | $-11.026bn | -0.36 |
| 75% | 145.52m | 0.25 | $36.38m | $-221.10m | $-12.075bn | -0.50 |
| 75% | 145.52m | 0.50 | $72.76m | $-184.72m | $-11.446bn | -0.42 |
| 75% | 145.52m | 1.00 | $145.52m | $-111.96m | $-10.188bn | -0.25 |
| 100% | 194.02m | 0.25 | $48.51m | $-208.97m | $-11.865bn | -0.47 |
| 100% | 194.02m | 0.50 | $97.01m | $-160.47m | $-11.026bn | -0.36 |
| 100% | 194.02m | 1.00 | $194.02m | $-63.46m | $-9.349bn | -0.14 |

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
| low | $1.286bn | $551.00m | $118.88m |
| base | $4.813bn | $2.063bn | $445.05m |
| high | $29.858bn | $12.796bn | $2.761bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/surabaya.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/southeast-asia/Indonesia/Surabaya) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `6f20bba6f82aa29a8d25ff2a41b26f6d61b598e2115bfb6347165fd9e75685fc` |
| cost_evaluation_id | `ffdad47bdc59876861f706b8478e0de5546b5edc1c355c6213af97c963c3b945` |
| outline_evaluation_id | `c98a92d5af8f7c0bd434d8978bade184b1c25626efad8a73b043a264939fe94e` |
| research_configuration_id | `f6bf631e0dcb00030429238014d66fd8c7f9d961aeb95619591d94226409546b` |
| seed_id | `88029cebe1dd03be30d831301831306aef8bccadb74e802bfd4659bc5c2c8d08` |
| selected_alignment_id | `e2276be01e0c1174bef9fbd3a311133d8704c8bc986c328aceee73ef806cd3ea` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `c0e95eaa603ec037528cf5a3ed0144614933ba1880a4e976052e6620320fb43f` |
| source_result_sha256 | `bbdcb4e48b2597b2a704bd3a7c47dbcffc7b45bcc33ed4af0b18ef1d2d7be0d3` |

Atlas packet `8ef7d18074da34132ac6f435e198ba8b4b9f7203f22180ac770b4c4a38c3db2c`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
