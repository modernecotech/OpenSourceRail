# Kathmandu — railway design and city programme

**NP · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kathmandu) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kathmandu) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kathmandu current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,442,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 234.92 km / 2 trackways |
| Lines / operational platform groups | 9 / 116 |
| Original access markers / separately costed access sites | 147 / 47 |
| Explicit interchange references | 26 |
| Fleet including reserve | 297 six-car trainsets |
| Train distance | 152,227 train-km/day; 55,562,957 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 37.77 | 24 | 200 | 65.6 | 42 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-2 | 29.24 | 16 | 200 | 60.6 | 39 + 6 | 4,181 | SW terminal ↔ NE terminal |
| line-3 | 21.58 | 16 | 200 | 39.5 | 26 + 4 | 4,181 | N terminal ↔ S terminal |
| line-4 | 24.84 | 12 | 200 | 38.6 | 25 + 4 | 4,181 | N terminal ↔ SW terminal |
| line-5 | 30.91 | 15 | 200 | 58.2 | 37 + 6 | 4,181 | E terminal ↔ W terminal |
| line-6 | 55.65 | 21 | 200 | 85.5 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 6.29 | 2 | 200 | 6.3 | 6 + 1 | 4,181 | E terminal ↔ NE terminal |
| line-8 | 23.78 | 8 | 200 | 31.9 | 21 + 4 | 4,181 | SE terminal ↔ E terminal |
| line-9 | 4.86 | 2 | 200 | 7.2 | 7 + 2 | 4,181 | W terminal ↔ W terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 58.31 | False | Unestablished |
| 800.00 | 13.33 | 233.23 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 587,284 kWh mechanical | 214.36 GWh mechanical |
| Nominal auxiliary load | 963,900 kWh | 351.82 GWh |
| Auxiliary supply including scenario charging losses | 1,014,632 kWh | 370.34 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 6.10 GWh |
| Total priced grid-supply scenario | See annual budget | 644.51 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $41.48m | $106.71m | $317.78m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
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
| line-1 | 4 / 749.2 kW | 37.77 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 21.58 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 24.84 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 55.65 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 6.29 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 23.78 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,358.4 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,044.6 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 5,878.3 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,882.9 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,291.5 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,518.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 11.11 km |
| Bridge route | 14.61 km |
| Elevated route | 209.20 km |
| Tunnel route | 0.00 km |
| Precast span stock | 23,088 spans |
| Independent supports | 24,102 |
| Running rail | 953.75 rail-km / 57,426 t |
| Complete fastening sets | 1,669,071 |
| Protected at-grade crossing packages | 128 |
| Bridge runs / tunnel portals | 181 / 0 |
| Additional station track | 7,040 m |
| Access connector allowance | 2,242.6 m; actual accessible paths require survey |
| Pooled depot area | 207,324 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.05m | $4.75m | $28.96m |
| Civil production campaign | $6.74m | $32.84m | $195.76m |

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
| low | make | 9 | 80,808 | 600,288 | 800,384 |
| base | make | 22 | 196,248 | 1,569,984 | 2,093,312 |
| high | make | 60 | 531,024 | 4,340,544 | 5,787,392 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 49 | Unestablished | 354,123 | 177.1 |
| Vehicle production / low | 42 | 84 | Unestablished | Unestablished |
| Civil field / low | 84 | 168 | 872,768 | Unestablished |
| Civil other installation / low | 732 | 1,464 | 7,606,394 | Unestablished |
| Civil precast / low | 72 | 144 | 800,384 | Unestablished |
| Control room and access-site coverage / base | 98 | Unestablished | 804,825 | 402.4 |
| Vehicle production / base | 119 | 238 | Unestablished | Unestablished |
| Civil field / base | 312 | 624 | 2,741,440 | Unestablished |
| Civil other installation / base | 5,172 | 10,344 | 45,512,715 | Unestablished |
| Civil precast / base | 176 | 352 | 2,093,312 | Unestablished |
| Control room and access-site coverage / high | 196 | Unestablished | 1,931,580 | 965.8 |
| Vehicle production / high | 327 | 654 | Unestablished | Unestablished |
| Civil field / high | 1,357 | 2,714 | 7,597,824 | Unestablished |
| Civil other installation / high | 51,026 | 102,052 | 285,744,223 | Unestablished |
| Civil precast / high | 480 | 960 | 5,787,392 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 94 | 386.0 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.288bn | $4.689bn | $28.537bn |
| Installed capital / route-km | $5.48m | $19.96m | $121.48m |
| 30-year whole-life NPV | $2.501bn | $8.902bn | $51.435bn |
| Annual operating provision | $56.35m | $186.15m | $945.33m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $906.98m | $906.98m |
| Guideway | $343.65m | $343.65m |
| Stations power | $749.63m | $749.63m |
| Factory tooling | $37.59m | $37.59m |
| Construction | $2.309bn | $2.309bn |
| Land utilities depot | $231.79m | $231.79m |
| Fleet | $83.92m | $83.92m |
| Energy | $0 | $1.845bn |
| Operations | $0 | $108.87m |
| Maintenance | $0 | $1.158bn |
| Renewals | $0 | $951.12m |
| Recovery | $26.49m | $53.97m |
| Reliability | $0 | $79.54m |
| Disposal | $0 | $43.37m |

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
| City project risk contingency | $937.78m | 20.0% |
| Network delivered assembled fleet | $723.64m | 15.4% |
| Bridge special foundations deck temporary | $590.92m | 12.6% |
| Design prototypes independent review | $277.17m | 5.9% |
| Repeat box beams | $169.90m | 3.6% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.288bn | $4.689bn | $28.537bn |
| Water-evidence alternative capital | $1.262bn | $4.532bn | $27.258bn |
| Alternative capital / route-km | $5.37m | $19.29m | $116.03m |
| Alternative whole-life NPV | $2.474bn | $8.745bn | $50.136bn |
| Included non-water obstruction reserve | $736,566 | $4.91m | $34.37m |

9.82 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 4 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-161.90m | $-8.483bn | -0.53 |
| 50% | 97.01m | 0.50 | $48.51m | $-137.65m | $-8.064bn | -0.45 |
| 50% | 97.01m | 1.00 | $97.01m | $-89.14m | $-7.225bn | -0.29 |
| 75% | 145.52m | 0.25 | $36.38m | $-149.77m | $-8.273bn | -0.49 |
| 75% | 145.52m | 0.50 | $72.76m | $-113.40m | $-7.644bn | -0.37 |
| 75% | 145.52m | 1.00 | $145.52m | $-40.64m | $-6.386bn | -0.13 |
| 100% | 194.02m | 0.25 | $48.51m | $-137.65m | $-8.064bn | -0.45 |
| 100% | 194.02m | 0.50 | $97.01m | $-89.14m | $-7.225bn | -0.29 |
| 100% | 194.02m | 1.00 | $194.02m | $7.87m | $-5.547bn | 0.03 |

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
| low | $901.92m | $386.54m | $83.39m |
| base | $3.282bn | $1.407bn | $303.48m |
| high | $19.976bn | $8.561bn | $1.847bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kathmandu.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Nepal/Kathmandu) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `db1cd0ff9b1fa4ff582f1145dda892a596e8ef21d577e41ab88ba2e10031c445` |
| cost_evaluation_id | `c0e0e358ba7f993228625004c7cc7d5f435e3ae1e32bc6681a45e6683ad4369b` |
| outline_evaluation_id | `23182877791b91f48e7e2159777d69552ef9c0874a9a9fd0f15c808b350f2188` |
| research_configuration_id | `7265c30b33fb19c07938c003fb16d6849b61c46d6e122cc3fccaa40618655db7` |
| seed_id | `b9acc57985fbec27e2f41592e5ba679129c2101066865d42bf8e41bb0cb94e6c` |
| selected_alignment_id | `802a100f980f5fa4d658f6c1e7ed08761a3818bdce4c480bac89eaeef2fb8fa8` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `098b0ecaea88568d568db461520cf7ce1189484be386a491f7430a8b42bd8026` |
| source_result_sha256 | `9b2d3a0a0c04816aaaa551c4085e8dd43b0d96b345377f80c6fe32555f44858e` |

Atlas packet `73476a3fddaf7b86e8157b0fd9ba88d7330600d8e08c6bdbcd4b7e7c5921cdb7`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
