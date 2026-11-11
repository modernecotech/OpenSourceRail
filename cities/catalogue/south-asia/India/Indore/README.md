# Indore — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=indore) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=indore) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Indore current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,200,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 360.85 km / 2 trackways |
| Lines / operational platform groups | 8 / 122 |
| Original access markers / separately costed access sites | 133 / 75 |
| Explicit interchange references | 26 |
| Fleet including reserve | 388 six-car trainsets |
| Train distance | 233,829 train-km/day; 85,347,679 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 42.15 | 13 | 200 | 57.1 | 37 + 6 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 43.27 | 20 | 200 | 86.3 | 54 + 9 | 4,181 | S terminal ↔ N terminal |
| line-3 | 35.56 | 10 | 200 | 46.8 | 30 + 5 | 4,181 | NW terminal ↔ S terminal |
| line-4 | 46.48 | 21 | 200 | 71.6 | 45 + 7 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 45.72 | 13 | 200 | 61.5 | 39 + 6 | 4,181 | S terminal ↔ NE terminal |
| line-6 | 29.14 | 10 | 200 | 40.8 | 27 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-7 | 35.78 | 12 | 200 | 50.2 | 32 + 5 | 4,181 | SW terminal ↔ NE terminal |
| line-8 | 82.75 | 23 | 200 | 114.9 | 70 + 11 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 61.32 | False | Unestablished |
| 800.00 | 13.33 | 245.30 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 921,608 kWh mechanical | 336.39 GWh mechanical |
| Nominal auxiliary load | 1,262,520 kWh | 460.82 GWh |
| Auxiliary supply including scenario charging losses | 1,328,968 kWh | 485.07 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.84 GWh |
| Total priced grid-supply scenario | See annual budget | 911.02 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $58.28m | $150.83m | $454.78m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 42.15 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 35.56 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 46.48 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 45.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 29.14 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 35.78 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 82.75 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 5,883.6 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,853.4 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,505.6 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,288.0 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,246.4 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,149.1 m | 5,554.5 m |
| line-8 | 3 | Coast stops before receiving zone | 6,809.0 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 51.26 km |
| Bridge route | 9.93 km |
| Elevated route | 299.65 km |
| Tunnel route | 0.00 km |
| Precast span stock | 31,166 spans |
| Independent supports | 31,706 |
| Running rail | 1,443.39 rail-km / 86,907 t |
| Complete fastening sets | 2,525,934 |
| Protected at-grade crossing packages | 122 |
| Bridge runs / tunnel portals | 86 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,033.3 m; actual accessible paths require survey |
| Pooled depot area | 270,608 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.31m | $6.53m | $37.42m |
| Civil production campaign | $8.89m | $43.71m | $260.96m |

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
| low | make | 13 | 109,081 | 810,316 | 1,080,421 |
| base | make | 30 | 264,911 | 2,119,288 | 2,825,717 |
| high | make | 80 | 716,818 | 5,859,208 | 7,812,277 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 77 | Unestablished | 556,479 | 278.2 |
| Vehicle production / low | 55 | 110 | Unestablished | Unestablished |
| Civil field / low | 113 | 226 | 1,169,291 | Unestablished |
| Civil other installation / low | 667 | 1,334 | 6,931,618 | Unestablished |
| Civil precast / low | 104 | 208 | 1,080,421 | Unestablished |
| Control room and access-site coverage / base | 154 | Unestablished | 1,264,725 | 632.4 |
| Vehicle production / base | 156 | 312 | Unestablished | Unestablished |
| Civil field / base | 418 | 836 | 3,674,091 | Unestablished |
| Civil other installation / base | 4,802 | 9,604 | 42,256,227 | Unestablished |
| Civil precast / base | 240 | 480 | 2,825,717 | Unestablished |
| Control room and access-site coverage / high | 308 | Unestablished | 3,035,340 | 1,517.7 |
| Vehicle production / high | 426 | 852 | Unestablished | Unestablished |
| Civil field / high | 1,819 | 3,638 | 10,185,419 | Unestablished |
| Civil other installation / high | 48,722 | 97,444 | 272,839,068 | Unestablished |
| Civil precast / high | 640 | 1,280 | 7,812,277 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 150 | 615.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.525bn | $5.362bn | $32.070bn |
| Installed capital / route-km | $4.23m | $14.86m | $88.87m |
| 30-year whole-life NPV | $3.160bn | $11.001bn | $62.567bn |
| Annual operating provision | $77.73m | $254.63m | $1.286bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.242bn | $1.242bn |
| Guideway | $481.05m | $481.05m |
| Stations power | $763.14m | $763.14m |
| Factory tooling | $50.24m | $50.24m |
| Construction | $2.345bn | $2.345bn |
| Land utilities depot | $325.84m | $325.84m |
| Fleet | $113.05m | $113.05m |
| Energy | $0 | $2.608bn |
| Operations | $0 | $171.08m |
| Maintenance | $0 | $1.459bn |
| Renewals | $0 | $1.187bn |
| Recovery | $41.39m | $84.33m |
| Reliability | $0 | $122.17m |
| Disposal | $0 | $49.59m |

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
| City project risk contingency | $1.072bn | 20.0% |
| Network delivered assembled fleet | $945.36m | 17.6% |
| Bridge special foundations deck temporary | $346.90m | 6.5% |
| Design prototypes independent review | $317.02m | 5.9% |
| Shared access and transfer complexes | $229.64m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.525bn | $5.362bn | $32.070bn |
| Water-evidence alternative capital | $1.487bn | $5.140bn | $30.272bn |
| Alternative capital / route-km | $4.12m | $14.24m | $83.89m |
| Alternative whole-life NPV | $3.122bn | $10.777bn | $60.724bn |
| Included non-water obstruction reserve | $491,139 | $3.27m | $22.92m |

6.55 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 2 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-233.07m | $-10.628bn | -0.67 |
| 50% | 86.23m | 0.50 | $43.12m | $-211.51m | $-10.255bn | -0.61 |
| 50% | 86.23m | 1.00 | $86.23m | $-168.40m | $-9.510bn | -0.49 |
| 75% | 129.35m | 0.25 | $32.34m | $-222.29m | $-10.442bn | -0.64 |
| 75% | 129.35m | 0.50 | $64.67m | $-189.95m | $-9.882bn | -0.55 |
| 75% | 129.35m | 1.00 | $129.35m | $-125.28m | $-8.764bn | -0.36 |
| 100% | 172.46m | 0.25 | $43.12m | $-211.51m | $-10.255bn | -0.61 |
| 100% | 172.46m | 0.50 | $86.23m | $-168.40m | $-9.510bn | -0.49 |
| 100% | 172.46m | 1.00 | $172.46m | $-82.16m | $-8.019bn | -0.24 |

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
| low | $1.068bn | $457.60m | $98.73m |
| base | $3.753bn | $1.608bn | $347.02m |
| high | $22.449bn | $9.621bn | $2.076bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/indore.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Indore) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `224d480ba73f9efecceae7c23286e7b96cbb8d64bcea2a7422ae51b1410c9f0a` |
| cost_evaluation_id | `1819b32997a2ab1bd554684ee42a58214b18350bb9914eafbd3b13b51348a1f8` |
| outline_evaluation_id | `6f1291f98ae7e061913be9045297dff5b62324981ca75d397d4d6a6d0b5406f1` |
| research_configuration_id | `94b8284fac2fbafff6d6e536f953415e3e983f2ca54c2cb4f742af24ff511f14` |
| seed_id | `dc50ca74e67b6e3ffe3d60d056854405ccb7afce9faf02f47ed769e323e11921` |
| selected_alignment_id | `c9130468f64bbc24c078e07247c7a58730f94f33c736252770a99b65563021c3` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `517831048fa7c2a16db5dc54d9736b475b7780049487eacb67bee215d13d042b` |
| source_result_sha256 | `99d96d0b628b9ec66b0643214dcd790d44ca100aa3854337b987522b6dbe39dd` |

Atlas packet `aa2effeb608fedf4eb37434cc826db1856283cce0b341e814db4411bb3328782`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
