# Tunis — railway design and city programme

**TN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=tunis) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=tunis) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Tunis current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,900,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 265.41 km / 2 trackways |
| Lines / operational platform groups | 8 / 82 |
| Original access markers / separately costed access sites | 85 / 56 |
| Explicit interchange references | 20 |
| Fleet including reserve | 278 six-car trainsets |
| Train distance | 171,983 train-km/day; 62,773,925 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 40.02 | 12 | 200 | 53.8 | 35 + 6 | 4,181 | E terminal ↔ W terminal |
| line-2 | 31.89 | 12 | 200 | 46.1 | 30 + 5 | 4,181 | S terminal ↔ N terminal |
| line-3 | 47.33 | 12 | 200 | 61.6 | 39 + 6 | 4,181 | W terminal ↔ E terminal |
| line-4 | 33.29 | 12 | 200 | 47.0 | 30 + 5 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 80.82 | 23 | 200 | 112.7 | 68 + 11 | 4,181 | Ring / closed circuit |
| line-6 | 12.36 | 4 | 200 | 23.1 | 16 + 3 | 4,181 | W terminal ↔ NW terminal |
| line-7 | 13.61 | 5 | 200 | 18.8 | 14 + 3 | 4,181 | NW terminal ↔ NE terminal |
| line-8 | 6.10 | 2 | 200 | 6.1 | 6 + 1 | 4,181 | E terminal ↔ SE terminal |

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
| Mechanical traction work | 695,573 kWh mechanical | 253.88 GWh mechanical |
| Nominal auxiliary load | 899,640 kWh | 328.37 GWh |
| Auxiliary supply including scenario charging losses | 946,989 kWh | 345.65 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.81 GWh |
| Total priced grid-supply scenario | See annual budget | 666.52 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $42.54m | $110.35m | $334.43m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 40.02 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 31.89 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 47.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 33.29 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 80.82 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 4 / 749.2 kW | 13.61 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 6.10 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,437.8 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,902.9 m | 5,554.5 m |
| line-3 | 3 | Coast stops before receiving zone | 6,603.7 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,597.1 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,871.3 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,836.5 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,100.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 24.72 km |
| Bridge route | 3.15 km |
| Elevated route | 237.53 km |
| Tunnel route | 0.00 km |
| Precast span stock | 24,146 spans |
| Independent supports | 24,340 |
| Running rail | 1,061.63 rail-km / 63,920 t |
| Complete fastening sets | 1,857,845 |
| Protected at-grade crossing packages | 74 |
| Bridge runs / tunnel portals | 16 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 198.7 m; actual accessible paths require survey |
| Pooled depot area | 193,960 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.05m | $4.44m | $27.77m |
| Civil production campaign | $7.01m | $34.22m | $204.09m |

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
| low | make | 10 | 84,511 | 627,796 | 837,061 |
| base | make | 23 | 205,241 | 1,641,928 | 2,189,237 |
| high | make | 62 | 555,358 | 4,539,448 | 6,052,597 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 58 | Unestablished | 419,166 | 209.6 |
| Vehicle production / low | 40 | 80 | Unestablished | Unestablished |
| Civil field / low | 87 | 174 | 903,520 | Unestablished |
| Civil other installation / low | 409 | 818 | 4,244,674 | Unestablished |
| Civil precast / low | 80 | 160 | 837,061 | Unestablished |
| Control room and access-site coverage / base | 116 | Unestablished | 952,650 | 476.3 |
| Vehicle production / base | 112 | 224 | Unestablished | Unestablished |
| Civil field / base | 323 | 646 | 2,839,339 | Unestablished |
| Civil other installation / base | 2,953 | 5,906 | 25,978,384 | Unestablished |
| Civil precast / base | 184 | 368 | 2,189,237 | Unestablished |
| Control room and access-site coverage / high | 232 | Unestablished | 2,286,360 | 1,143.2 |
| Vehicle production / high | 306 | 612 | Unestablished | Unestablished |
| Civil field / high | 1,406 | 2,812 | 7,872,053 | Unestablished |
| Civil other installation / high | 30,128 | 60,256 | 168,711,570 | Unestablished |
| Civil precast / high | 496 | 992 | 6,052,597 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 112 | 459.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.074bn | $3.708bn | $21.983bn |
| Installed capital / route-km | $4.05m | $13.97m | $82.83m |
| 30-year whole-life NPV | $2.261bn | $7.798bn | $44.181bn |
| Annual operating provision | $56.66m | $185.62m | $940.48m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $913.08m | $913.08m |
| Guideway | $366.46m | $366.46m |
| Stations power | $508.43m | $508.43m |
| Factory tooling | $38.66m | $38.66m |
| Construction | $1.529bn | $1.529bn |
| Land utilities depot | $239.85m | $239.85m |
| Fleet | $82.40m | $82.40m |
| Energy | $0 | $1.908bn |
| Operations | $0 | $128.87m |
| Maintenance | $0 | $1.052bn |
| Renewals | $0 | $845.89m |
| Recovery | $29.80m | $60.72m |
| Reliability | $0 | $89.86m |
| Disposal | $0 | $34.29m |

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
| City project risk contingency | $741.52m | 20.0% |
| Network delivered assembled fleet | $677.34m | 18.3% |
| Design prototypes independent review | $219.24m | 5.9% |
| Repeat box beams | $177.68m | 4.8% |
| Shared access and transfer complexes | $172.05m | 4.6% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.074bn | $3.708bn | $21.983bn |
| Water-evidence alternative capital | $1.071bn | $3.690bn | $21.843bn |
| Alternative capital / route-km | $4.04m | $13.90m | $82.30m |
| Alternative whole-life NPV | $2.258bn | $7.780bn | $44.039bn |
| Included non-water obstruction reserve | $82,930 | $552,865 | $3.87m |

1.11 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-164.06m | $-7.425bn | -0.68 |
| 50% | 86.23m | 0.50 | $43.12m | $-142.51m | $-7.052bn | -0.59 |
| 50% | 86.23m | 1.00 | $86.23m | $-99.39m | $-6.306bn | -0.41 |
| 75% | 129.35m | 0.25 | $32.34m | $-153.28m | $-7.238bn | -0.64 |
| 75% | 129.35m | 0.50 | $64.67m | $-120.95m | $-6.679bn | -0.50 |
| 75% | 129.35m | 1.00 | $129.35m | $-56.27m | $-5.561bn | -0.23 |
| 100% | 172.46m | 0.25 | $43.12m | $-142.51m | $-7.052bn | -0.59 |
| 100% | 172.46m | 0.50 | $86.23m | $-99.39m | $-6.306bn | -0.41 |
| 100% | 172.46m | 1.00 | $172.46m | $-13.16m | $-4.815bn | -0.05 |

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
| low | $751.92m | $322.25m | $69.52m |
| base | $2.595bn | $1.112bn | $239.97m |
| high | $15.388bn | $6.595bn | $1.423bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/tunis.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/north-africa/Tunisia/Tunis) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `4065db4d9a651dd034bd8146144dff4fd11f568c3972a53c0fe659979542d278` |
| cost_evaluation_id | `c359ff9a3dbfbe4f3ccd3a43b9b961d11b4c58284e8aed2e2f0b6a1b76376ac4` |
| outline_evaluation_id | `b252718ac08b656ff3c81757413a4e8a2626d06513d20b24f2c2cd4a3dc08000` |
| research_configuration_id | `3760920605dd4c40837c706ebb5ba623042e2f037afa4477794ccb8561316457` |
| seed_id | `247fe34664e196fd33838ea8feb6ada87abd293cdb5d29509afbe0e0c3422ffa` |
| selected_alignment_id | `6e2aeab6275194ff9ee07a10a3059fbbc419b0e38d43b6d3ac97cddfe18a2223` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `2575c99c1961fabd38c7343d7915f6e00f187901efa072f4c06d6159e8a07e48` |
| source_result_sha256 | `2139897c17e3404db8757e38443f1535ba97c5d7a48b5953d38966540cbc1a00` |

Atlas packet `632a355fd0191b40a0e19b582e580202ef8dc64f28c8317417b0c885292b44fd`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
