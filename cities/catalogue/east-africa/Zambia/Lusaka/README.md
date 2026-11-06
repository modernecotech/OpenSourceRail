# Lusaka — railway design and city programme

**ZM · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=lusaka) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=lusaka) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Lusaka current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,037,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 293.18 km / 2 trackways |
| Lines / operational platform groups | 12 / 110 |
| Original access markers / separately costed access sites | 113 / 60 |
| Explicit interchange references | 32 |
| Fleet including reserve | 340 six-car trainsets |
| Train distance | 189,980 train-km/day; 69,342,606 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 33.59 | 11 | 200 | 47.3 | 31 + 5 | 4,181 | NE terminal ↔ W terminal |
| line-2 | 29.18 | 11 | 200 | 41.8 | 27 + 5 | 4,181 | E terminal ↔ SW terminal |
| line-3 | 25.46 | 11 | 200 | 43.5 | 28 + 5 | 4,181 | SE terminal ↔ W terminal |
| line-4 | 18.53 | 12 | 200 | 38.5 | 25 + 4 | 4,181 | E terminal ↔ NW terminal |
| line-5 | 29.09 | 10 | 200 | 41.7 | 27 + 5 | 4,181 | N terminal ↔ S terminal |
| line-6 | 27.64 | 11 | 200 | 46.0 | 30 + 5 | 4,181 | NE terminal ↔ W terminal |
| line-7 | 28.89 | 8 | 200 | 37.7 | 25 + 4 | 4,181 | N terminal ↔ SW terminal |
| line-8 | 74.93 | 26 | 200 | 110.3 | 68 + 11 | 4,181 | Ring / closed circuit |
| line-9 | 6.93 | 3 | 200 | 10.8 | 9 + 2 | 4,181 | N terminal ↔ N terminal |
| line-10 | 5.65 | 2 | 200 | 5.7 | 6 + 1 | 4,181 | S terminal ↔ SW terminal |
| line-11 | 5.74 | 2 | 200 | 5.8 | 6 + 1 | 4,181 | SE terminal ↔ SE terminal |
| line-12 | 7.55 | 3 | 200 | 9.5 | 8 + 2 | 4,181 | SW terminal ↔ S terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 55.29 | False | Unestablished |
| 800.00 | 13.33 | 221.17 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 731,605 kWh mechanical | 267.04 GWh mechanical |
| Nominal auxiliary load | 1,096,200 kWh | 400.11 GWh |
| Auxiliary supply including scenario charging losses | 1,153,895 kWh | 421.17 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.26 GWh |
| Total priced grid-supply scenario | See annual budget | 762.92 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $49.06m | $126.31m | $376.74m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Station launch reference | 0 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |
| line-10 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 33.59 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 29.18 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 29.09 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-7 | 4 / 749.2 kW | 28.89 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 74.93 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-10 | 4 / 749.2 kW | 5.65 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-11 | 4 / 749.2 kW | 5.74 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 4 / 749.2 kW | 7.55 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,127.7 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,799.0 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,903.4 m | 5,554.5 m |
| line-7 | 2 | Coast stops before receiving zone | 6,811.1 m | 5,554.5 m |
| line-8 | 3 | Coast stops before receiving zone | 6,271.6 m | 5,554.5 m |
| line-10 | 1 | Coast stops before receiving zone | 5,647.0 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 5,736.3 m | 5,554.5 m |
| line-12 | 1 | Coast stops before receiving zone | 5,603.8 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 37.81 km |
| Bridge route | 0.18 km |
| Elevated route | 255.20 km |
| Tunnel route | 0.00 km |
| Precast span stock | 25,584 spans |
| Independent supports | 25,786 |
| Running rail | 1,172.71 rail-km / 70,609 t |
| Complete fastening sets | 2,052,251 |
| Protected at-grade crossing packages | 107 |
| Bridge runs / tunnel portals | 3 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 236.5 m; actual accessible paths require survey |
| Pooled depot area | 236,912 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.15m | $5.16m | $33.80m |
| Civil production campaign | $7.37m | $36.23m | $215.67m |

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
| low | make | 10 | 89,544 | 665,184 | 886,912 |
| base | make | 25 | 217,464 | 1,739,712 | 2,319,616 |
| high | make | 66 | 588,432 | 4,809,792 | 6,413,056 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 62 | Unestablished | 448,074 | 224.0 |
| Vehicle production / low | 48 | 96 | Unestablished | Unestablished |
| Civil field / low | 93 | 186 | 957,291 | Unestablished |
| Civil other installation / low | 535 | 1,070 | 5,555,788 | Unestablished |
| Civil precast / low | 80 | 160 | 886,912 | Unestablished |
| Control room and access-site coverage / base | 124 | Unestablished | 1,018,350 | 509.2 |
| Vehicle production / base | 136 | 272 | Unestablished | Unestablished |
| Civil field / base | 342 | 684 | 3,008,320 | Unestablished |
| Civil other installation / base | 3,462 | 6,924 | 30,458,408 | Unestablished |
| Civil precast / base | 200 | 400 | 2,319,616 | Unestablished |
| Control room and access-site coverage / high | 248 | Unestablished | 2,444,040 | 1,222.0 |
| Vehicle production / high | 374 | 748 | Unestablished | Unestablished |
| Civil field / high | 1,490 | 2,980 | 8,340,565 | Unestablished |
| Civil other installation / high | 32,535 | 65,070 | 182,190,705 | Unestablished |
| Civil precast / high | 528 | 1,056 | 6,413,056 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 120 | 492.8 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.238bn | $4.208bn | $24.190bn |
| Installed capital / route-km | $4.22m | $14.35m | $82.51m |
| 30-year whole-life NPV | $2.626bn | $9.011bn | $50.201bn |
| Annual operating provision | $65.58m | $215.16m | $1.090bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.041bn | $1.041bn |
| Guideway | $393.55m | $393.55m |
| Stations power | $726.71m | $726.71m |
| Factory tooling | $41.38m | $41.38m |
| Construction | $1.599bn | $1.599bn |
| Land utilities depot | $277.26m | $277.26m |
| Fleet | $96.24m | $96.24m |
| Energy | $0 | $2.184bn |
| Operations | $0 | $137.76m |
| Maintenance | $0 | $1.265bn |
| Renewals | $0 | $1.043bn |
| Recovery | $33.11m | $67.47m |
| Reliability | $0 | $99.26m |
| Disposal | $0 | $38.92m |

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
| City project risk contingency | $841.63m | 20.0% |
| Network delivered assembled fleet | $828.40m | 19.7% |
| Design prototypes independent review | $248.70m | 5.9% |
| Shared access and transfer complexes | $194.91m | 4.6% |
| Repeat box beams | $188.27m | 4.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.238bn | $4.208bn | $24.190bn |
| Water-evidence alternative capital | $1.239bn | $4.213bn | $24.230bn |
| Alternative capital / route-km | $4.23m | $14.37m | $82.65m |
| Alternative whole-life NPV | $2.627bn | $9.016bn | $50.242bn |
| Included non-water obstruction reserve | $1,757 | $11,716 | $82,013 |

0.02 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 129.35m | 0.25 | $32.34m | $-182.82m | $-8.452bn | -0.67 |
| 50% | 129.35m | 0.50 | $64.67m | $-150.49m | $-7.893bn | -0.55 |
| 50% | 129.35m | 1.00 | $129.35m | $-85.81m | $-6.774bn | -0.32 |
| 75% | 194.02m | 0.25 | $48.51m | $-166.65m | $-8.172bn | -0.61 |
| 75% | 194.02m | 0.50 | $97.01m | $-118.15m | $-7.334bn | -0.43 |
| 75% | 194.02m | 1.00 | $194.02m | $-21.14m | $-5.656bn | -0.08 |
| 100% | 258.70m | 0.25 | $64.67m | $-150.49m | $-7.893bn | -0.55 |
| 100% | 258.70m | 0.50 | $129.35m | $-85.81m | $-6.774bn | -0.32 |
| 100% | 258.70m | 1.00 | $258.70m | $43.54m | $-4.538bn | 0.16 |

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
| low | $866.72m | $371.45m | $80.14m |
| base | $2.946bn | $1.262bn | $272.37m |
| high | $16.933bn | $7.257bn | $1.566bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/lusaka.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Zambia/Lusaka) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `1edb17c54f271efd7cccff0a816b3b3fd40f95370803f57ec6714bc3e5003cf8` |
| cost_evaluation_id | `ad53b188ac38caa2d5b5b68f633ffe2b0c73b5b750d4c698c29b38acd4b6efff` |
| outline_evaluation_id | `3cf16f071931333a641ade19d7bc75d5ad414dd6981bb62d36a22c8ec864080e` |
| research_configuration_id | `af5191169d44535e6f4e19be1524da3c7e6d6ccc92ba557e88a41e9868f4b583` |
| seed_id | `f9d54e93ba1548cb8ced19c475836242a2488718ea2db48a3e60b866985fc96c` |
| selected_alignment_id | `689a9b18303a28e5408213387d9c3841664dc4fa11696b53698aa951f8175205` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `eb44f1fb31831f58e22ba0f8518787431a82e097c49518fc4463a5ef6613d0e5` |
| source_result_sha256 | `232c8a4dfacf30f356a6bc5335615c094fe4aadf7ae1845c31729b7a7b5d0958` |

Atlas packet `6570763f1000bb49b04edf9056582c37eae87e6a5bc25e0fa07da7d452598843`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
