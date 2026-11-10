# Omdurman — railway design and city programme

**SD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=omdurman) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=omdurman) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Omdurman current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,800,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 308.88 km / 2 trackways |
| Lines / operational platform groups | 9 / 142 |
| Original access markers / separately costed access sites | 168 / 66 |
| Explicit interchange references | 37 |
| Fleet including reserve | 359 six-car trainsets |
| Train distance | 200,153 train-km/day; 73,055,968 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 40.73 | 22 | 200 | 66.4 | 42 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-2 | 48.19 | 30 | 200 | 83.5 | 52 + 8 | 4,181 | NE terminal ↔ SW terminal |
| line-3 | 41.19 | 14 | 200 | 58.2 | 37 + 6 | 4,181 | N terminal ↔ SE terminal |
| line-4 | 43.56 | 32 | 200 | 80.6 | 51 + 8 | 4,181 | NW terminal ↔ E terminal |
| line-5 | 26.63 | 12 | 200 | 46.1 | 30 + 5 | 4,181 | E terminal ↔ W terminal |
| line-6 | 88.13 | 25 | 200 | 123.7 | 76 + 12 | 4,181 | Ring / closed circuit |
| line-7 | 6.34 | 2 | 200 | 6.3 | 6 + 1 | 4,181 | SE terminal ↔ S terminal |
| line-8 | 6.74 | 2 | 200 | 6.7 | 6 + 1 | 4,181 | NW terminal ↔ NW terminal |
| line-9 | 7.36 | 3 | 200 | 10.8 | 9 + 2 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 71.38 | False | Unestablished |
| 800.00 | 13.33 | 285.51 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 868,380 kWh mechanical | 316.96 GWh mechanical |
| Nominal auxiliary load | 1,168,020 kWh | 426.33 GWh |
| Auxiliary supply including scenario charging losses | 1,229,495 kWh | 448.77 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.26 GWh |
| Total priced grid-supply scenario | See annual budget | 848.93 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $54.34m | $140.55m | $423.46m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 40.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 48.19 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 41.19 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 43.56 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 88.13 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 6.34 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 6.74 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,030.3 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,642.9 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,985.3 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,995.6 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,263.3 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,343.8 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,742.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 36.63 km |
| Bridge route | 6.10 km |
| Elevated route | 266.14 km |
| Tunnel route | 0.00 km |
| Precast span stock | 27,530 spans |
| Independent supports | 28,280 |
| Running rail | 1,235.51 rail-km / 74,390 t |
| Complete fastening sets | 2,162,151 |
| Protected at-grade crossing packages | 331 |
| Bridge runs / tunnel portals | 23 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,865.8 m; actual accessible paths require survey |
| Pooled depot area | 250,276 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.22m | $5.38m | $35.22m |
| Civil production campaign | $7.90m | $38.81m | $231.54m |

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
| low | make | 11 | 96,355 | 715,780 | 954,373 |
| base | make | 27 | 234,005 | 1,872,040 | 2,496,053 |
| high | make | 71 | 633,190 | 5,175,640 | 6,900,853 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 68 | Unestablished | 491,436 | 245.7 |
| Vehicle production / low | 51 | 102 | Unestablished | Unestablished |
| Civil field / low | 100 | 200 | 1,035,787 | Unestablished |
| Civil other installation / low | 614 | 1,228 | 6,376,625 | Unestablished |
| Civil precast / low | 88 | 176 | 954,373 | Unestablished |
| Control room and access-site coverage / base | 136 | Unestablished | 1,116,900 | 558.5 |
| Vehicle production / base | 144 | 288 | Unestablished | Unestablished |
| Civil field / base | 370 | 740 | 3,254,187 | Unestablished |
| Civil other installation / base | 4,383 | 8,766 | 38,566,475 | Unestablished |
| Civil precast / base | 216 | 432 | 2,496,053 | Unestablished |
| Control room and access-site coverage / high | 272 | Unestablished | 2,680,560 | 1,340.3 |
| Vehicle production / high | 395 | 790 | Unestablished | Unestablished |
| Civil field / high | 1,611 | 3,222 | 9,020,427 | Unestablished |
| Civil other installation / high | 43,913 | 87,826 | 245,911,604 | Unestablished |
| Civil precast / high | 568 | 1,136 | 6,900,853 | Unestablished |

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
| Installed capital | $1.396bn | $4.888bn | $28.954bn |
| Installed capital / route-km | $4.52m | $15.82m | $93.74m |
| 30-year whole-life NPV | $2.917bn | $10.106bn | $57.140bn |
| Annual operating provision | $72.05m | $235.24m | $1.183bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.160bn | $1.160bn |
| Guideway | $420.58m | $420.58m |
| Stations power | $723.54m | $723.54m |
| Factory tooling | $44.19m | $44.19m |
| Construction | $2.110bn | $2.110bn |
| Land utilities depot | $289.91m | $289.91m |
| Fleet | $105.26m | $105.26m |
| Energy | $0 | $2.430bn |
| Operations | $0 | $151.09m |
| Maintenance | $0 | $1.346bn |
| Renewals | $0 | $1.106bn |
| Recovery | $34.77m | $70.84m |
| Reliability | $0 | $104.58m |
| Disposal | $0 | $45.21m |

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
| City project risk contingency | $977.58m | 20.0% |
| Network delivered assembled fleet | $874.70m | 17.9% |
| Design prototypes independent review | $288.98m | 5.9% |
| Shared access and transfer complexes | $216.21m | 4.4% |
| Repeat box beams | $202.59m | 4.1% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.396bn | $4.888bn | $28.954bn |
| Water-evidence alternative capital | $1.441bn | $5.146bn | $31.041bn |
| Alternative capital / route-km | $4.66m | $16.66m | $100.50m |
| Alternative whole-life NPV | $2.962bn | $10.369bn | $59.295bn |
| Included non-water obstruction reserve | $69,340 | $462,269 | $3.24m |

0.92 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 1 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-210.99m | $-9.687bn | -0.67 |
| 50% | 97.01m | 0.50 | $48.51m | $-186.74m | $-9.268bn | -0.59 |
| 50% | 97.01m | 1.00 | $97.01m | $-138.23m | $-8.429bn | -0.44 |
| 75% | 145.52m | 0.25 | $36.38m | $-198.86m | $-9.477bn | -0.63 |
| 75% | 145.52m | 0.50 | $72.76m | $-162.48m | $-8.848bn | -0.51 |
| 75% | 145.52m | 1.00 | $145.52m | $-89.73m | $-7.590bn | -0.28 |
| 100% | 194.02m | 0.25 | $48.51m | $-186.74m | $-9.268bn | -0.59 |
| 100% | 194.02m | 0.50 | $97.01m | $-138.23m | $-8.429bn | -0.44 |
| 100% | 194.02m | 1.00 | $194.02m | $-41.22m | $-6.751bn | -0.13 |

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
| low | $976.97m | $418.70m | $90.33m |
| base | $3.422bn | $1.466bn | $316.36m |
| high | $20.268bn | $8.686bn | $1.874bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/omdurman.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/north-africa/Sudan/Omdurman) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `d59d8aef8c759fcf6a109d60f84d9f084e90a4b25f7c99df1700e67d2314f2f9` |
| cost_evaluation_id | `692ddc844677309db5ce56e17912ad39fecfb712bec89bbd2df7d80d098343c5` |
| outline_evaluation_id | `1f072dbea9260c84f529cc71a3f9483f982d69d8424ab10d373012e046af7b5a` |
| research_configuration_id | `e9982e1f3bafbfad08366471b22962ac42a10dd546755203ab1d2f46c69c677b` |
| seed_id | `72c955c981fc2bc5d4c15e897a43066770802d4954575143edc047b6b1b342cd` |
| selected_alignment_id | `d97523e8c681e26f46bef211a44e141728ad5fcbf85f8bbaec4a8cb1ee600fcf` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `598fa9a2c6fb4f326753adc837278a218dd7bb2e48f5f766a795234f575d8702` |
| source_result_sha256 | `677fa4e560412f88c758848befd566dce19665c67d447ece3f58c635f96ee87c` |

Atlas packet `d2301ddae9cc17d76cca21c5b58b0f16333509d0a5314184a8500aa814af1717`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
