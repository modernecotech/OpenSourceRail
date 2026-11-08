# Kirkuk — railway design and city programme

**IQ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kirkuk) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kirkuk) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kirkuk current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,780,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 173.96 km / 2 trackways |
| Lines / operational platform groups | 8 / 62 |
| Original access markers / separately costed access sites | 71 / 35 |
| Explicit interchange references | 17 |
| Fleet including reserve | 205 six-car trainsets |
| Train distance | 112,725 train-km/day; 41,144,666 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 24.23 | 10 | 200 | 35.8 | 24 + 4 | 4,181 | S terminal ↔ N terminal |
| line-2 | 23.95 | 8 | 200 | 43.3 | 28 + 5 | 4,181 | S terminal ↔ NE terminal |
| line-3 | 22.02 | 9 | 200 | 36.4 | 24 + 4 | 4,181 | SW terminal ↔ E terminal |
| line-4 | 25.24 | 7 | 200 | 32.5 | 22 + 4 | 4,181 | E terminal ↔ W terminal |
| line-5 | 58.60 | 19 | 200 | 84.5 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-6 | 4.74 | 2 | 200 | 6.9 | 6 + 1 | 4,181 | NE terminal ↔ NW terminal |
| line-7 | 8.01 | 3 | 200 | 11.9 | 9 + 2 | 4,181 | NW terminal ↔ N terminal |
| line-8 | 7.17 | 4 | 200 | 12.1 | 10 + 2 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 31.16 | False | Unestablished |
| 800.00 | 13.33 | 124.66 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 392,286 kWh mechanical | 143.18 GWh mechanical |
| Nominal auxiliary load | 661,500 kWh | 241.45 GWh |
| Auxiliary supply including scenario charging losses | 696,316 kWh | 254.16 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.36 GWh |
| Total priced grid-supply scenario | See annual budget | 439.59 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $28.31m | $72.78m | $216.29m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 24.23 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 25.24 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 58.60 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,298.5 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,893.1 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,292.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 10.02 km |
| Bridge route | 0.66 km |
| Elevated route | 163.28 km |
| Tunnel route | 0.00 km |
| Precast span stock | 16,416 spans |
| Independent supports | 16,510 |
| Running rail | 695.83 rail-km / 41,896 t |
| Complete fastening sets | 1,217,710 |
| Protected at-grade crossing packages | 25 |
| Bridge runs / tunnel portals | 11 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 773.2 m; actual accessible paths require survey |
| Pooled depot area | 143,468 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $888,450 | $3.64m | $20.33m |
| Civil production campaign | $4.97m | $23.87m | $141.22m |

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
| low | make | 7 | 57,456 | 426,816 | 569,088 |
| base | make | 16 | 139,536 | 1,116,288 | 1,488,384 |
| high | make | 42 | 377,568 | 3,086,208 | 4,114,944 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 37 | Unestablished | 267,399 | 133.7 |
| Vehicle production / low | 29 | 58 | Unestablished | Unestablished |
| Civil field / low | 60 | 120 | 613,867 | Unestablished |
| Civil other installation / low | 317 | 634 | 3,289,748 | Unestablished |
| Civil precast / low | 56 | 112 | 569,088 | Unestablished |
| Control room and access-site coverage / base | 74 | Unestablished | 607,725 | 303.9 |
| Vehicle production / base | 82 | 164 | Unestablished | Unestablished |
| Civil field / base | 220 | 440 | 1,929,152 | Unestablished |
| Civil other installation / base | 2,064 | 4,128 | 18,156,140 | Unestablished |
| Civil precast / base | 128 | 256 | 1,488,384 | Unestablished |
| Control room and access-site coverage / high | 148 | Unestablished | 1,458,540 | 729.3 |
| Vehicle production / high | 226 | 452 | Unestablished | Unestablished |
| Civil field / high | 956 | 1,912 | 5,348,693 | Unestablished |
| Civil other installation / high | 19,551 | 39,102 | 109,482,076 | Unestablished |
| Civil precast / high | 336 | 672 | 4,114,944 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 70 | 287.4 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $733.27m | $2.523bn | $14.725bn |
| Installed capital / route-km | $4.22m | $14.51m | $84.65m |
| 30-year whole-life NPV | $1.538bn | $5.325bn | $30.040bn |
| Annual operating provision | $38.03m | $125.32m | $640.51m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $604.55m | $604.55m |
| Guideway | $246.29m | $246.29m |
| Stations power | $420.34m | $420.34m |
| Factory tooling | $27.51m | $27.51m |
| Construction | $979.54m | $979.54m |
| Land utilities depot | $168.57m | $168.57m |
| Fleet | $56.64m | $56.64m |
| Energy | $0 | $1.259bn |
| Operations | $0 | $82.21m |
| Maintenance | $0 | $746.89m |
| Renewals | $0 | $611.59m |
| Recovery | $19.87m | $40.48m |
| Reliability | $0 | $58.90m |
| Disposal | $0 | $23.34m |

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
| City project risk contingency | $504.66m | 20.0% |
| Network delivered assembled fleet | $499.48m | 19.8% |
| Design prototypes independent review | $149.14m | 5.9% |
| Repeat box beams | $120.80m | 4.8% |
| Shared access and transfer complexes | $112.03m | 4.4% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $733.27m | $2.523bn | $14.725bn |
| Water-evidence alternative capital | $729.38m | $2.501bn | $14.542bn |
| Alternative capital / route-km | $4.19m | $14.38m | $83.59m |
| Alternative whole-life NPV | $1.534bn | $5.303bn | $29.852bn |
| Included non-water obstruction reserve | $42,191 | $281,270 | $1.97m |

0.56 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-103.77m | $-4.953bn | -0.64 |
| 50% | 86.23m | 0.50 | $43.12m | $-82.21m | $-4.580bn | -0.50 |
| 50% | 86.23m | 1.00 | $86.23m | $-39.09m | $-3.834bn | -0.24 |
| 75% | 129.35m | 0.25 | $32.34m | $-92.99m | $-4.766bn | -0.57 |
| 75% | 129.35m | 0.50 | $64.67m | $-60.65m | $-4.207bn | -0.37 |
| 75% | 129.35m | 1.00 | $129.35m | $4.02m | $-3.089bn | 0.02 |
| 100% | 172.46m | 0.25 | $43.12m | $-82.21m | $-4.580bn | -0.50 |
| 100% | 172.46m | 0.50 | $86.23m | $-39.09m | $-3.834bn | -0.24 |
| 100% | 172.46m | 1.00 | $172.46m | $47.14m | $-2.343bn | 0.29 |

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
| low | $513.29m | $219.98m | $47.46m |
| base | $1.766bn | $756.99m | $163.32m |
| high | $10.308bn | $4.418bn | $953.06m |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kirkuk.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Kirkuk) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `c1a9719fcb1175df3db78238334fdd55f013c60dd7a810183ac4a2f4cb39222f` |
| cost_evaluation_id | `d85c57ea97c2f1663e700a4f1847580c4a1b3394a99874d563500b8c20a7cb91` |
| outline_evaluation_id | `302a8589b7470090b622e25665d5a4f980a37a3acbd9604218e8fa04fba54f76` |
| research_configuration_id | `129cd7bb2564d236f9019b6f6f180de01f45ce855919e173809c36c3e4d77c15` |
| seed_id | `808ea72dd8b27bff362e184d1dcb4cfedcfaa7beba41d675bb938fa9a8e1480b` |
| selected_alignment_id | `cc4359af814ba46ccab01ea12973549e9df77cd12147a6477b0abb5029a49a06` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `f6f494640993aa8ff9ba0263fe4d49becaa9c5fc5db8a954fa4fa26c64b0fe04` |
| source_result_sha256 | `45586a47baef02e858b44bf1a59508506efc0e77c19344a64640a56574a39504` |

Atlas packet `591048207b84a5cedd1c3fa506fd818195bf59af59626a05895f4db1c95396ea`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
