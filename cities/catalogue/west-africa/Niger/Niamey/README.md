# Niamey — railway design and city programme

**NE · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=niamey) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=niamey) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Niamey current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,407,635 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 186.16 km / 2 trackways |
| Lines / operational platform groups | 9 / 74 |
| Original access markers / separately costed access sites | 84 / 37 |
| Explicit interchange references | 24 |
| Fleet including reserve | 230 six-car trainsets |
| Train distance | 120,631 train-km/day; 44,030,423 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 29.38 | 14 | 200 | 56.6 | 36 + 6 | 4,181 | SE terminal ↔ N terminal |
| line-2 | 20.67 | 8 | 200 | 28.8 | 20 + 3 | 4,181 | NW terminal ↔ E terminal |
| line-3 | 16.78 | 10 | 200 | 27.5 | 19 + 3 | 4,181 | NE terminal ↔ SW terminal |
| line-4 | 22.55 | 10 | 200 | 40.6 | 27 + 5 | 4,181 | W terminal ↔ E terminal |
| line-5 | 17.29 | 7 | 200 | 30.8 | 21 + 4 | 4,181 | NW terminal ↔ S terminal |
| line-6 | 56.14 | 17 | 200 | 79.7 | 48 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 5.06 | 2 | 200 | 7.8 | 7 + 2 | 4,181 | NW terminal ↔ W terminal |
| line-8 | 10.29 | 3 | 200 | 12.0 | 9 + 2 | 4,181 | SE terminal ↔ SW terminal |
| line-9 | 8.01 | 3 | 200 | 10.1 | 8 + 2 | 4,181 | SE terminal ↔ SE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 37.20 | False | Unestablished |
| 800.00 | 13.33 | 148.79 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 434,218 kWh mechanical | 158.49 GWh mechanical |
| Nominal auxiliary load | 737,100 kWh | 269.04 GWh |
| Auxiliary supply including scenario charging losses | 775,895 kWh | 283.20 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.08 GWh |
| Total priced grid-supply scenario | See annual budget | 488.46 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $31.51m | $80.87m | $239.55m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 20.67 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 16.78 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 56.14 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 10.29 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 8.01 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 5,717.8 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,757.6 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,709.2 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,090.7 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,626.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 12.61 km |
| Bridge route | 4.16 km |
| Elevated route | 169.40 km |
| Tunnel route | 0.00 km |
| Precast span stock | 17,438 spans |
| Independent supports | 17,670 |
| Running rail | 744.64 rail-km / 44,835 t |
| Complete fastening sets | 1,303,116 |
| Protected at-grade crossing packages | 62 |
| Bridge runs / tunnel portals | 27 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 685.5 m; actual accessible paths require survey |
| Pooled depot area | 160,264 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $898,384 | $3.86m | $24.10m |
| Civil production campaign | $5.25m | $25.34m | $149.96m |

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
| low | make | 7 | 61,033 | 453,388 | 604,517 |
| base | make | 17 | 148,223 | 1,185,784 | 1,581,045 |
| high | make | 45 | 401,074 | 3,278,344 | 4,371,125 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 39 | Unestablished | 281,853 | 140.9 |
| Vehicle production / low | 33 | 66 | Unestablished | Unestablished |
| Civil field / low | 63 | 126 | 653,493 | Unestablished |
| Civil other installation / low | 414 | 828 | 4,296,877 | Unestablished |
| Civil precast / low | 56 | 112 | 604,517 | Unestablished |
| Control room and access-site coverage / base | 78 | Unestablished | 640,575 | 320.3 |
| Vehicle production / base | 92 | 184 | Unestablished | Unestablished |
| Civil field / base | 234 | 468 | 2,053,483 | Unestablished |
| Civil other installation / base | 2,765 | 5,530 | 24,324,198 | Unestablished |
| Civil precast / base | 136 | 272 | 1,581,045 | Unestablished |
| Control room and access-site coverage / high | 156 | Unestablished | 1,537,380 | 768.7 |
| Vehicle production / high | 253 | 506 | Unestablished | Unestablished |
| Civil field / high | 1,017 | 2,034 | 5,692,960 | Unestablished |
| Civil other installation / high | 26,469 | 52,938 | 148,221,095 | Unestablished |
| Civil precast / high | 360 | 720 | 4,371,125 | Unestablished |

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
| Installed capital | $852.29m | $2.996bn | $17.697bn |
| Installed capital / route-km | $4.58m | $16.09m | $95.06m |
| 30-year whole-life NPV | $1.752bn | $6.129bn | $34.782bn |
| Annual operating provision | $42.32m | $139.39m | $710.04m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $673.01m | $673.01m |
| Guideway | $262.23m | $262.23m |
| Stations power | $500.62m | $500.62m |
| Factory tooling | $29.20m | $29.20m |
| Construction | $1.263bn | $1.263bn |
| Land utilities depot | $183.20m | $183.20m |
| Fleet | $63.23m | $63.23m |
| Energy | $0 | $1.398bn |
| Operations | $0 | $86.65m |
| Maintenance | $0 | $839.90m |
| Renewals | $0 | $695.30m |
| Recovery | $21.52m | $43.85m |
| Reliability | $0 | $63.03m |
| Disposal | $0 | $27.71m |

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
| City project risk contingency | $599.13m | 20.0% |
| Network delivered assembled fleet | $560.39m | 18.7% |
| Design prototypes independent review | $177.06m | 5.9% |
| Bridge special foundations deck temporary | $130.03m | 4.3% |
| Repeat box beams | $128.32m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $852.29m | $2.996bn | $17.697bn |
| Water-evidence alternative capital | $853.80m | $3.004bn | $17.763bn |
| Alternative capital / route-km | $4.59m | $16.14m | $95.42m |
| Alternative whole-life NPV | $1.754bn | $6.138bn | $34.853bn |
| Included non-water obstruction reserve | $98,816 | $658,771 | $4.61m |

1.32 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 1 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-115.14m | $-5.710bn | -0.59 |
| 50% | 97.01m | 0.50 | $48.51m | $-90.88m | $-5.290bn | -0.47 |
| 50% | 97.01m | 1.00 | $97.01m | $-42.38m | $-4.451bn | -0.22 |
| 75% | 145.52m | 0.25 | $36.38m | $-103.01m | $-5.500bn | -0.53 |
| 75% | 145.52m | 0.50 | $72.76m | $-66.63m | $-4.871bn | -0.34 |
| 75% | 145.52m | 1.00 | $145.52m | $6.13m | $-3.613bn | 0.03 |
| 100% | 194.02m | 0.25 | $48.51m | $-90.88m | $-5.290bn | -0.47 |
| 100% | 194.02m | 0.50 | $97.01m | $-42.38m | $-4.451bn | -0.22 |
| 100% | 194.02m | 1.00 | $194.02m | $54.63m | $-2.774bn | 0.28 |

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
| low | $596.60m | $255.69m | $55.16m |
| base | $2.097bn | $898.69m | $193.89m |
| high | $12.388bn | $5.309bn | $1.145bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/niamey.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-africa/Niger/Niamey) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `51cca18a92aaf98fb1f0ee132ca806d8dd652e212132798eac7481c3b6248ec5` |
| cost_evaluation_id | `ee4eb6a2109b6e1b16b31a961f34b13408d2a228ebe6ca7d0ea49c5c6168ebff` |
| outline_evaluation_id | `b7c04104345d3b6517bab10d755789688700f88c9f5f044671c0856f1c038f60` |
| research_configuration_id | `b0a3853959eb68afc5f4d3cfcbacdb377095dd133384e9b2ff8e80b78e2374fe` |
| seed_id | `98e09ffc54f1c044e14aea2d298ecff885bf1496671215183159d57770efbb32` |
| selected_alignment_id | `c12c9172f80b5556191bb22fed8ef80ab15c4f9ca34c101cb2f7f13fc32adf87` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `a20371bfe56754d2ea1ff40957c42750566963c31155619e91f145b7cd1e76c5` |
| source_result_sha256 | `2789de6fd690477bbe085f1b04ffdff41529ed7ff301409174430b7bc8c2386f` |

Atlas packet `7f9c234b321076bda8f0abc2815a9b1f3b4b8c45ceeb551b9ec47e5f99b134fa`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
