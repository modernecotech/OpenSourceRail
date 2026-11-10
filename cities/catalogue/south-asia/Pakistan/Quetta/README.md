# Quetta — railway design and city programme

**PK · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=quetta) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=quetta) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Quetta current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,200,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 128.80 km / 2 trackways |
| Lines / operational platform groups | 6 / 40 |
| Original access markers / separately costed access sites | 41 / 28 |
| Explicit interchange references | 12 |
| Fleet including reserve | 137 six-car trainsets |
| Train distance | 83,461 train-km/day; 30,463,365 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 20.56 | 7 | 200 | 27.5 | 19 + 3 | 4,181 | SW terminal ↔ NE terminal |
| line-2 | 27.21 | 8 | 200 | 36.3 | 24 + 4 | 4,181 | S terminal ↔ NE terminal |
| line-3 | 14.37 | 5 | 200 | 19.1 | 14 + 3 | 4,181 | SW terminal ↔ N terminal |
| line-4 | 54.92 | 16 | 200 | 77.8 | 48 + 8 | 4,181 | Ring / closed circuit |
| line-5 | 4.78 | 2 | 200 | 7.0 | 6 + 1 | 4,181 | S terminal ↔ S terminal |
| line-6 | 6.96 | 2 | 200 | 6.9 | 6 + 1 | 4,181 | NE terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 20.11 | False | Unestablished |
| 800.00 | 13.33 | 80.42 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 340,163 kWh mechanical | 124.16 GWh mechanical |
| Nominal auxiliary load | 442,260 kWh | 161.42 GWh |
| Auxiliary supply including scenario charging losses | 465,537 kWh | 169.92 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 2.90 GWh |
| Total priced grid-supply scenario | See annual budget | 327.68 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $20.88m | $54.25m | $164.81m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 20.56 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 27.21 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 14.37 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 54.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 6.96 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,583.8 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,041.7 m | 5,554.5 m |
| line-3 | 1 | Coast stops before receiving zone | 5,614.3 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 6,949.3 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,959.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 5.30 km |
| Bridge route | 0.34 km |
| Elevated route | 123.16 km |
| Tunnel route | 0.00 km |
| Precast span stock | 12,364 spans |
| Independent supports | 12,410 |
| Running rail | 515.19 rail-km / 31,020 t |
| Complete fastening sets | 901,588 |
| Protected at-grade crossing packages | 16 |
| Bridge runs / tunnel portals | 4 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 68.2 m; actual accessible paths require survey |
| Pooled depot area | 95,836 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $781,364 | $2.70m | $15.22m |
| Civil production campaign | $3.86m | $18.44m | $108.62m |

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
| low | make | 5 | 43,274 | 321,464 | 428,619 |
| base | make | 12 | 105,094 | 840,752 | 1,121,003 |
| high | make | 32 | 284,372 | 2,324,432 | 3,099,243 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 30 | Unestablished | 216,810 | 108.4 |
| Vehicle production / low | 20 | 40 | Unestablished | Unestablished |
| Civil field / low | 45 | 90 | 462,080 | Unestablished |
| Civil other installation / low | 186 | 372 | 1,930,646 | Unestablished |
| Civil precast / low | 40 | 80 | 428,619 | Unestablished |
| Control room and access-site coverage / base | 60 | Unestablished | 492,750 | 246.4 |
| Vehicle production / base | 55 | 110 | Unestablished | Unestablished |
| Civil field / base | 166 | 332 | 1,452,181 | Unestablished |
| Civil other installation / base | 1,319 | 2,638 | 11,607,156 | Unestablished |
| Civil precast / base | 96 | 192 | 1,121,003 | Unestablished |
| Control room and access-site coverage / high | 120 | Unestablished | 1,182,600 | 591.3 |
| Vehicle production / high | 151 | 302 | Unestablished | Unestablished |
| Civil field / high | 719 | 1,438 | 4,026,347 | Unestablished |
| Civil other installation / high | 13,356 | 26,712 | 74,790,839 | Unestablished |
| Civil precast / high | 256 | 512 | 3,099,243 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 56 | 230.0 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $522.75m | $1.782bn | $10.483bn |
| Installed capital / route-km | $4.06m | $13.84m | $81.39m |
| 30-year whole-life NPV | $1.109bn | $3.807bn | $21.558bn |
| Annual operating provision | $27.94m | $91.86m | $468.67m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $452.08m | $452.08m |
| Guideway | $184.52m | $184.52m |
| Stations power | $253.73m | $253.73m |
| Factory tooling | $21.14m | $21.14m |
| Construction | $694.20m | $694.20m |
| Land utilities depot | $120.80m | $120.80m |
| Fleet | $40.73m | $40.73m |
| Energy | $0 | $938.12m |
| Operations | $0 | $66.66m |
| Maintenance | $0 | $524.54m |
| Renewals | $0 | $420.14m |
| Recovery | $14.90m | $30.36m |
| Reliability | $0 | $43.61m |
| Disposal | $0 | $16.48m |

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
| City project risk contingency | $356.42m | 20.0% |
| Network delivered assembled fleet | $333.80m | 18.7% |
| Design prototypes independent review | $105.37m | 5.9% |
| Repeat box beams | $90.98m | 5.1% |
| Shared access and transfer complexes | $88.03m | 4.9% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $522.75m | $1.782bn | $10.483bn |
| Water-evidence alternative capital | $521.62m | $1.775bn | $10.429bn |
| Alternative capital / route-km | $4.05m | $13.78m | $80.97m |
| Alternative whole-life NPV | $1.107bn | $3.800bn | $21.503bn |
| Included non-water obstruction reserve | $23,479 | $156,529 | $1.10m |

0.31 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 1 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 64.67m | 0.25 | $16.17m | $-75.69m | $-3.528bn | -0.66 |
| 50% | 64.67m | 0.50 | $32.34m | $-59.52m | $-3.248bn | -0.52 |
| 50% | 64.67m | 1.00 | $64.67m | $-27.18m | $-2.689bn | -0.24 |
| 75% | 97.01m | 0.25 | $24.25m | $-67.60m | $-3.388bn | -0.59 |
| 75% | 97.01m | 0.50 | $48.51m | $-43.35m | $-2.968bn | -0.38 |
| 75% | 97.01m | 1.00 | $97.01m | $5.15m | $-2.130bn | 0.04 |
| 100% | 129.35m | 0.25 | $32.34m | $-59.52m | $-3.248bn | -0.52 |
| 100% | 129.35m | 0.50 | $64.67m | $-27.18m | $-2.689bn | -0.24 |
| 100% | 129.35m | 1.00 | $129.35m | $37.49m | $-1.570bn | 0.33 |

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
| low | $365.93m | $156.83m | $33.83m |
| base | $1.247bn | $534.63m | $115.34m |
| high | $7.338bn | $3.145bn | $678.49m |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/quetta.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Pakistan/Quetta) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `dc9abe68f6e9c2b2fd66defed7a8d6f73600e84248933f20b5c6612c54aea40c` |
| cost_evaluation_id | `eb37ae11b44f2361727e6e698bfa5b5bf1311b62f4f50d798986666d14536cf5` |
| outline_evaluation_id | `94b2535d782eb68be1bbd111447b76e5347afd2c16dc3fef1b7d49bd3afdea4d` |
| research_configuration_id | `189cea4d62de68e163c4f2c2a8fe8fbe28859401dd8f1f3a3828f4b78db2cafe` |
| seed_id | `41c82abd1f11c77c7923ac714f6637309f46cc4b0325d96dcd4aac85a96a20c2` |
| selected_alignment_id | `25ee4d6b363df34a4e4d6f004eec6dc0928eff61fa29db3b15440b4c224ee2d7` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `4434c29ac2bb437a79429340abd3c83aaf9145cf288d2dfbad7ca7b36fee0c7f` |
| source_result_sha256 | `441cf401999ebff2b91e34184d374889645be6d0e0e1c174e05684017f55a626` |

Atlas packet `68b605a8abeb5ffe5aea0cda185bbadd223c63d7045bfc7fbee473f8191c86ef`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
