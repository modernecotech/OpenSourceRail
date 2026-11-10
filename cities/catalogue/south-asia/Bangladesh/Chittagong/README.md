# Chittagong — railway design and city programme

**BD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=chittagong) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=chittagong) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Chittagong current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 5,200,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 380.50 km / 2 trackways |
| Lines / operational platform groups | 12 / 169 |
| Original access markers / separately costed access sites | 191 / 86 |
| Explicit interchange references | 42 |
| Fleet including reserve | 441 six-car trainsets |
| Train distance | 246,564 train-km/day; 89,995,811 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 47.13 | 13 | 200 | 62.1 | 40 + 6 | 4,181 | S terminal ↔ NW terminal |
| line-2 | 31.87 | 28 | 200 | 72.6 | 46 + 7 | 4,181 | S terminal ↔ N terminal |
| line-3 | 61.23 | 33 | 200 | 101.6 | 63 + 10 | 4,181 | NW terminal ↔ S terminal |
| line-4 | 34.07 | 14 | 200 | 50.7 | 33 + 5 | 4,181 | NE terminal ↔ SW terminal |
| line-5 | 36.54 | 13 | 200 | 51.9 | 33 + 5 | 4,181 | SW terminal ↔ NE terminal |
| line-6 | 26.46 | 9 | 200 | 36.4 | 24 + 4 | 4,181 | W terminal ↔ SE terminal |
| line-7 | 34.40 | 13 | 200 | 49.5 | 32 + 5 | 4,181 | SW terminal ↔ SE terminal |
| line-8 | 72.75 | 31 | 200 | 112.8 | 68 + 11 | 4,181 | Ring / closed circuit |
| line-9 | 13.51 | 7 | 200 | 23.3 | 16 + 3 | 4,181 | E terminal ↔ SW terminal |
| line-10 | 6.41 | 2 | 200 | 6.4 | 6 + 1 | 4,181 | NE terminal ↔ NE terminal |
| line-11 | 7.76 | 3 | 200 | 11.9 | 9 + 2 | 4,181 | NW terminal ↔ N terminal |
| line-12 | 8.36 | 3 | 200 | 12.8 | 10 + 2 | 4,181 | N terminal ↔ E terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 84.95 | False | Unestablished |
| 800.00 | 13.33 | 339.79 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,056,040 kWh mechanical | 385.45 GWh mechanical |
| Nominal auxiliary load | 1,436,400 kWh | 524.29 GWh |
| Auxiliary supply including scenario charging losses | 1,512,000 kWh | 551.88 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 8.86 GWh |
| Total priced grid-supply scenario | See annual budget | 1,040.94 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $66.70m | $172.34m | $517.97m |

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
| line-9 | Station launch reference | 0 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Station launch reference | 0 kg | 250 kg |
| line-12 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 47.13 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 61.23 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 34.07 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 36.54 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 26.46 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 34.40 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 72.75 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-10 | 4 / 749.2 kW | 6.41 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-12 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,008.3 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,824.2 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,616.0 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,689.0 m | 5,554.5 m |
| line-6 | 2 | Coast stops before receiving zone | 6,560.6 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,627.3 m | 5,554.5 m |
| line-8 | 2 | Coast stops before receiving zone | 6,560.7 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 6,414.7 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 50.87 km |
| Bridge route | 46.82 km |
| Elevated route | 282.81 km |
| Tunnel route | 0.00 km |
| Precast span stock | 34,258 spans |
| Independent supports | 35,960 |
| Running rail | 1,546.64 rail-km / 93,123 t |
| Complete fastening sets | 2,706,619 |
| Protected at-grade crossing packages | 175 |
| Bridge runs / tunnel portals | 344 / 0 |
| Additional station track | 12,320 m |
| Access connector allowance | 1,937.5 m; actual accessible paths require survey |
| Pooled depot area | 308,412 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.40m | $7.11m | $41.45m |
| Civil production campaign | $9.70m | $47.80m | $286.05m |

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
| low | make | 14 | 119,903 | 890,708 | 1,187,611 |
| base | make | 33 | 291,193 | 2,329,544 | 3,106,059 |
| high | make | 88 | 787,934 | 6,440,504 | 8,587,339 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 88 | Unestablished | 635,976 | 318.0 |
| Vehicle production / low | 62 | 124 | Unestablished | Unestablished |
| Civil field / low | 125 | 250 | 1,297,120 | Unestablished |
| Civil other installation / low | 1,298 | 2,596 | 13,497,558 | Unestablished |
| Civil precast / low | 112 | 224 | 1,187,611 | Unestablished |
| Control room and access-site coverage / base | 176 | Unestablished | 1,445,400 | 722.7 |
| Vehicle production / base | 177 | 354 | Unestablished | Unestablished |
| Civil field / base | 463 | 926 | 4,074,069 | Unestablished |
| Civil other installation / base | 9,724 | 19,448 | 85,570,805 | Unestablished |
| Civil precast / base | 264 | 528 | 3,106,059 | Unestablished |
| Control room and access-site coverage / high | 352 | Unestablished | 3,468,960 | 1,734.5 |
| Vehicle production / high | 485 | 970 | Unestablished | Unestablished |
| Civil field / high | 2,017 | 4,034 | 11,290,507 | Unestablished |
| Civil other installation / high | 100,028 | 200,056 | 560,151,219 | Unestablished |
| Civil precast / high | 704 | 1,408 | 8,587,339 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 172 | 706.3 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.123bn | $8.003bn | $50.389bn |
| Installed capital / route-km | $5.58m | $21.03m | $132.43m |
| 30-year whole-life NPV | $4.049bn | $14.689bn | $86.953bn |
| Annual operating provision | $90.24m | $297.45m | $1.509bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.391bn | $1.391bn |
| Guideway | $524.38m | $524.38m |
| Stations power | $1.186bn | $1.186bn |
| Factory tooling | $54.92m | $54.92m |
| Construction | $4.319bn | $4.319bn |
| Land utilities depot | $358.16m | $358.16m |
| Fleet | $127.24m | $127.24m |
| Energy | $0 | $2.980bn |
| Operations | $0 | $195.52m |
| Maintenance | $0 | $1.794bn |
| Renewals | $0 | $1.469bn |
| Recovery | $43.05m | $87.71m |
| Reliability | $0 | $128.83m |
| Disposal | $0 | $74.02m |

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
| City project risk contingency | $1.601bn | 20.0% |
| Bridge special foundations deck temporary | $1.544bn | 19.3% |
| Network delivered assembled fleet | $1.074bn | 13.4% |
| Design prototypes independent review | $473.14m | 5.9% |
| Shared access and transfer complexes | $275.51m | 3.4% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.123bn | $8.003bn | $50.389bn |
| Water-evidence alternative capital | $2.006bn | $7.317bn | $44.806bn |
| Alternative capital / route-km | $5.27m | $19.23m | $117.76m |
| Alternative whole-life NPV | $3.932bn | $13.999bn | $81.249bn |
| Included non-water obstruction reserve | $2.26m | $15.07m | $105.51m |

30.15 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 30 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 129.35m | 0.25 | $32.34m | $-265.11m | $-14.130bn | -0.51 |
| 50% | 129.35m | 0.50 | $64.67m | $-232.77m | $-13.571bn | -0.45 |
| 50% | 129.35m | 1.00 | $129.35m | $-168.10m | $-12.453bn | -0.32 |
| 75% | 194.02m | 0.25 | $48.51m | $-248.94m | $-13.851bn | -0.48 |
| 75% | 194.02m | 0.50 | $97.01m | $-200.44m | $-13.012bn | -0.39 |
| 75% | 194.02m | 1.00 | $194.02m | $-103.43m | $-11.334bn | -0.20 |
| 100% | 258.70m | 0.25 | $64.67m | $-232.77m | $-13.571bn | -0.45 |
| 100% | 258.70m | 0.50 | $129.35m | $-168.10m | $-12.453bn | -0.32 |
| 100% | 258.70m | 1.00 | $258.70m | $-38.75m | $-10.216bn | -0.07 |

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
| low | $1.486bn | $636.98m | $137.42m |
| base | $5.602bn | $2.401bn | $517.97m |
| high | $35.272bn | $15.117bn | $3.261bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/chittagong.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Bangladesh/Chittagong) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `a23c1011dd43977994b21a7557c22d79bbb5c9dbff49016c6c781f2c204d49a6` |
| cost_evaluation_id | `f85630e4204634890c677b44abfe7fc706488a995d36e4335291a01403470222` |
| outline_evaluation_id | `731eadd7ff8e2e4274336421559927428a41a53ccee7e1ad8634790ca81a8a77` |
| research_configuration_id | `f327945f79b71ba09509a82da8e1831a92c1b2ff0f1d3c1726615d75a8b95757` |
| seed_id | `4a7b5dde8d08fd75a8d9ab80f49a32ebb6b4f5e9ec5ff5a8dcc55654a19ac0db` |
| selected_alignment_id | `c7d9c6aa552db9314eb8074516f7fd924e48ee99fa33f3568b69e79baac07095` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `f56a44a1c8848e791de1964806725a894131c488307c767ccf97a33f451a1924` |
| source_result_sha256 | `a6d00f933461e0089d80737ee2e0f82eccef814d977a4a109d6a920a0b03e3b6` |

Atlas packet `31d34d3efbd19f70f0426ad662f1699876144cd086c351d319220c37eaaac258`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
