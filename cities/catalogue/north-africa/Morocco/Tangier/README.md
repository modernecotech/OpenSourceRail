# Tangier — railway design and city programme

**MA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=tangier) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=tangier) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Tangier current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,200,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 199.43 km / 2 trackways |
| Lines / operational platform groups | 8 / 82 |
| Original access markers / separately costed access sites | 88 / 43 |
| Explicit interchange references | 20 |
| Fleet including reserve | 233 six-car trainsets |
| Train distance | 129,233 train-km/day; 47,170,149 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 24.89 | 13 | 200 | 40.2 | 26 + 4 | 4,181 | W terminal ↔ E terminal |
| line-2 | 36.85 | 15 | 200 | 55.4 | 36 + 6 | 4,181 | W terminal ↔ NE terminal |
| line-3 | 22.63 | 10 | 200 | 33.7 | 23 + 4 | 4,181 | SW terminal ↔ E terminal |
| line-4 | 24.35 | 8 | 200 | 38.5 | 25 + 4 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 59.99 | 21 | 200 | 88.1 | 54 + 9 | 4,181 | Ring / closed circuit |
| line-6 | 9.27 | 3 | 200 | 11.1 | 9 + 2 | 4,181 | NE terminal ↔ NE terminal |
| line-7 | 8.42 | 6 | 200 | 16.6 | 12 + 2 | 4,181 | W terminal ↔ W terminal |
| line-8 | 13.04 | 6 | 200 | 18.9 | 14 + 3 | 4,181 | SW terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 41.22 | False | Unestablished |
| 800.00 | 13.33 | 164.87 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 529,082 kWh mechanical | 193.11 GWh mechanical |
| Nominal auxiliary load | 752,220 kWh | 274.56 GWh |
| Auxiliary supply including scenario charging losses | 791,811 kWh | 289.01 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.94 GWh |
| Total priced grid-supply scenario | See annual budget | 534.92 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $34.26m | $88.56m | $266.33m |

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
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 24.89 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 36.85 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 22.63 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 59.99 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 9.27 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 13.04 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,556.8 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 6,158.2 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,041.8 m | 5,554.5 m |
| line-5 | 4 | Coast stops before receiving zone | 6,809.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,310.8 m | 5,554.5 m |
| line-8 | 2 | Coast stops before receiving zone | 6,061.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 16.22 km |
| Bridge route | 1.87 km |
| Elevated route | 181.34 km |
| Tunnel route | 0.00 km |
| Precast span stock | 18,450 spans |
| Independent supports | 18,696 |
| Running rail | 797.74 rail-km / 48,032 t |
| Complete fastening sets | 1,396,039 |
| Protected at-grade crossing packages | 67 |
| Bridge runs / tunnel portals | 33 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 457.6 m; actual accessible paths require survey |
| Pooled depot area | 163,228 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $898,384 | $3.86m | $24.51m |
| Civil production campaign | $5.51m | $26.59m | $157.98m |

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
| low | make | 8 | 64,575 | 479,700 | 639,600 |
| base | make | 18 | 156,825 | 1,254,600 | 1,672,800 |
| high | make | 48 | 424,350 | 3,468,600 | 4,624,800 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 45 | Unestablished | 325,215 | 162.6 |
| Vehicle production / low | 33 | 66 | Unestablished | Unestablished |
| Civil field / low | 67 | 134 | 691,424 | Unestablished |
| Civil other installation / low | 382 | 764 | 3,966,145 | Unestablished |
| Civil precast / low | 64 | 128 | 639,600 | Unestablished |
| Control room and access-site coverage / base | 90 | Unestablished | 739,125 | 369.6 |
| Vehicle production / base | 94 | 188 | Unestablished | Unestablished |
| Civil field / base | 247 | 494 | 2,172,672 | Unestablished |
| Civil other installation / base | 2,666 | 5,332 | 23,456,242 | Unestablished |
| Civil precast / base | 144 | 288 | 1,672,800 | Unestablished |
| Control room and access-site coverage / high | 180 | Unestablished | 1,773,900 | 887.0 |
| Vehicle production / high | 256 | 512 | Unestablished | Unestablished |
| Civil field / high | 1,076 | 2,152 | 6,023,392 | Unestablished |
| Civil other installation / high | 26,401 | 52,802 | 147,841,965 | Unestablished |
| Civil precast / high | 384 | 768 | 4,624,800 | Unestablished |

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
| Installed capital | $888.96m | $3.090bn | $18.220bn |
| Installed capital / route-km | $4.46m | $15.49m | $91.36m |
| 30-year whole-life NPV | $1.856bn | $6.424bn | $36.324bn |
| Annual operating provision | $45.73m | $149.96m | $759.32m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $741.10m | $741.10m |
| Guideway | $278.53m | $278.53m |
| Stations power | $466.01m | $466.01m |
| Factory tooling | $30.45m | $30.45m |
| Construction | $1.292bn | $1.292bn |
| Land utilities depot | $191.49m | $191.49m |
| Fleet | $67.61m | $67.61m |
| Energy | $0 | $1.531bn |
| Operations | $0 | $99.98m |
| Maintenance | $0 | $870.03m |
| Renewals | $0 | $712.76m |
| Recovery | $23.18m | $47.23m |
| Reliability | $0 | $67.52m |
| Disposal | $0 | $28.58m |

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
| City project risk contingency | $617.98m | 20.0% |
| Network delivered assembled fleet | $567.70m | 18.4% |
| Design prototypes independent review | $182.67m | 5.9% |
| Shared access and transfer complexes | $136.75m | 4.4% |
| Repeat box beams | $135.77m | 4.4% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $888.96m | $3.090bn | $18.220bn |
| Water-evidence alternative capital | $893.65m | $3.117bn | $18.434bn |
| Alternative capital / route-km | $4.48m | $15.63m | $92.43m |
| Alternative whole-life NPV | $1.860bn | $6.452bn | $36.547bn |
| Included non-water obstruction reserve | $116,434 | $776,230 | $5.43m |

1.55 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 10 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-128.40m | $-6.051bn | -0.64 |
| 50% | 86.23m | 0.50 | $43.12m | $-106.84m | $-5.679bn | -0.53 |
| 50% | 86.23m | 1.00 | $86.23m | $-63.72m | $-4.933bn | -0.32 |
| 75% | 129.35m | 0.25 | $32.34m | $-117.62m | $-5.865bn | -0.59 |
| 75% | 129.35m | 0.50 | $64.67m | $-85.28m | $-5.306bn | -0.43 |
| 75% | 129.35m | 1.00 | $129.35m | $-20.61m | $-4.188bn | -0.10 |
| 100% | 172.46m | 0.25 | $43.12m | $-106.84m | $-5.679bn | -0.53 |
| 100% | 172.46m | 0.50 | $86.23m | $-63.72m | $-4.933bn | -0.32 |
| 100% | 172.46m | 1.00 | $172.46m | $22.51m | $-3.442bn | 0.11 |

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
| low | $622.27m | $266.69m | $57.54m |
| base | $2.163bn | $926.97m | $199.99m |
| high | $12.754bn | $5.466bn | $1.179bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/tangier.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/north-africa/Morocco/Tangier) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `cbca30d54fe77690f9f0c40b25539493aba65ef242d69c942096b8b169f318b5` |
| cost_evaluation_id | `a1fe207d2ee1ee1da3e8bb4292fb9b1347d752f7dc992325b945d89b5f2a8488` |
| outline_evaluation_id | `8b3a07e77caa079fb6ab500d8d57382bdf864040103074b61a4ba0ed2a5adb4c` |
| research_configuration_id | `8967ea2eca9f02f4839758976bd35a14c698d5c7b082ec514f622373108257f6` |
| seed_id | `d078ce295d0907168d0002d00878b897ce35305a66c29b0fbee9e97ca0b02868` |
| selected_alignment_id | `1c7e31e8ba8b2f15a6fcdcd12bb83fff4ed451d3e56350b9b035d8e7c51da5cd` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `e5cd2d3104d9bce03078abc0578b162e1ebae315442b46b4ca22c95bb490e88b` |
| source_result_sha256 | `1e1981dfdfb56d23097fe2a4ea5083923ea8fab4e6b56adecdfa75965d9ba6f7` |

Atlas packet `ee89c7a022dd2f26c77f87297474fb3ffcdcd856e4f8512b552ec41a36d847aa`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
