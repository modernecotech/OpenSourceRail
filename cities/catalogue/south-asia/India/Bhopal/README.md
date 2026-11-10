# Bhopal — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=bhopal) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=bhopal) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Bhopal current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,400,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 193.24 km / 2 trackways |
| Lines / operational platform groups | 6 / 75 |
| Original access markers / separately costed access sites | 84 / 38 |
| Explicit interchange references | 21 |
| Fleet including reserve | 230 six-car trainsets |
| Train distance | 125,221 train-km/day; 45,705,823 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 27.69 | 12 | 200 | 41.5 | 27 + 5 | 4,181 | E terminal ↔ W terminal |
| line-2 | 27.68 | 15 | 200 | 51.4 | 33 + 5 | 4,181 | S terminal ↔ N terminal |
| line-3 | 23.53 | 7 | 200 | 43.3 | 28 + 5 | 4,181 | SE terminal ↔ N terminal |
| line-4 | 36.52 | 14 | 200 | 52.7 | 34 + 6 | 4,181 | SW terminal ↔ NE terminal |
| line-5 | 20.71 | 9 | 200 | 37.4 | 25 + 4 | 4,181 | NW terminal ↔ SE terminal |
| line-6 | 57.12 | 18 | 200 | 81.8 | 50 + 8 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 37.70 | False | Unestablished |
| 800.00 | 13.33 | 150.80 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 459,046 kWh mechanical | 167.55 GWh mechanical |
| Nominal auxiliary load | 744,660 kWh | 271.80 GWh |
| Auxiliary supply including scenario charging losses | 783,853 kWh | 286.11 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.79 GWh |
| Total priced grid-supply scenario | See annual budget | 501.90 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $32.34m | $83.10m | $246.69m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 27.69 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 36.52 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 57.12 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,037.7 m | 5,554.5 m |
| line-4 | 3 | Coast stops before receiving zone | 6,751.2 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,092.4 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 10.68 km |
| Bridge route | 3.34 km |
| Elevated route | 179.23 km |
| Tunnel route | 0.00 km |
| Precast span stock | 18,516 spans |
| Independent supports | 18,792 |
| Running rail | 779.13 rail-km / 46,912 t |
| Complete fastening sets | 1,363,481 |
| Protected at-grade crossing packages | 51 |
| Bridge runs / tunnel portals | 41 / 0 |
| Additional station track | 3,080 m |
| Access connector allowance | 698.5 m; actual accessible paths require survey |
| Pooled depot area | 160,264 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $898,384 | $3.86m | $24.10m |
| Civil production campaign | $5.52m | $26.72m | $158.72m |

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
| low | make | 8 | 64,806 | 481,416 | 641,888 |
| base | make | 18 | 157,386 | 1,259,088 | 1,678,784 |
| high | make | 48 | 425,868 | 3,481,008 | 4,641,344 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 40 | Unestablished | 289,080 | 144.5 |
| Vehicle production / low | 33 | 66 | Unestablished | Unestablished |
| Civil field / low | 67 | 134 | 694,208 | Unestablished |
| Civil other installation / low | 449 | 898 | 4,665,534 | Unestablished |
| Civil precast / low | 64 | 128 | 641,888 | Unestablished |
| Control room and access-site coverage / base | 80 | Unestablished | 657,000 | 328.5 |
| Vehicle production / base | 92 | 184 | Unestablished | Unestablished |
| Civil field / base | 248 | 496 | 2,181,376 | Unestablished |
| Civil other installation / base | 2,960 | 5,920 | 26,044,034 | Unestablished |
| Civil precast / base | 144 | 288 | 1,678,784 | Unestablished |
| Control room and access-site coverage / high | 160 | Unestablished | 1,576,800 | 788.4 |
| Vehicle production / high | 253 | 506 | Unestablished | Unestablished |
| Civil field / high | 1,080 | 2,160 | 6,047,424 | Unestablished |
| Civil other installation / high | 27,894 | 55,788 | 156,205,342 | Unestablished |
| Civil precast / high | 384 | 768 | 4,641,344 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 76 | 312.1 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $898.09m | $3.137bn | $18.468bn |
| Installed capital / route-km | $4.65m | $16.23m | $95.57m |
| 30-year whole-life NPV | $1.827bn | $6.367bn | $35.993bn |
| Annual operating provision | $43.64m | $143.81m | $730.82m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $680.15m | $680.15m |
| Guideway | $277.17m | $277.17m |
| Stations power | $541.11m | $541.11m |
| Factory tooling | $30.58m | $30.58m |
| Construction | $1.338bn | $1.338bn |
| Land utilities depot | $184.79m | $184.79m |
| Fleet | $63.66m | $63.66m |
| Energy | $0 | $1.437bn |
| Operations | $0 | $88.87m |
| Maintenance | $0 | $873.19m |
| Renewals | $0 | $713.77m |
| Recovery | $21.52m | $43.85m |
| Reliability | $0 | $65.43m |
| Disposal | $0 | $29.02m |

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
| City project risk contingency | $627.43m | 20.0% |
| Network delivered assembled fleet | $560.39m | 17.9% |
| Design prototypes independent review | $185.40m | 5.9% |
| Repeat box beams | $136.25m | 4.3% |
| Bridge special foundations deck temporary | $134.81m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $898.09m | $3.137bn | $18.468bn |
| Water-evidence alternative capital | $895.32m | $3.121bn | $18.332bn |
| Alternative capital / route-km | $4.63m | $16.15m | $94.87m |
| Alternative whole-life NPV | $1.824bn | $6.350bn | $35.856bn |
| Included non-water obstruction reserve | $91,578 | $610,517 | $4.27m |

1.22 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 64.67m | 0.25 | $16.17m | $-127.64m | $-6.087bn | -0.63 |
| 50% | 64.67m | 0.50 | $32.34m | $-111.47m | $-5.807bn | -0.55 |
| 50% | 64.67m | 1.00 | $64.67m | $-79.13m | $-5.248bn | -0.39 |
| 75% | 97.01m | 0.25 | $24.25m | $-119.55m | $-5.947bn | -0.59 |
| 75% | 97.01m | 0.50 | $48.51m | $-95.30m | $-5.528bn | -0.47 |
| 75% | 97.01m | 1.00 | $97.01m | $-46.80m | $-4.689bn | -0.23 |
| 100% | 129.35m | 0.25 | $32.34m | $-111.47m | $-5.807bn | -0.55 |
| 100% | 129.35m | 0.50 | $64.67m | $-79.13m | $-5.248bn | -0.39 |
| 100% | 129.35m | 1.00 | $129.35m | $-14.46m | $-4.130bn | -0.07 |

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
| low | $628.66m | $269.43m | $58.13m |
| base | $2.196bn | $941.14m | $203.05m |
| high | $12.927bn | $5.540bn | $1.195bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/bhopal.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Bhopal) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `ccc6db55c968a973ac30865abf947fe91326d20e01a3b8604fdbc2430c3400b7` |
| cost_evaluation_id | `d54fa7fd0a3b57e1151e0ab71a10fcbc778092d9df770bdeeec281a1f3628eb9` |
| outline_evaluation_id | `f0c45d16b9413f9ece256ca8ee36628761b5cdc19a98654173f89ceda456031b` |
| research_configuration_id | `9c08e06098a879f6338502a3b7d5c5a020763af442ded109e6c0c336d169aea8` |
| seed_id | `bc75bde98ac0429762bbe265cd19ae101ebafa700f02965b309cc0a81149c2f9` |
| selected_alignment_id | `6ac358f94428779557c6ed65dadffe7bb9906002b010bf1a760b7b569fdb1179` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `7a5632f2e14e56bf5161ee74b26141ae9a1fcd0e07e2cc9863de16c4ff60c277` |
| source_result_sha256 | `4c71e1dd27ad9d7dee83ad8c15a6ea9d515783ec18a24ddfc50ab90779930bea` |

Atlas packet `fe44b7f468d3b666343785f654f26b9a5077215f8e2807e513f311d60849722d`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
