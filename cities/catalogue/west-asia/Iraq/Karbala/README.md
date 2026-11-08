# Karbala — railway design and city programme

**IQ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=karbala) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=karbala) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Karbala current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,390,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 179.30 km / 2 trackways |
| Lines / operational platform groups | 9 / 65 |
| Original access markers / separately costed access sites | 69 / 37 |
| Explicit interchange references | 17 |
| Fleet including reserve | 211 six-car trainsets |
| Train distance | 116,189 train-km/day; 42,409,054 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 21.70 | 8 | 200 | 30.4 | 21 + 4 | 4,181 | E terminal ↔ W terminal |
| line-2 | 16.66 | 8 | 200 | 30.4 | 21 + 4 | 4,181 | SW terminal ↔ N terminal |
| line-3 | 19.23 | 8 | 200 | 32.6 | 22 + 4 | 4,181 | SE terminal ↔ W terminal |
| line-4 | 21.71 | 6 | 200 | 28.1 | 19 + 3 | 4,181 | E terminal ↔ NW terminal |
| line-5 | 24.70 | 10 | 200 | 36.9 | 24 + 4 | 4,181 | SW terminal ↔ NE terminal |
| line-6 | 55.41 | 16 | 200 | 78.9 | 48 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 4.14 | 2 | 200 | 5.6 | 6 + 1 | 4,181 | SW terminal ↔ SE terminal |
| line-8 | 7.79 | 4 | 200 | 13.1 | 10 + 2 | 4,181 | N terminal ↔ NW terminal |
| line-9 | 7.98 | 3 | 200 | 9.9 | 8 + 2 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 32.67 | False | Unestablished |
| 800.00 | 13.33 | 130.69 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 446,121 kWh mechanical | 162.83 GWh mechanical |
| Nominal auxiliary load | 676,620 kWh | 246.97 GWh |
| Auxiliary supply including scenario charging losses | 712,232 kWh | 259.96 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.65 GWh |
| Total priced grid-supply scenario | See annual budget | 469.18 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $30.15m | $77.68m | $231.88m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 21.70 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 21.71 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 24.70 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 55.41 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 7.98 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,299.1 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,687.0 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,574.4 m | 5,554.5 m |
| line-6 | 4 | Coast stops before receiving zone | 5,988.6 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,025.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 22.97 km |
| Bridge route | 1.32 km |
| Elevated route | 155.01 km |
| Tunnel route | 0.00 km |
| Precast span stock | 15,686 spans |
| Independent supports | 15,824 |
| Running rail | 717.22 rail-km / 43,184 t |
| Complete fastening sets | 1,255,131 |
| Protected at-grade crossing packages | 54 |
| Bridge runs / tunnel portals | 10 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 279.4 m; actual accessible paths require survey |
| Pooled depot area | 148,148 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $888,450 | $3.64m | $20.68m |
| Civil production campaign | $4.78m | $22.92m | $135.70m |

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
| low | make | 7 | 54,901 | 407,836 | 543,781 |
| base | make | 15 | 133,331 | 1,066,648 | 1,422,197 |
| high | make | 41 | 360,778 | 2,948,968 | 3,931,957 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 39 | Unestablished | 281,853 | 140.9 |
| Vehicle production / low | 30 | 60 | Unestablished | Unestablished |
| Civil field / low | 57 | 114 | 587,083 | Unestablished |
| Civil other installation / low | 352 | 704 | 3,660,603 | Unestablished |
| Civil precast / low | 56 | 112 | 543,781 | Unestablished |
| Control room and access-site coverage / base | 78 | Unestablished | 640,575 | 320.3 |
| Vehicle production / base | 85 | 170 | Unestablished | Unestablished |
| Civil field / base | 210 | 420 | 1,844,907 | Unestablished |
| Civil other installation / base | 2,383 | 4,766 | 20,964,409 | Unestablished |
| Civil precast / base | 120 | 240 | 1,422,197 | Unestablished |
| Control room and access-site coverage / high | 156 | Unestablished | 1,537,380 | 768.7 |
| Vehicle production / high | 232 | 464 | Unestablished | Unestablished |
| Civil field / high | 914 | 1,828 | 5,114,955 | Unestablished |
| Civil other installation / high | 23,034 | 46,068 | 128,988,561 | Unestablished |
| Civil precast / high | 328 | 656 | 3,931,957 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 74 | 303.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $780.08m | $2.709bn | $15.858bn |
| Installed capital / route-km | $4.35m | $15.11m | $88.44m |
| 30-year whole-life NPV | $1.631bn | $5.657bn | $31.865bn |
| Annual operating provision | $40.26m | $132.10m | $669.68m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $643.38m | $643.38m |
| Guideway | $241.10m | $241.10m |
| Stations power | $431.22m | $431.22m |
| Factory tooling | $26.56m | $26.56m |
| Construction | $1.113bn | $1.113bn |
| Land utilities depot | $174.64m | $174.64m |
| Fleet | $59.56m | $59.56m |
| Energy | $0 | $1.343bn |
| Operations | $0 | $86.65m |
| Maintenance | $0 | $773.13m |
| Renewals | $0 | $637.86m |
| Recovery | $19.87m | $40.48m |
| Reliability | $0 | $60.71m |
| Disposal | $0 | $25.06m |

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
| City project risk contingency | $541.86m | 20.0% |
| Network delivered assembled fleet | $514.10m | 19.0% |
| Design prototypes independent review | $160.15m | 5.9% |
| Shared access and transfer complexes | $117.46m | 4.3% |
| Repeat box beams | $115.43m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $780.08m | $2.709bn | $15.858bn |
| Water-evidence alternative capital | $779.59m | $2.706bn | $15.834bn |
| Alternative capital / route-km | $4.35m | $15.09m | $88.31m |
| Alternative whole-life NPV | $1.631bn | $5.654bn | $31.841bn |
| Included non-water obstruction reserve | $11,235 | $74,899 | $524,292 |

0.15 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-107.85m | $-5.237bn | -0.62 |
| 50% | 97.01m | 0.50 | $48.51m | $-83.60m | $-4.818bn | -0.48 |
| 50% | 97.01m | 1.00 | $97.01m | $-35.09m | $-3.979bn | -0.20 |
| 75% | 145.52m | 0.25 | $36.38m | $-95.72m | $-5.027bn | -0.55 |
| 75% | 145.52m | 0.50 | $72.76m | $-59.34m | $-4.398bn | -0.34 |
| 75% | 145.52m | 1.00 | $145.52m | $13.41m | $-3.140bn | 0.08 |
| 100% | 194.02m | 0.25 | $48.51m | $-83.60m | $-4.818bn | -0.48 |
| 100% | 194.02m | 0.50 | $97.01m | $-35.09m | $-3.979bn | -0.20 |
| 100% | 194.02m | 1.00 | $194.02m | $61.92m | $-2.302bn | 0.35 |

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
| low | $546.06m | $234.02m | $50.49m |
| base | $1.897bn | $812.79m | $175.35m |
| high | $11.100bn | $4.757bn | $1.026bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/karbala.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Karbala) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `0f06103972f3f6967db477b6b1727f7b7a567a3026c59319de75790b2205b4b8` |
| cost_evaluation_id | `341c7a79906503b23f4134063fd27b76c3d1bc59ee4191c2cf5fee077b85c448` |
| outline_evaluation_id | `cd318f9247757a1727732c8bd86a65fb7e2d5e1115d1d0cf2779667633955a52` |
| research_configuration_id | `12dea618cb105dc51ed5d71324f0d416a8cd2f4ffd72a663c40c79070ecce940` |
| seed_id | `8ddaa31b5ce2ca7e973fa383f7c49f765791d5552062fbd9be217de9107c4269` |
| selected_alignment_id | `8d039eeda2402356183da0a486ee5e68271cbdb42151594d850e1c23bc3947a6` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `74cc5da5d2cea3e40089f364cbb0444c45440a82a70db9ade2826f04a74c9f8e` |
| source_result_sha256 | `895cfe6ef4d7ec5124ba9c1bdb6042df6d50e80b59bd5ef1f2067b72cb115837` |

Atlas packet `c8ad2ea81d3e9a5f7fbd71283cc9089c92eaa9020b654e0284efbdea3f42a746`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
