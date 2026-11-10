# Ranchi — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=ranchi) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=ranchi) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Ranchi current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,400,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 228.95 km / 2 trackways |
| Lines / operational platform groups | 6 / 84 |
| Original access markers / separately costed access sites | 106 / 48 |
| Explicit interchange references | 17 |
| Fleet including reserve | 263 six-car trainsets |
| Train distance | 148,360 train-km/day; 54,151,416 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 36.51 | 15 | 200 | 65.4 | 42 + 7 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 28.57 | 14 | 200 | 45.3 | 29 + 5 | 4,181 | N terminal ↔ S terminal |
| line-3 | 25.88 | 13 | 200 | 52.5 | 34 + 6 | 4,181 | SE terminal ↔ W terminal |
| line-4 | 30.62 | 9 | 200 | 40.8 | 27 + 5 | 4,181 | E terminal ↔ SW terminal |
| line-5 | 29.47 | 10 | 200 | 41.8 | 27 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-6 | 77.89 | 23 | 200 | 108.2 | 66 + 10 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

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
| Mechanical traction work | 549,223 kWh mechanical | 200.47 GWh mechanical |
| Nominal auxiliary load | 850,500 kWh | 310.43 GWh |
| Auxiliary supply including scenario charging losses | 895,263 kWh | 326.77 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.52 GWh |
| Total priced grid-supply scenario | See annual budget | 584.18 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $37.53m | $96.72m | $289.05m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 28.57 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 30.62 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 29.47 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 77.89 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 6,680.0 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,425.6 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,861.9 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,054.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 19.35 km |
| Bridge route | 2.16 km |
| Elevated route | 207.44 km |
| Tunnel route | 0.00 km |
| Precast span stock | 21,428 spans |
| Independent supports | 21,880 |
| Running rail | 927.24 rail-km / 55,829 t |
| Complete fastening sets | 1,622,675 |
| Protected at-grade crossing packages | 139 |
| Bridge runs / tunnel portals | 37 / 0 |
| Additional station track | 5,720 m |
| Access connector allowance | 1,565.9 m; actual accessible paths require survey |
| Pooled depot area | 184,132 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $26.35m |
| Civil production campaign | $6.31m | $30.65m | $181.81m |

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
| low | make | 9 | 74,998 | 557,128 | 742,837 |
| base | make | 21 | 182,138 | 1,457,104 | 1,942,805 |
| high | make | 55 | 492,844 | 4,028,464 | 5,371,285 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 50 | Unestablished | 361,350 | 180.7 |
| Vehicle production / low | 37 | 74 | Unestablished | Unestablished |
| Civil field / low | 78 | 156 | 804,800 | Unestablished |
| Civil other installation / low | 519 | 1,038 | 5,387,786 | Unestablished |
| Civil precast / low | 72 | 144 | 742,837 | Unestablished |
| Control room and access-site coverage / base | 100 | Unestablished | 821,250 | 410.6 |
| Vehicle production / base | 106 | 212 | Unestablished | Unestablished |
| Civil field / base | 288 | 576 | 2,528,683 | Unestablished |
| Civil other installation / base | 3,401 | 6,802 | 29,925,041 | Unestablished |
| Civil precast / base | 168 | 336 | 1,942,805 | Unestablished |
| Control room and access-site coverage / high | 200 | Unestablished | 1,971,000 | 985.5 |
| Vehicle production / high | 289 | 578 | Unestablished | Unestablished |
| Civil field / high | 1,252 | 2,504 | 7,009,813 | Unestablished |
| Civil other installation / high | 31,862 | 63,724 | 178,426,964 | Unestablished |
| Civil precast / high | 440 | 880 | 5,371,285 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 96 | 394.2 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.054bn | $3.645bn | $21.285bn |
| Installed capital / route-km | $4.60m | $15.92m | $92.97m |
| 30-year whole-life NPV | $2.140bn | $7.428bn | $41.860bn |
| Annual operating provision | $50.99m | $168.56m | $859.33m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $800.38m | $800.38m |
| Guideway | $323.57m | $323.57m |
| Stations power | $638.60m | $638.60m |
| Factory tooling | $34.86m | $34.86m |
| Construction | $1.531bn | $1.531bn |
| Land utilities depot | $215.44m | $215.44m |
| Fleet | $74.15m | $74.15m |
| Energy | $0 | $1.672bn |
| Operations | $0 | $111.09m |
| Maintenance | $0 | $1.026bn |
| Renewals | $0 | $835.19m |
| Recovery | $26.49m | $53.97m |
| Reliability | $0 | $77.52m |
| Disposal | $0 | $33.71m |

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
| City project risk contingency | $728.96m | 20.0% |
| Network delivered assembled fleet | $640.80m | 17.6% |
| Design prototypes independent review | $215.40m | 5.9% |
| Repeat box beams | $157.68m | 4.3% |
| Shared access and transfer complexes | $147.33m | 4.0% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.054bn | $3.645bn | $21.285bn |
| Water-evidence alternative capital | $1.046bn | $3.600bn | $20.920bn |
| Alternative capital / route-km | $4.57m | $15.72m | $91.37m |
| Alternative whole-life NPV | $2.133bn | $7.383bn | $41.487bn |
| Included non-water obstruction reserve | $130,149 | $867,657 | $6.07m |

1.74 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 1 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 64.67m | 0.25 | $16.17m | $-152.39m | $-7.149bn | -0.65 |
| 50% | 64.67m | 0.50 | $32.34m | $-136.22m | $-6.869bn | -0.58 |
| 50% | 64.67m | 1.00 | $64.67m | $-103.88m | $-6.310bn | -0.44 |
| 75% | 97.01m | 0.25 | $24.25m | $-144.30m | $-7.009bn | -0.61 |
| 75% | 97.01m | 0.50 | $48.51m | $-120.05m | $-6.590bn | -0.51 |
| 75% | 97.01m | 1.00 | $97.01m | $-71.54m | $-5.751bn | -0.30 |
| 100% | 129.35m | 0.25 | $32.34m | $-136.22m | $-6.869bn | -0.58 |
| 100% | 129.35m | 0.50 | $64.67m | $-103.88m | $-6.310bn | -0.44 |
| 100% | 129.35m | 1.00 | $129.35m | $-39.21m | $-5.192bn | -0.17 |

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
| low | $737.73m | $316.17m | $68.21m |
| base | $2.551bn | $1.093bn | $235.91m |
| high | $14.900bn | $6.386bn | $1.378bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/ranchi.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Ranchi) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `2291e9849805b312acde8fa7acc74f8f6a7d6e57aab28858ef0f9ce4f5314696` |
| cost_evaluation_id | `0291ef9c13633b5fc2e401ae82cf6b0e7bdddec72e43ceb9ca8ccde313e6eab2` |
| outline_evaluation_id | `7e68ffef2d52ce85f5931ddf64e103a770a34a7f24c20640b0ef7bc3de440bf9` |
| research_configuration_id | `e367eae99df34b50cd8c76a5b5a7a6e38e7f7a87dd333a6379f83127a7d9f82a` |
| seed_id | `8c6426bdd51ff59cd887a64119c3f31a321e175d6777687052cf0218353f175f` |
| selected_alignment_id | `9edee6a05f2fe4d4db77ff93fb2e7323a21544c7cf4a4cc452c390a80c58c413` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `208851a3aa4973da417eb583718fb8542ef81856991c4b2477d7489780354da5` |
| source_result_sha256 | `0967fb993b353532c9b4960f1b9702d1720cbeee6e320579d31b1557c1e4cee0` |

Atlas packet `41645bb6f70839752e9dbca92f2c8594fb8921df9abdc3cfc8bb56b0fa61365b`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
