# Hyderabad Pk — railway design and city programme

**PK · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=hyderabad-pk) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=hyderabad-pk) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Hyderabad Pk current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,900,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 215.90 km / 2 trackways |
| Lines / operational platform groups | 9 / 101 |
| Original access markers / separately costed access sites | 115 / 47 |
| Explicit interchange references | 26 |
| Fleet including reserve | 275 six-car trainsets |
| Train distance | 139,902 train-km/day; 51,064,374 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 17.85 | 11 | 200 | 32.8 | 22 + 4 | 4,181 | E terminal ↔ SW terminal |
| line-2 | 22.26 | 16 | 200 | 46.4 | 30 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-3 | 21.00 | 9 | 200 | 30.8 | 21 + 4 | 4,181 | S terminal ↔ NE terminal |
| line-4 | 27.86 | 12 | 200 | 49.5 | 32 + 5 | 4,181 | SE terminal ↔ N terminal |
| line-5 | 32.22 | 19 | 200 | 63.1 | 40 + 6 | 4,181 | W terminal ↔ E terminal |
| line-6 | 64.09 | 20 | 200 | 91.2 | 56 + 9 | 4,181 | Ring / closed circuit |
| line-7 | 4.36 | 3 | 200 | 7.3 | 7 + 2 | 4,181 | SE terminal ↔ S terminal |
| line-8 | 13.33 | 6 | 200 | 20.1 | 14 + 3 | 4,181 | NW terminal ↔ N terminal |
| line-9 | 12.93 | 5 | 200 | 17.5 | 13 + 2 | 4,181 | SE terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 50.77 | False | Unestablished |
| 800.00 | 13.33 | 203.07 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 530,997 kWh mechanical | 193.81 GWh mechanical |
| Nominal auxiliary load | 888,300 kWh | 324.23 GWh |
| Auxiliary supply including scenario charging losses | 935,053 kWh | 341.29 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.81 GWh |
| Total priced grid-supply scenario | See annual budget | 593.23 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $38.34m | $98.22m | $289.58m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
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
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 21.00 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 64.09 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 4 / 749.2 kW | 13.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 12.93 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-3 | 1 | Coast stops before receiving zone | 5,838.3 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,799.0 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 6,454.9 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 5,920.5 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 15.66 km |
| Bridge route | 13.17 km |
| Elevated route | 187.07 km |
| Tunnel route | 0.00 km |
| Precast span stock | 20,200 spans |
| Independent supports | 20,722 |
| Running rail | 863.60 rail-km / 51,997 t |
| Complete fastening sets | 1,511,292 |
| Protected at-grade crossing packages | 60 |
| Bridge runs / tunnel portals | 105 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,175.7 m; actual accessible paths require survey |
| Pooled depot area | 192,244 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.39m | $27.12m |
| Civil production campaign | $5.94m | $29.02m | $172.23m |

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
| low | make | 8 | 70,700 | 525,200 | 700,267 |
| base | make | 20 | 171,700 | 1,373,600 | 1,831,467 |
| high | make | 52 | 464,600 | 3,797,600 | 5,063,467 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 49 | Unestablished | 354,123 | 177.1 |
| Vehicle production / low | 39 | 78 | Unestablished | Unestablished |
| Civil field / low | 74 | 148 | 759,701 | Unestablished |
| Civil other installation / low | 647 | 1,294 | 6,728,029 | Unestablished |
| Civil precast / low | 64 | 128 | 700,267 | Unestablished |
| Control room and access-site coverage / base | 98 | Unestablished | 804,825 | 402.4 |
| Vehicle production / base | 110 | 220 | Unestablished | Unestablished |
| Civil field / base | 272 | 544 | 2,386,837 | Unestablished |
| Civil other installation / base | 4,377 | 8,754 | 38,514,416 | Unestablished |
| Civil precast / base | 160 | 320 | 1,831,467 | Unestablished |
| Control room and access-site coverage / high | 196 | Unestablished | 1,931,580 | 965.8 |
| Vehicle production / high | 302 | 604 | Unestablished | Unestablished |
| Civil field / high | 1,182 | 2,364 | 6,616,277 | Unestablished |
| Civil other installation / high | 42,055 | 84,110 | 235,507,348 | Unestablished |
| Civil precast / high | 416 | 832 | 5,063,467 | Unestablished |

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
| Installed capital | $1.115bn | $4.027bn | $24.258bn |
| Installed capital / route-km | $5.16m | $18.65m | $112.36m |
| 30-year whole-life NPV | $2.223bn | $7.893bn | $45.323bn |
| Annual operating provision | $51.84m | $170.95m | $869.00m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $783.37m | $783.37m |
| Guideway | $303.87m | $303.87m |
| Stations power | $722.20m | $722.20m |
| Factory tooling | $33.41m | $33.41m |
| Construction | $1.870bn | $1.870bn |
| Land utilities depot | $214.47m | $214.47m |
| Fleet | $74.32m | $74.32m |
| Energy | $0 | $1.698bn |
| Operations | $0 | $108.87m |
| Maintenance | $0 | $1.050bn |
| Renewals | $0 | $873.34m |
| Recovery | $24.83m | $50.60m |
| Reliability | $0 | $73.10m |
| Disposal | $0 | $37.24m |

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
| City project risk contingency | $805.30m | 20.0% |
| Network delivered assembled fleet | $670.03m | 16.6% |
| Bridge special foundations deck temporary | $444.76m | 11.0% |
| Design prototypes independent review | $237.94m | 5.9% |
| Shared access and transfer complexes | $153.62m | 3.8% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.115bn | $4.027bn | $24.258bn |
| Water-evidence alternative capital | $1.109bn | $3.990bn | $23.958bn |
| Alternative capital / route-km | $5.14m | $18.48m | $110.97m |
| Alternative whole-life NPV | $2.217bn | $7.857bn | $45.024bn |
| Included non-water obstruction reserve | $388,389 | $2.59m | $18.12m |

5.18 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 5 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-146.69m | $-7.474bn | -0.56 |
| 50% | 97.01m | 0.50 | $48.51m | $-122.44m | $-7.054bn | -0.47 |
| 50% | 97.01m | 1.00 | $97.01m | $-73.94m | $-6.216bn | -0.28 |
| 75% | 145.52m | 0.25 | $36.38m | $-134.57m | $-7.264bn | -0.52 |
| 75% | 145.52m | 0.50 | $72.76m | $-98.19m | $-6.635bn | -0.38 |
| 75% | 145.52m | 1.00 | $145.52m | $-25.43m | $-5.377bn | -0.10 |
| 100% | 194.02m | 0.25 | $48.51m | $-122.44m | $-7.054bn | -0.47 |
| 100% | 194.02m | 0.50 | $97.01m | $-73.94m | $-6.216bn | -0.28 |
| 100% | 194.02m | 1.00 | $194.02m | $23.07m | $-4.538bn | 0.09 |

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
| low | $780.50m | $334.50m | $72.17m |
| base | $2.819bn | $1.208bn | $260.61m |
| high | $16.980bn | $7.277bn | $1.570bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/hyderabad-pk.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Pakistan/Hyderabad-Pk) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `8072ceb62e7d2a521d00f63f7437226563f34e49a58ff63ebb199d98b36ba97e` |
| cost_evaluation_id | `44ea9ffba38a185c988d6f5ec9a6c707e6a7bd4ab4a399e4cc96d6c27bfe2e96` |
| outline_evaluation_id | `31362fd08f6f6eb42f32dcafd740d3fec13a131d512006c50952e5a7a494f634` |
| research_configuration_id | `4cd71e7882f4c0b27780f9697dcc0d52eb07ba9a183027df9e0aca2cfaefe942` |
| seed_id | `3327c4b0d14368ba67265d4184019188e4e0ff6cba34c959717208fa49e05074` |
| selected_alignment_id | `041d226364c4c264ec3159b8a7f8217bc76933665cf2c95b99293bd648c9de62` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `6a6f52d8ee0944146e37ea930272127386c53b719cbba5788dccde7ed7f2ac01` |
| source_result_sha256 | `1c55cbe8da8590e124733346df26662b4a979e27d8594c2a2ce2e32c9c5bd047` |

Atlas packet `85d96366b2479f36008da17db474b5703262b963b27e0548069902afddde283d`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
