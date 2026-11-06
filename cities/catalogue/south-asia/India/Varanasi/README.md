# Varanasi — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=varanasi) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=varanasi) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Varanasi current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,500,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 213.63 km / 2 trackways |
| Lines / operational platform groups | 6 / 67 |
| Original access markers / separately costed access sites | 75 / 41 |
| Explicit interchange references | 16 |
| Fleet including reserve | 231 six-car trainsets |
| Train distance | 138,433 train-km/day; 50,527,893 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 33.33 | 10 | 200 | 45.4 | 30 + 5 | 4,181 | S terminal ↔ NE terminal |
| line-2 | 57.10 | 19 | 200 | 80.3 | 50 + 8 | 4,181 | NW terminal ↔ SE terminal |
| line-3 | 14.14 | 6 | 200 | 23.1 | 16 + 3 | 4,181 | N terminal ↔ SW terminal |
| line-4 | 21.98 | 6 | 200 | 38.5 | 25 + 4 | 4,181 | W terminal ↔ S terminal |
| line-5 | 22.91 | 7 | 200 | 30.9 | 21 + 4 | 4,181 | NW terminal ↔ E terminal |
| line-6 | 64.17 | 19 | 200 | 90.1 | 56 + 9 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 33.68 | False | Unestablished |
| 800.00 | 13.33 | 134.71 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 515,028 kWh mechanical | 187.99 GWh mechanical |
| Nominal auxiliary load | 748,440 kWh | 273.18 GWh |
| Auxiliary supply including scenario charging losses | 787,832 kWh | 287.56 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.79 GWh |
| Total priced grid-supply scenario | See annual budget | 526.72 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $33.76m | $87.21m | $261.97m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 33.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 57.10 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 22.91 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 64.17 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 5,642.3 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 5,778.4 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,903.7 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,259.8 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 22.19 km |
| Bridge route | 42.43 km |
| Elevated route | 149.01 km |
| Tunnel route | 0.00 km |
| Precast span stock | 19,388 spans |
| Independent supports | 20,134 |
| Running rail | 854.52 rail-km / 51,451 t |
| Complete fastening sets | 1,495,414 |
| Protected at-grade crossing packages | 75 |
| Bridge runs / tunnel portals | 170 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 584.6 m; actual accessible paths require survey |
| Pooled depot area | 162,084 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $898,384 | $3.86m | $24.10m |
| Civil production campaign | $5.74m | $27.93m | $165.49m |

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
| low | make | 8 | 67,858 | 504,088 | 672,117 |
| base | make | 19 | 164,798 | 1,318,384 | 1,757,845 |
| high | make | 50 | 445,924 | 3,644,944 | 4,859,925 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 43 | Unestablished | 310,761 | 155.4 |
| Vehicle production / low | 33 | 66 | Unestablished | Unestablished |
| Civil field / low | 71 | 142 | 731,776 | Unestablished |
| Civil other installation / low | 669 | 1,338 | 6,954,732 | Unestablished |
| Civil precast / low | 64 | 128 | 672,117 | Unestablished |
| Control room and access-site coverage / base | 86 | Unestablished | 706,275 | 353.1 |
| Vehicle production / base | 93 | 186 | Unestablished | Unestablished |
| Civil field / base | 262 | 524 | 2,298,731 | Unestablished |
| Civil other installation / base | 5,593 | 11,186 | 49,216,357 | Unestablished |
| Civil precast / base | 152 | 304 | 1,757,845 | Unestablished |
| Control room and access-site coverage / high | 172 | Unestablished | 1,695,060 | 847.5 |
| Vehicle production / high | 254 | 508 | Unestablished | Unestablished |
| Civil field / high | 1,138 | 2,276 | 6,371,221 | Unestablished |
| Civil other installation / high | 61,610 | 123,220 | 345,015,114 | Unestablished |
| Civil precast / high | 400 | 800 | 4,859,925 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 82 | 336.7 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.122bn | $4.479bn | $29.721bn |
| Installed capital / route-km | $5.25m | $20.97m | $139.12m |
| 30-year whole-life NPV | $2.070bn | $7.765bn | $47.713bn |
| Annual operating provision | $45.07m | $147.78m | $748.12m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $729.94m | $729.94m |
| Guideway | $294.48m | $294.48m |
| Stations power | $424.44m | $424.44m |
| Factory tooling | $31.78m | $31.78m |
| Construction | $2.710bn | $2.710bn |
| Land utilities depot | $197.05m | $197.05m |
| Fleet | $66.74m | $66.74m |
| Energy | $0 | $1.508bn |
| Operations | $0 | $95.54m |
| Maintenance | $0 | $853.84m |
| Renewals | $0 | $689.60m |
| Recovery | $24.83m | $50.60m |
| Reliability | $0 | $72.33m |
| Disposal | $0 | $41.43m |

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
| Bridge special foundations deck temporary | $1.174bn | 26.2% |
| City project risk contingency | $895.80m | 20.0% |
| Network delivered assembled fleet | $562.83m | 12.6% |
| Design prototypes independent review | $265.03m | 5.9% |
| Repeat box beams | $142.67m | 3.2% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.122bn | $4.479bn | $29.721bn |
| Water-evidence alternative capital | $898.51m | $3.182bn | $19.185bn |
| Alternative capital / route-km | $4.21m | $14.90m | $89.80m |
| Alternative whole-life NPV | $1.846bn | $6.457bn | $36.915bn |
| Included non-water obstruction reserve | $2.91m | $19.42m | $135.94m |

38.84 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 5 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 64.67m | 0.25 | $16.17m | $-131.61m | $-7.486bn | -0.45 |
| 50% | 64.67m | 0.50 | $32.34m | $-115.44m | $-7.206bn | -0.40 |
| 50% | 64.67m | 1.00 | $64.67m | $-83.11m | $-6.647bn | -0.29 |
| 75% | 97.01m | 0.25 | $24.25m | $-123.53m | $-7.346bn | -0.43 |
| 75% | 97.01m | 0.50 | $48.51m | $-99.28m | $-6.927bn | -0.34 |
| 75% | 97.01m | 1.00 | $97.01m | $-50.77m | $-6.088bn | -0.18 |
| 100% | 129.35m | 0.25 | $32.34m | $-115.44m | $-7.206bn | -0.40 |
| 100% | 129.35m | 0.50 | $64.67m | $-83.11m | $-6.647bn | -0.29 |
| 100% | 129.35m | 1.00 | $129.35m | $-18.43m | $-5.529bn | -0.06 |

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
| low | $785.24m | $336.53m | $72.61m |
| base | $3.135bn | $1.344bn | $289.90m |
| high | $20.805bn | $8.916bn | $1.924bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/varanasi.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Varanasi) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `f2d9a737cef368da4f68542e031608a15179c93955838d2968527176e6694a9a` |
| cost_evaluation_id | `ba7c0fa61915db169db36852ea4b3f5d94c7b2636d437e15488e30b9b4761d98` |
| outline_evaluation_id | `e070e084f3fc4a5bf6e4b81d9301dcfa38fa572787a9d309d90968cc9c11e514` |
| research_configuration_id | `dbb1d7578dc3b0e6e5e20ff775f66ebd1ff33bd1d7ea042e760def7062cf6c97` |
| seed_id | `5ce239ff4408bdfe8b03f89b09a3631a254f1cc5e3980ba932972d031f086d61` |
| selected_alignment_id | `72e0fae5b81b7010acb0637aff15e14e09db31a62b43a39a097107167d95b5fe` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `aa9ef6eaa3dcc038d3067c13863dd3ddb24d47eaaa76ab0a868b5f872818d338` |
| source_result_sha256 | `82dd265885eab2b980e47746c783ac3bb834ac9d3679fe39f37e92fd4c899bbc` |

Atlas packet `dd5173cc06f42230b492675090a8353745c8e325c9644a70b796238dbe0f1842`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
