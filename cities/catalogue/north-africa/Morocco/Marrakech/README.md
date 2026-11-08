# Marrakech — railway design and city programme

**MA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=marrakech) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=marrakech) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Marrakech current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,200,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 219.67 km / 2 trackways |
| Lines / operational platform groups | 9 / 104 |
| Original access markers / separately costed access sites | 128 / 54 |
| Explicit interchange references | 21 |
| Fleet including reserve | 274 six-car trainsets |
| Train distance | 142,345 train-km/day; 51,955,748 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 27.75 | 12 | 200 | 41.4 | 27 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-2 | 30.07 | 12 | 200 | 58.0 | 37 + 6 | 4,181 | NE terminal ↔ SW terminal |
| line-3 | 21.11 | 8 | 200 | 29.3 | 20 + 3 | 4,181 | W terminal ↔ E terminal |
| line-4 | 29.25 | 13 | 200 | 44.1 | 29 + 5 | 4,181 | SW terminal ↔ N terminal |
| line-5 | 35.83 | 23 | 200 | 62.1 | 40 + 6 | 4,181 | S terminal ↔ NW terminal |
| line-6 | 52.94 | 24 | 200 | 84.2 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 5.91 | 3 | 200 | 9.1 | 8 + 2 | 4,181 | SW terminal ↔ E terminal |
| line-8 | 4.93 | 3 | 200 | 8.6 | 7 + 2 | 4,181 | SE terminal ↔ S terminal |
| line-9 | 11.87 | 6 | 200 | 19.4 | 14 + 3 | 4,181 | S terminal ↔ E terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 52.28 | False | Unestablished |
| 800.00 | 13.33 | 209.10 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 579,001 kWh mechanical | 211.34 GWh mechanical |
| Nominal auxiliary load | 884,520 kWh | 322.85 GWh |
| Auxiliary supply including scenario charging losses | 931,074 kWh | 339.84 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.81 GWh |
| Total priced grid-supply scenario | See annual budget | 611.77 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $39.24m | $101.29m | $303.54m |

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
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 27.75 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 21.11 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 29.25 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 35.83 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 52.94 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 5,860.3 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 5,815.4 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,877.6 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,562.5 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,855.4 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 26.21 km |
| Bridge route | 7.31 km |
| Elevated route | 186.14 km |
| Tunnel route | 0.00 km |
| Precast span stock | 19,716 spans |
| Independent supports | 20,024 |
| Running rail | 889.23 rail-km / 53,541 t |
| Complete fastening sets | 1,556,153 |
| Protected at-grade crossing packages | 62 |
| Bridge runs / tunnel portals | 43 / 0 |
| Additional station track | 5,280 m |
| Access connector allowance | 1,853.1 m; actual accessible paths require survey |
| Pooled depot area | 191,672 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.39m | $27.12m |
| Civil production campaign | $5.85m | $28.35m | $168.30m |

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
| low | make | 8 | 69,006 | 512,616 | 683,488 |
| base | make | 19 | 167,586 | 1,340,688 | 1,787,584 |
| high | make | 51 | 453,468 | 3,706,608 | 4,942,144 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 56 | Unestablished | 404,712 | 202.4 |
| Vehicle production / low | 39 | 78 | Unestablished | Unestablished |
| Civil field / low | 72 | 144 | 739,349 | Unestablished |
| Civil other installation / low | 530 | 1,060 | 5,509,135 | Unestablished |
| Civil precast / low | 64 | 128 | 683,488 | Unestablished |
| Control room and access-site coverage / base | 112 | Unestablished | 919,800 | 459.9 |
| Vehicle production / base | 110 | 220 | Unestablished | Unestablished |
| Civil field / base | 264 | 528 | 2,323,200 | Unestablished |
| Civil other installation / base | 3,576 | 7,152 | 31,462,870 | Unestablished |
| Civil precast / base | 152 | 304 | 1,787,584 | Unestablished |
| Control room and access-site coverage / high | 224 | Unestablished | 2,207,520 | 1,103.8 |
| Vehicle production / high | 301 | 602 | Unestablished | Unestablished |
| Civil field / high | 1,151 | 2,302 | 6,440,555 | Unestablished |
| Civil other installation / high | 34,542 | 69,084 | 193,434,389 | Unestablished |
| Civil precast / high | 408 | 816 | 4,942,144 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 108 | 443.5 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.068bn | $3.730bn | $21.935bn |
| Installed capital / route-km | $4.86m | $16.98m | $99.86m |
| 30-year whole-life NPV | $2.200bn | $7.661bn | $43.471bn |
| Annual operating provision | $53.01m | $174.93m | $892.35m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $846.11m | $846.11m |
| Guideway | $301.69m | $301.69m |
| Stations power | $658.03m | $658.03m |
| Factory tooling | $32.74m | $32.74m |
| Construction | $1.572bn | $1.572bn |
| Land utilities depot | $216.12m | $216.12m |
| Fleet | $77.99m | $77.99m |
| Energy | $0 | $1.751bn |
| Operations | $0 | $124.42m |
| Maintenance | $0 | $1.049bn |
| Renewals | $0 | $871.49m |
| Recovery | $24.83m | $50.60m |
| Reliability | $0 | $74.37m |
| Disposal | $0 | $34.50m |

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
| City project risk contingency | $745.99m | 20.0% |
| Network delivered assembled fleet | $667.60m | 17.9% |
| Bridge special foundations deck temporary | $223.57m | 6.0% |
| Design prototypes independent review | $220.43m | 5.9% |
| Shared access and transfer complexes | $167.62m | 4.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.068bn | $3.730bn | $21.935bn |
| Water-evidence alternative capital | $1.029bn | $3.507bn | $20.124bn |
| Alternative capital / route-km | $4.69m | $15.97m | $91.61m |
| Alternative whole-life NPV | $2.161bn | $7.436bn | $41.614bn |
| Included non-water obstruction reserve | $527,782 | $3.52m | $24.63m |

7.04 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-150.68m | $-7.242bn | -0.62 |
| 50% | 97.01m | 0.50 | $48.51m | $-126.43m | $-6.822bn | -0.52 |
| 50% | 97.01m | 1.00 | $97.01m | $-77.92m | $-5.983bn | -0.32 |
| 75% | 145.52m | 0.25 | $36.38m | $-138.55m | $-7.032bn | -0.57 |
| 75% | 145.52m | 0.50 | $72.76m | $-102.17m | $-6.403bn | -0.42 |
| 75% | 145.52m | 1.00 | $145.52m | $-29.42m | $-5.145bn | -0.12 |
| 100% | 194.02m | 0.25 | $48.51m | $-126.43m | $-6.822bn | -0.52 |
| 100% | 194.02m | 0.50 | $97.01m | $-77.92m | $-5.983bn | -0.32 |
| 100% | 194.02m | 1.00 | $194.02m | $19.09m | $-4.306bn | 0.08 |

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
| low | $747.40m | $320.31m | $69.11m |
| base | $2.611bn | $1.119bn | $241.42m |
| high | $15.355bn | $6.581bn | $1.420bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/marrakech.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/north-africa/Morocco/Marrakech) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `652fddc7be86a7722ad15142a354e5580434d239212de8a93e63507d92b9e8d3` |
| cost_evaluation_id | `d663a76d1c5bc31419f855ea26f99d23dfba84b4c77a25b6aa026d4a399e623a` |
| outline_evaluation_id | `214dfae12864e0e27430cb159dbfc23b9525d7b95f23c54f431303c234601898` |
| research_configuration_id | `8170ea1c553f8de4ff7b830f786134d8d61015eaf38bcb2ba3fd7b877eac1abd` |
| seed_id | `d0c6fb7435b3117c03081de060abc5e3b1cbd28be2eecbddb3ba8e3ea6eab52c` |
| selected_alignment_id | `eea87832aa820286d4f2e6f27f0edbf88385bcd4ea4de1b3288860e3e83c081e` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `72c048fb372959924821183162bd00b3c2487612c99c5633737b0096224ca013` |
| source_result_sha256 | `681fef76dac45854cdb86500e67ed30811dc2e357e7fffdd9b9ce8b5ab3b3bf1` |

Atlas packet `aa00f2099b5c07a62ec87b9a323d622f6c1f1da984d55144c72a7a4a5bc7e256`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
