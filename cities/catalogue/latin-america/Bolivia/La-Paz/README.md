# La Paz — railway design and city programme

**BO · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=la-paz) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=la-paz) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![La Paz current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,815,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 227.43 km / 2 trackways |
| Lines / operational platform groups | 9 / 70 |
| Original access markers / separately costed access sites | 72 / 48 |
| Explicit interchange references | 22 |
| Fleet including reserve | 253 six-car trainsets |
| Train distance | 147,373 train-km/day; 53,791,091 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 28.67 | 10 | 200 | 40.2 | 26 + 4 | 4,181 | NE terminal ↔ SW terminal |
| line-2 | 37.14 | 12 | 200 | 64.5 | 41 + 7 | 4,181 | W terminal ↔ E terminal |
| line-3 | 30.77 | 9 | 200 | 41.5 | 27 + 5 | 4,181 | E terminal ↔ SW terminal |
| line-4 | 27.85 | 10 | 200 | 39.4 | 26 + 4 | 4,181 | SE terminal ↔ NW terminal |
| line-5 | 30.00 | 9 | 200 | 40.7 | 27 + 5 | 4,181 | S terminal ↔ N terminal |
| line-6 | 50.45 | 12 | 200 | 67.2 | 42 + 7 | 4,181 | Ring / closed circuit |
| line-7 | 5.04 | 2 | 200 | 7.8 | 7 + 2 | 4,181 | S terminal ↔ S terminal |
| line-8 | 5.25 | 2 | 200 | 8.5 | 7 + 2 | 4,181 | W terminal ↔ NW terminal |
| line-9 | 12.26 | 4 | 200 | 15.4 | 12 + 2 | 4,181 | N terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 35.19 | False | Unestablished |
| 800.00 | 13.33 | 140.74 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 555,035 kWh mechanical | 202.59 GWh mechanical |
| Nominal auxiliary load | 812,700 kWh | 296.64 GWh |
| Auxiliary supply including scenario charging losses | 855,474 kWh | 312.25 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.52 GWh |
| Total priced grid-supply scenario | See annual budget | 571.49 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $36.62m | $94.62m | $284.20m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 28.67 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 30.77 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 27.85 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 30.00 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 50.45 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 12.26 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,886.3 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 6,164.8 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,121.9 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,305.7 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,049.2 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,963.6 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 18.82 km |
| Bridge route | 14.13 km |
| Elevated route | 194.47 km |
| Tunnel route | 0.00 km |
| Precast span stock | 21,304 spans |
| Independent supports | 21,770 |
| Running rail | 920.27 rail-km / 55,409 t |
| Complete fastening sets | 1,610,471 |
| Protected at-grade crossing packages | 36 |
| Bridge runs / tunnel portals | 95 / 0 |
| Additional station track | 5,280 m |
| Access connector allowance | 185.2 m; actual accessible paths require survey |
| Pooled depot area | 177,164 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $25.93m |
| Civil production campaign | $6.26m | $30.51m | $181.03m |

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
| low | make | 9 | 74,564 | 553,904 | 738,539 |
| base | make | 21 | 181,084 | 1,448,672 | 1,931,563 |
| high | make | 55 | 489,992 | 4,005,152 | 5,340,203 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 50 | Unestablished | 361,350 | 180.7 |
| Vehicle production / low | 36 | 72 | Unestablished | Unestablished |
| Civil field / low | 77 | 154 | 800,320 | Unestablished |
| Civil other installation / low | 570 | 1,140 | 5,927,237 | Unestablished |
| Civil precast / low | 72 | 144 | 738,539 | Unestablished |
| Control room and access-site coverage / base | 100 | Unestablished | 821,250 | 410.6 |
| Vehicle production / base | 102 | 204 | Unestablished | Unestablished |
| Civil field / base | 286 | 572 | 2,514,581 | Unestablished |
| Civil other installation / base | 4,218 | 8,436 | 37,117,230 | Unestablished |
| Civil precast / base | 168 | 336 | 1,931,563 | Unestablished |
| Control room and access-site coverage / high | 200 | Unestablished | 1,971,000 | 985.5 |
| Vehicle production / high | 278 | 556 | Unestablished | Unestablished |
| Civil field / high | 1,245 | 2,490 | 6,970,667 | Unestablished |
| Civil other installation / high | 43,145 | 86,290 | 241,611,935 | Unestablished |
| Civil precast / high | 440 | 880 | 5,340,203 | Unestablished |

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
| Installed capital | $1.091bn | $3.999bn | $24.723bn |
| Installed capital / route-km | $4.80m | $17.58m | $108.71m |
| 30-year whole-life NPV | $2.140bn | $7.654bn | $44.820bn |
| Annual operating provision | $49.50m | $163.51m | $836.63m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $787.47m | $787.47m |
| Guideway | $321.52m | $321.52m |
| Stations power | $558.28m | $558.28m |
| Factory tooling | $34.73m | $34.73m |
| Construction | $1.984bn | $1.984bn |
| Land utilities depot | $213.47m | $213.47m |
| Fleet | $72.38m | $72.38m |
| Energy | $0 | $1.636bn |
| Operations | $0 | $111.09m |
| Maintenance | $0 | $975.65m |
| Renewals | $0 | $791.01m |
| Recovery | $26.49m | $53.97m |
| Reliability | $0 | $77.00m |
| Disposal | $0 | $36.99m |

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
| City project risk contingency | $799.73m | 20.0% |
| Network delivered assembled fleet | $616.43m | 15.4% |
| Bridge special foundations deck temporary | $453.00m | 11.3% |
| Design prototypes independent review | $236.44m | 5.9% |
| Repeat box beams | $156.77m | 3.9% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.091bn | $3.999bn | $24.723bn |
| Water-evidence alternative capital | $1.030bn | $3.640bn | $21.805bn |
| Alternative capital / route-km | $4.53m | $16.00m | $95.88m |
| Alternative whole-life NPV | $2.078bn | $7.292bn | $41.833bn |
| Included non-water obstruction reserve | $928,111 | $6.19m | $43.31m |

12.37 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 1 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-139.25m | $-7.235bn | -0.54 |
| 50% | 97.01m | 0.50 | $48.51m | $-115.00m | $-6.815bn | -0.44 |
| 50% | 97.01m | 1.00 | $97.01m | $-66.50m | $-5.976bn | -0.26 |
| 75% | 145.52m | 0.25 | $36.38m | $-127.13m | $-7.025bn | -0.49 |
| 75% | 145.52m | 0.50 | $72.76m | $-90.75m | $-6.396bn | -0.35 |
| 75% | 145.52m | 1.00 | $145.52m | $-17.99m | $-5.138bn | -0.07 |
| 100% | 194.02m | 0.25 | $48.51m | $-115.00m | $-6.815bn | -0.44 |
| 100% | 194.02m | 0.50 | $97.01m | $-66.50m | $-5.976bn | -0.26 |
| 100% | 194.02m | 1.00 | $194.02m | $30.51m | $-4.299bn | 0.12 |

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
| low | $763.98m | $327.42m | $70.64m |
| base | $2.799bn | $1.200bn | $258.81m |
| high | $17.306bn | $7.417bn | $1.600bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/la-paz.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/latin-america/Bolivia/La-Paz) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `7ad64e601b909b5d949c7446de52fd9e87dc95cb9854a7ba80c94b27cf41bf50` |
| cost_evaluation_id | `fd50618d507e05d300822cce2ab49ee976e19831f6579c5dca55a1c64abcdbd7` |
| outline_evaluation_id | `a2a623d5467ea4a76a22b55483c71a2db5c532bfbd5209c74ce1dad3f0d66357` |
| research_configuration_id | `0b721829a81da8969185c0b17e54e75e1fa49b796c323b478a561c241a723b8f` |
| seed_id | `66148d7250d9f81cd273a589f36bdf49df1a7680ac945765dd87cb8dd007aa4f` |
| selected_alignment_id | `eee157819ddc39de9c0c9024c1cdf8aa75ec10ac43b1fcde19ce5941fdfb2214` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `ced1a89f061df6df80dc0e9fb5a6a2a33e0e8f21436dfe65fab9255266b19d46` |
| source_result_sha256 | `6ebec0d9bfa0da29be4972ee8facf46745dd7498f6bd535316f0031d19d76b86` |

Atlas packet `621b0ca2e15114a691a1c84d599c09c8d702cbb56f5651bba744a431f6854ab2`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
