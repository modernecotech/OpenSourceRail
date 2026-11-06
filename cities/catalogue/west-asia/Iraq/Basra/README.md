# Basra — railway design and city programme

**IQ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=basra) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=basra) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Basra current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,955,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 341.45 km / 2 trackways |
| Lines / operational platform groups | 11 / 120 |
| Original access markers / separately costed access sites | 137 / 71 |
| Explicit interchange references | 26 |
| Fleet including reserve | 369 six-car trainsets |
| Train distance | 221,258 train-km/day; 80,759,300 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 47.50 | 14 | 200 | 65.3 | 41 + 7 | 4,181 | S terminal ↔ N terminal |
| line-2 | 21.70 | 13 | 200 | 36.9 | 24 + 4 | 4,181 | SE terminal ↔ N terminal |
| line-3 | 39.34 | 11 | 200 | 51.8 | 33 + 5 | 4,181 | E terminal ↔ W terminal |
| line-4 | 34.05 | 12 | 200 | 47.3 | 31 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-5 | 40.79 | 15 | 200 | 58.4 | 37 + 6 | 4,181 | SW terminal ↔ E terminal |
| line-6 | 25.00 | 9 | 200 | 40.1 | 26 + 4 | 4,181 | N terminal ↔ SW terminal |
| line-7 | 94.55 | 31 | 200 | 137.3 | 84 + 13 | 4,181 | Ring / closed circuit |
| line-8 | 10.67 | 4 | 200 | 14.3 | 11 + 2 | 4,181 | SW terminal ↔ W terminal |
| line-9 | 11.33 | 6 | 200 | 17.9 | 13 + 2 | 4,181 | E terminal ↔ E terminal |
| line-10 | 9.94 | 3 | 200 | 16.8 | 12 + 2 | 4,181 | SE terminal ↔ SE terminal |
| line-11 | 6.57 | 2 | 200 | 6.5 | 6 + 1 | 4,181 | N terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 60.32 | False | Unestablished |
| 800.00 | 13.33 | 241.27 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 878,582 kWh mechanical | 320.68 GWh mechanical |
| Nominal auxiliary load | 1,202,040 kWh | 438.74 GWh |
| Auxiliary supply including scenario charging losses | 1,265,305 kWh | 461.84 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.41 GWh |
| Total priced grid-supply scenario | See annual budget | 867.61 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $55.50m | $143.64m | $433.30m |

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
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 47.50 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 21.70 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 39.34 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 34.05 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 40.79 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 4 / 749.2 kW | 94.55 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 10.67 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 11.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 4 / 749.2 kW | 6.57 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,884.7 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,865.8 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,808.1 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 5,886.5 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,972.2 m | 5,554.5 m |
| line-7 | 5 | Coast stops before receiving zone | 6,320.1 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 5,642.6 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,440.1 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,574.9 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 36.91 km |
| Bridge route | 57.77 km |
| Elevated route | 246.77 km |
| Tunnel route | 0.00 km |
| Precast span stock | 30,768 spans |
| Independent supports | 31,548 |
| Running rail | 1,365.79 rail-km / 82,234 t |
| Complete fastening sets | 2,390,137 |
| Protected at-grade crossing packages | 86 |
| Bridge runs / tunnel portals | 169 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,182.5 m; actual accessible paths require survey |
| Pooled depot area | 257,244 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.30m | $5.38m | $35.99m |
| Civil production campaign | $8.77m | $43.16m | $257.44m |

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
| low | make | 12 | 107,688 | 799,968 | 1,066,624 |
| base | make | 30 | 261,528 | 2,092,224 | 2,789,632 |
| high | make | 79 | 707,664 | 5,784,384 | 7,712,512 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 73 | Unestablished | 527,571 | 263.8 |
| Vehicle production / low | 52 | 104 | Unestablished | Unestablished |
| Civil field / low | 112 | 224 | 1,156,992 | Unestablished |
| Civil other installation / low | 991 | 1,982 | 10,299,537 | Unestablished |
| Civil precast / low | 96 | 192 | 1,066,624 | Unestablished |
| Control room and access-site coverage / base | 146 | Unestablished | 1,199,025 | 599.5 |
| Vehicle production / base | 148 | 296 | Unestablished | Unestablished |
| Civil field / base | 414 | 828 | 3,635,072 | Unestablished |
| Civil other installation / base | 8,159 | 16,318 | 71,793,993 | Unestablished |
| Civil precast / base | 240 | 480 | 2,789,632 | Unestablished |
| Control room and access-site coverage / high | 292 | Unestablished | 2,877,660 | 1,438.8 |
| Vehicle production / high | 406 | 812 | Unestablished | Unestablished |
| Civil field / high | 1,800 | 3,600 | 10,076,416 | Unestablished |
| Civil other installation / high | 89,125 | 178,250 | 499,098,297 | Unestablished |
| Civil precast / high | 632 | 1,264 | 7,712,512 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 142 | 583.1 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.749bn | $6.822bn | $44.512bn |
| Installed capital / route-km | $5.12m | $19.98m | $130.36m |
| 30-year whole-life NPV | $3.305bn | $12.197bn | $73.931bn |
| Annual operating provision | $73.96m | $242.24m | $1.226bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.195bn | $1.195bn |
| Guideway | $468.40m | $468.40m |
| Stations power | $699.58m | $699.58m |
| Factory tooling | $48.54m | $48.54m |
| Construction | $3.952bn | $3.952bn |
| Land utilities depot | $311.58m | $311.58m |
| Fleet | $108.37m | $108.37m |
| Energy | $0 | $2.484bn |
| Operations | $0 | $162.20m |
| Maintenance | $0 | $1.388bn |
| Renewals | $0 | $1.123bn |
| Recovery | $38.08m | $77.59m |
| Reliability | $0 | $115.60m |
| Disposal | $0 | $63.10m |

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
| Bridge special foundations deck temporary | $1.503bn | 22.0% |
| City project risk contingency | $1.364bn | 20.0% |
| Network delivered assembled fleet | $899.06m | 13.2% |
| Design prototypes independent review | $403.60m | 5.9% |
| Repeat box beams | $226.41m | 3.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.749bn | $6.822bn | $44.512bn |
| Water-evidence alternative capital | $1.536bn | $5.588bn | $34.477bn |
| Alternative capital / route-km | $4.50m | $16.37m | $100.97m |
| Alternative whole-life NPV | $3.092bn | $10.953bn | $63.659bn |
| Included non-water obstruction reserve | $3.59m | $23.92m | $167.41m |

47.83 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 9 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 118.57m | 0.25 | $29.64m | $-212.59m | $-11.684bn | -0.48 |
| 50% | 118.57m | 0.50 | $59.28m | $-182.95m | $-11.172bn | -0.41 |
| 50% | 118.57m | 1.00 | $118.57m | $-123.67m | $-10.146bn | -0.28 |
| 75% | 177.85m | 0.25 | $44.46m | $-197.77m | $-11.428bn | -0.45 |
| 75% | 177.85m | 0.50 | $88.93m | $-153.31m | $-10.659bn | -0.35 |
| 75% | 177.85m | 1.00 | $177.85m | $-64.38m | $-9.121bn | -0.15 |
| 100% | 237.14m | 0.25 | $59.28m | $-182.95m | $-11.172bn | -0.41 |
| 100% | 237.14m | 0.50 | $118.57m | $-123.67m | $-10.146bn | -0.28 |
| 100% | 237.14m | 1.00 | $237.14m | $-5.10m | $-8.096bn | -0.01 |

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
| low | $1.224bn | $524.62m | $113.18m |
| base | $4.775bn | $2.047bn | $441.53m |
| high | $31.158bn | $13.353bn | $2.881bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/basra.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Basra) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `bd322f488fa2272846263623c64ad9332216291f591838d8ea75a4ee54d1634a` |
| cost_evaluation_id | `8f2fbf3752a98f80111ef3f2a9fba41f60c77b4f3a170cc9a90b961f83760a58` |
| outline_evaluation_id | `3f3afc11300aa043285dc94ccbc78c9d9278c608fe0ea15b117b14a41660349d` |
| research_configuration_id | `a5f95b8a9ad2f1b522278579ee7f5f6e927cf75b575fde093c1f81b22ead7a33` |
| seed_id | `8ddf01854189904647058a0c36e08bee328cbfca3152135bcede40d2bede2e98` |
| selected_alignment_id | `bc02b09285adbbdd6251d26eacf8b3d2f0a69cb64f4a3b7b324fe58f8aa6fcd0` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `1430d812580fa2502506b998f99a0f418b2eef54cf3c680858cc69b8a6406328` |
| source_result_sha256 | `ef5e1f1bd0b455e30a1f4a5d53b8ea66df2bb7b0a6c02f0355e4f2d354e40567` |

Atlas packet `146d752875cec375db98c4f9e5f7549f037a7c8f99d9cda0990d247ae6271f56`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
