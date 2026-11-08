# Lucknow — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=lucknow) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=lucknow) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Lucknow current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,500,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 345.34 km / 2 trackways |
| Lines / operational platform groups | 8 / 109 |
| Original access markers / separately costed access sites | 111 / 70 |
| Explicit interchange references | 29 |
| Fleet including reserve | 356 six-car trainsets |
| Train distance | 223,780 train-km/day; 81,679,718 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 51.03 | 17 | 200 | 72.3 | 46 + 7 | 4,181 | W terminal ↔ E terminal |
| line-2 | 25.50 | 10 | 200 | 36.3 | 24 + 4 | 4,181 | S terminal ↔ N terminal |
| line-3 | 20.28 | 9 | 200 | 30.1 | 20 + 3 | 4,181 | SW terminal ↔ E terminal |
| line-4 | 23.21 | 8 | 200 | 32.4 | 22 + 4 | 4,181 | SE terminal ↔ NE terminal |
| line-5 | 46.76 | 15 | 200 | 64.8 | 41 + 7 | 4,181 | SW terminal ↔ NE terminal |
| line-6 | 39.74 | 14 | 200 | 57.2 | 37 + 6 | 4,181 | SE terminal ↔ W terminal |
| line-7 | 38.92 | 12 | 200 | 53.2 | 34 + 6 | 4,181 | SE terminal ↔ W terminal |
| line-8 | 99.88 | 24 | 200 | 134.4 | 82 + 13 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 54.79 | False | Unestablished |
| 800.00 | 13.33 | 219.16 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 931,989 kWh mechanical | 340.18 GWh mechanical |
| Nominal auxiliary load | 1,156,680 kWh | 422.19 GWh |
| Auxiliary supply including scenario charging losses | 1,217,558 kWh | 444.41 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 7.26 GWh |
| Total priced grid-supply scenario | See annual budget | 871.59 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $55.60m | $144.30m | $437.92m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 51.03 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 25.50 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 20.28 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 23.21 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 46.76 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 39.74 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 38.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 99.88 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,269.8 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 5,592.3 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,640.9 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 5,619.7 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,082.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,208.4 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,992.0 m | 5,554.5 m |
| line-8 | 5 | Coast stops before receiving zone | 6,560.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 37.22 km |
| Bridge route | 17.46 km |
| Elevated route | 290.66 km |
| Tunnel route | 0.00 km |
| Precast span stock | 31,128 spans |
| Independent supports | 31,902 |
| Running rail | 1,381.36 rail-km / 83,172 t |
| Complete fastening sets | 2,417,378 |
| Protected at-grade crossing packages | 178 |
| Bridge runs / tunnel portals | 111 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 126.5 m; actual accessible paths require survey |
| Pooled depot area | 248,560 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.22m | $5.38m | $35.22m |
| Civil production campaign | $8.88m | $43.59m | $260.59m |

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
| low | make | 13 | 108,948 | 809,328 | 1,079,104 |
| base | make | 30 | 264,588 | 2,116,704 | 2,822,272 |
| high | make | 80 | 715,944 | 5,852,064 | 7,802,752 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 72 | Unestablished | 520,344 | 260.2 |
| Vehicle production / low | 50 | 100 | Unestablished | Unestablished |
| Civil field / low | 113 | 226 | 1,170,368 | Unestablished |
| Civil other installation / low | 709 | 1,418 | 7,369,374 | Unestablished |
| Civil precast / low | 104 | 208 | 1,079,104 | Unestablished |
| Control room and access-site coverage / base | 144 | Unestablished | 1,182,600 | 591.3 |
| Vehicle production / base | 143 | 286 | Unestablished | Unestablished |
| Civil field / base | 418 | 836 | 3,677,120 | Unestablished |
| Civil other installation / base | 5,577 | 11,154 | 49,071,966 | Unestablished |
| Civil precast / base | 240 | 480 | 2,822,272 | Unestablished |
| Control room and access-site coverage / high | 288 | Unestablished | 2,838,240 | 1,419.1 |
| Vehicle production / high | 391 | 782 | Unestablished | Unestablished |
| Civil field / high | 1,821 | 3,642 | 10,193,024 | Unestablished |
| Civil other installation / high | 59,211 | 118,422 | 331,579,638 | Unestablished |
| Civil precast / high | 640 | 1,280 | 7,802,752 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 140 | 574.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.542bn | $5.629bn | $34.920bn |
| Installed capital / route-km | $4.46m | $16.30m | $101.12m |
| 30-year whole-life NPV | $3.087bn | $10.941bn | $63.680bn |
| Annual operating provision | $73.82m | $241.19m | $1.215bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.191bn | $1.191bn |
| Guideway | $473.83m | $473.83m |
| Stations power | $643.68m | $643.68m |
| Factory tooling | $48.97m | $48.97m |
| Construction | $2.818bn | $2.818bn |
| Land utilities depot | $307.70m | $307.70m |
| Fleet | $106.82m | $106.82m |
| Energy | $0 | $2.495bn |
| Operations | $0 | $159.97m |
| Maintenance | $0 | $1.357bn |
| Renewals | $0 | $1.089bn |
| Recovery | $39.74m | $80.96m |
| Reliability | $0 | $116.92m |
| Disposal | $0 | $52.07m |

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
| City project risk contingency | $1.126bn | 20.0% |
| Network delivered assembled fleet | $867.39m | 15.4% |
| Bridge special foundations deck temporary | $548.78m | 9.7% |
| Design prototypes independent review | $332.99m | 5.9% |
| Repeat box beams | $229.06m | 4.1% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.542bn | $5.629bn | $34.920bn |
| Water-evidence alternative capital | $1.449bn | $5.091bn | $30.547bn |
| Alternative capital / route-km | $4.20m | $14.74m | $88.45m |
| Alternative whole-life NPV | $2.994bn | $10.397bn | $59.194bn |
| Included non-water obstruction reserve | $1.11m | $7.39m | $51.75m |

14.79 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 4 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-219.63m | $-10.568bn | -0.60 |
| 50% | 86.23m | 0.50 | $43.12m | $-198.07m | $-10.195bn | -0.54 |
| 50% | 86.23m | 1.00 | $86.23m | $-154.95m | $-9.450bn | -0.43 |
| 75% | 129.35m | 0.25 | $32.34m | $-208.85m | $-10.382bn | -0.57 |
| 75% | 129.35m | 0.50 | $64.67m | $-176.51m | $-9.822bn | -0.48 |
| 75% | 129.35m | 1.00 | $129.35m | $-111.84m | $-8.704bn | -0.31 |
| 100% | 172.46m | 0.25 | $43.12m | $-198.07m | $-10.195bn | -0.54 |
| 100% | 172.46m | 0.50 | $86.23m | $-154.95m | $-9.450bn | -0.43 |
| 100% | 172.46m | 1.00 | $172.46m | $-68.72m | $-7.959bn | -0.19 |

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
| low | $1.079bn | $462.53m | $99.79m |
| base | $3.941bn | $1.689bn | $364.35m |
| high | $24.444bn | $10.476bn | $2.260bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/lucknow.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Lucknow) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `dd2a971791e6e2564b80437e441a671903bb8c8e0e8a1d32da02fa2ed5891269` |
| cost_evaluation_id | `6affead2bf3f3b39f5b6075a5d49088b4a17c7dfe88ed10e2e05620aa4c268cc` |
| outline_evaluation_id | `29d00c937ecb643677149fb0b6a969433b013e75bb0a1624d4ab1740cf5bd538` |
| research_configuration_id | `e1bc9e72bc4b08c33b7add01e1a6d93aea05b0116217f9acfd7ac9bc9c07514d` |
| seed_id | `b04dd20b40f0a26b1fdf3059106d08967acc320c614d6cc3d2b5e7dd086d9fdf` |
| selected_alignment_id | `8ffae60fd603c40611c94cdb5ce2712217f67b3d61f1a676889a25cc2ce7a60d` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `5947fd8aa2d56965c25eca4a90569d10d4b42f8ab40d6521e47c41f3c6e1fe3f` |
| source_result_sha256 | `e77f7199e24e10c8791d9ea24ca527d1e98526f7aec4232c34be8209e4368eb9` |

Atlas packet `16134c33150e0185f83e235fcefa7980fa2702a2ca42e3a5c2190ccd2c06c0bf`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
