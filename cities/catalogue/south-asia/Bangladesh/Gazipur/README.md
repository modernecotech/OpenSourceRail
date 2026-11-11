# Gazipur — railway design and city programme

**BD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=gazipur) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=gazipur) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Gazipur current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,400,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 289.66 km / 2 trackways |
| Lines / operational platform groups | 9 / 93 |
| Original access markers / separately costed access sites | 97 / 61 |
| Explicit interchange references | 26 |
| Fleet including reserve | 312 six-car trainsets |
| Train distance | 187,700 train-km/day; 68,510,527 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 39.71 | 15 | 200 | 68.6 | 43 + 7 | 4,181 | S terminal ↔ NE terminal |
| line-2 | 36.15 | 11 | 200 | 48.4 | 31 + 5 | 4,181 | W terminal ↔ E terminal |
| line-3 | 46.86 | 16 | 200 | 65.8 | 42 + 7 | 4,181 | NE terminal ↔ SW terminal |
| line-4 | 50.45 | 14 | 200 | 68.4 | 43 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 30.43 | 9 | 200 | 40.8 | 27 + 5 | 4,181 | N terminal ↔ S terminal |
| line-6 | 66.49 | 19 | 200 | 92.2 | 56 + 9 | 4,181 | Ring / closed circuit |
| line-7 | 7.47 | 3 | 200 | 9.4 | 8 + 2 | 4,181 | SE terminal ↔ S terminal |
| line-8 | 5.49 | 3 | 200 | 7.9 | 7 + 2 | 4,181 | S terminal ↔ S terminal |
| line-9 | 6.61 | 3 | 200 | 10.6 | 9 + 2 | 4,181 | NW terminal ↔ NE terminal |

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
| Mechanical traction work | 732,007 kWh mechanical | 267.18 GWh mechanical |
| Nominal auxiliary load | 1,005,480 kWh | 367.00 GWh |
| Auxiliary supply including scenario charging losses | 1,058,400 kWh | 386.32 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 6.68 GWh |
| Total priced grid-supply scenario | See annual budget | 726.51 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $46.53m | $120.28m | $361.84m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 36.15 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 46.86 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 50.45 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 30.43 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 66.49 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 7.47 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 6,107.3 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,695.0 m | 5,554.5 m |
| line-4 | 3 | Coast stops before receiving zone | 6,001.9 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,425.6 m | 5,554.5 m |
| line-6 | 2 | Coast stops before receiving zone | 6,084.0 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,770.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 64.80 km |
| Bridge route | 15.75 km |
| Elevated route | 209.11 km |
| Tunnel route | 0.00 km |
| Precast span stock | 23,052 spans |
| Independent supports | 24,326 |
| Running rail | 1,158.64 rail-km / 69,762 t |
| Complete fastening sets | 2,027,625 |
| Protected at-grade crossing packages | 417 |
| Bridge runs / tunnel portals | 142 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 308.4 m; actual accessible paths require survey |
| Pooled depot area | 218,400 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.14m | $4.80m | $29.97m |
| Civil production campaign | $6.69m | $32.73m | $194.95m |

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
| low | make | 9 | 80,682 | 599,352 | 799,136 |
| base | make | 22 | 195,942 | 1,567,536 | 2,090,048 |
| high | make | 59 | 530,196 | 4,333,776 | 5,778,368 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 63 | Unestablished | 455,301 | 227.7 |
| Vehicle production / low | 44 | 88 | Unestablished | Unestablished |
| Civil field / low | 85 | 170 | 874,197 | Unestablished |
| Civil other installation / low | 663 | 1,326 | 6,890,439 | Unestablished |
| Civil precast / low | 72 | 144 | 799,136 | Unestablished |
| Control room and access-site coverage / base | 126 | Unestablished | 1,034,775 | 517.4 |
| Vehicle production / base | 125 | 250 | Unestablished | Unestablished |
| Civil field / base | 312 | 624 | 2,745,536 | Unestablished |
| Civil other installation / base | 5,080 | 10,160 | 44,701,529 | Unestablished |
| Civil precast / base | 176 | 352 | 2,090,048 | Unestablished |
| Control room and access-site coverage / high | 252 | Unestablished | 2,483,460 | 1,241.7 |
| Vehicle production / high | 343 | 686 | Unestablished | Unestablished |
| Civil field / high | 1,359 | 2,718 | 7,608,299 | Unestablished |
| Civil other installation / high | 53,251 | 106,502 | 298,202,180 | Unestablished |
| Civil precast / high | 472 | 944 | 5,778,368 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 122 | 501.0 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.297bn | $4.797bn | $29.784bn |
| Installed capital / route-km | $4.48m | $16.56m | $102.82m |
| 30-year whole-life NPV | $2.600bn | $9.306bn | $54.372bn |
| Annual operating provision | $61.96m | $203.07m | $1.028bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $981.28m | $981.28m |
| Guideway | $365.83m | $365.83m |
| Stations power | $622.68m | $622.68m |
| Factory tooling | $37.52m | $37.52m |
| Construction | $2.402bn | $2.402bn |
| Land utilities depot | $264.79m | $264.79m |
| Fleet | $89.87m | $89.87m |
| Energy | $0 | $2.080bn |
| Operations | $0 | $139.98m |
| Maintenance | $0 | $1.159bn |
| Renewals | $0 | $952.80m |
| Recovery | $33.11m | $67.47m |
| Reliability | $0 | $98.07m |
| Disposal | $0 | $44.37m |

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
| City project risk contingency | $959.37m | 20.0% |
| Network delivered assembled fleet | $760.18m | 15.8% |
| Bridge special foundations deck temporary | $559.63m | 11.7% |
| Design prototypes independent review | $283.68m | 5.9% |
| Surface formation drainage crossings | $196.89m | 4.1% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.297bn | $4.797bn | $29.784bn |
| Water-evidence alternative capital | $1.257bn | $4.564bn | $27.888bn |
| Alternative capital / route-km | $4.34m | $15.76m | $96.28m |
| Alternative whole-life NPV | $2.560bn | $9.071bn | $52.434bn |
| Included non-water obstruction reserve | $767,532 | $5.12m | $35.82m |

10.23 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 29 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-178.82m | $-8.886bn | -0.58 |
| 50% | 97.01m | 0.50 | $48.51m | $-154.57m | $-8.467bn | -0.50 |
| 50% | 97.01m | 1.00 | $97.01m | $-106.06m | $-7.628bn | -0.34 |
| 75% | 145.52m | 0.25 | $36.38m | $-166.69m | $-8.676bn | -0.54 |
| 75% | 145.52m | 0.50 | $72.76m | $-130.32m | $-8.047bn | -0.42 |
| 75% | 145.52m | 1.00 | $145.52m | $-57.56m | $-6.789bn | -0.19 |
| 100% | 194.02m | 0.25 | $48.51m | $-154.57m | $-8.467bn | -0.50 |
| 100% | 194.02m | 0.50 | $97.01m | $-106.06m | $-7.628bn | -0.34 |
| 100% | 194.02m | 1.00 | $194.02m | $-9.05m | $-5.951bn | -0.03 |

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
| low | $908.05m | $389.16m | $83.96m |
| base | $3.358bn | $1.439bn | $310.47m |
| high | $20.849bn | $8.935bn | $1.928bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/gazipur.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Bangladesh/Gazipur) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `c2f779cbbfff32b098b142ca40a9a7c2898d7b72e4c574ad7cc1f439bff5c089` |
| cost_evaluation_id | `bfc50a51de58288b7cd6b9ab59036a4a037bce5a49610cf5af0bd903f66db41e` |
| outline_evaluation_id | `dd6aecab2a5927571f770a6954433f7e0c5b224e087932b2cec295c50eace5d7` |
| research_configuration_id | `56ebfaafc1b1ea6a3f1ddad6682602f89077e3e6cb25cea2dbab81310320209e` |
| seed_id | `b9935ab8fead072b8b4ede9cb8812ecc0a4575df7bcc8da239453fe51a64b3ca` |
| selected_alignment_id | `7c0549311cb70a9cdc47ea842c3669eb4721ed68b1da670e4c7535d3130b7128` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `ab782bb6f14f42dde440c41be0effd0c85833e14c118ca99c75b5881a6452a9d` |
| source_result_sha256 | `237463f52fd41c38a9c42fb386034f4134064d39c5b6ad6a98911a4d2052d148` |

Atlas packet `a8b2f945aad22870466735f3fa7f6a05c0859d5b9d14d48156c1f8c00f015c85`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
