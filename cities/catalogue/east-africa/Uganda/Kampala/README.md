# Kampala — railway design and city programme

**UG · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=kampala) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=kampala) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Kampala current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,875,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 231.14 km / 2 trackways |
| Lines / operational platform groups | 9 / 95 |
| Original access markers / separately costed access sites | 108 / 50 |
| Explicit interchange references | 23 |
| Fleet including reserve | 277 six-car trainsets |
| Train distance | 149,775 train-km/day; 54,668,050 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 36.78 | 15 | 200 | 68.5 | 43 + 7 | 4,181 | E terminal ↔ SW terminal |
| line-2 | 20.65 | 13 | 200 | 37.7 | 25 + 4 | 4,181 | S terminal ↔ NW terminal |
| line-3 | 23.36 | 9 | 200 | 33.4 | 22 + 4 | 4,181 | S terminal ↔ N terminal |
| line-4 | 32.28 | 14 | 200 | 48.2 | 31 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-5 | 30.39 | 12 | 200 | 44.5 | 29 + 5 | 4,181 | NE terminal ↔ S terminal |
| line-6 | 59.02 | 18 | 200 | 84.8 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 4.61 | 2 | 200 | 6.6 | 6 + 1 | 4,181 | SW terminal ↔ W terminal |
| line-8 | 11.64 | 8 | 200 | 26.2 | 18 + 3 | 4,181 | SE terminal ↔ SE terminal |
| line-9 | 12.40 | 4 | 200 | 16.1 | 12 + 2 | 4,181 | E terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 47.75 | False | Unestablished |
| 800.00 | 13.33 | 191.01 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 580,024 kWh mechanical | 211.71 GWh mechanical |
| Nominal auxiliary load | 899,640 kWh | 328.37 GWh |
| Auxiliary supply including scenario charging losses | 946,989 kWh | 345.65 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.66 GWh |
| Total priced grid-supply scenario | See annual budget | 617.84 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $39.76m | $102.29m | $304.56m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
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
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 4 / 749.2 kW | 23.36 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 4 / 749.2 kW | 32.28 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 4 / 749.2 kW | 30.39 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 59.02 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 12.40 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-3 | 1 | Coast stops before receiving zone | 5,699.2 m | 5,554.5 m |
| line-4 | 2 | Coast stops before receiving zone | 5,644.3 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,286.6 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,492.0 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,383.0 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 13.72 km |
| Bridge route | 0.57 km |
| Elevated route | 216.84 km |
| Tunnel route | 0.00 km |
| Precast span stock | 22,388 spans |
| Independent supports | 22,720 |
| Running rail | 944.78 rail-km / 56,885 t |
| Complete fastening sets | 1,653,366 |
| Protected at-grade crossing packages | 116 |
| Bridge runs / tunnel portals | 14 / 0 |
| Additional station track | 10,120 m |
| Access connector allowance | 1,005.3 m; actual accessible paths require survey |
| Pooled depot area | 193,388 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.05m | $4.44m | $27.36m |
| Civil production campaign | $6.54m | $31.99m | $190.14m |

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
| low | make | 9 | 78,358 | 582,088 | 776,117 |
| base | make | 22 | 190,298 | 1,522,384 | 2,029,845 |
| high | make | 58 | 514,924 | 4,208,944 | 5,611,925 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 52 | Unestablished | 375,804 | 187.9 |
| Vehicle production / low | 39 | 78 | Unestablished | Unestablished |
| Civil field / low | 81 | 162 | 839,360 | Unestablished |
| Civil other installation / low | 600 | 1,200 | 6,236,454 | Unestablished |
| Civil precast / low | 72 | 144 | 776,117 | Unestablished |
| Control room and access-site coverage / base | 104 | Unestablished | 854,100 | 427.1 |
| Vehicle production / base | 111 | 222 | Unestablished | Unestablished |
| Civil field / base | 300 | 600 | 2,637,483 | Unestablished |
| Civil other installation / base | 3,748 | 7,496 | 32,975,591 | Unestablished |
| Civil precast / base | 176 | 352 | 2,029,845 | Unestablished |
| Control room and access-site coverage / high | 208 | Unestablished | 2,049,840 | 1,024.9 |
| Vehicle production / high | 305 | 610 | Unestablished | Unestablished |
| Civil field / high | 1,306 | 2,612 | 7,311,893 | Unestablished |
| Civil other installation / high | 33,480 | 66,960 | 187,486,690 | Unestablished |
| Civil precast / high | 464 | 928 | 5,611,925 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 100 | 410.6 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.138bn | $3.886bn | $22.285bn |
| Installed capital / route-km | $4.92m | $16.81m | $96.42m |
| 30-year whole-life NPV | $2.304bn | $7.955bn | $44.444bn |
| Annual operating provision | $54.36m | $180.11m | $919.77m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $831.14m | $831.14m |
| Guideway | $335.43m | $335.43m |
| Stations power | $777.79m | $777.79m |
| Factory tooling | $36.43m | $36.43m |
| Construction | $1.579bn | $1.579bn |
| Land utilities depot | $223.04m | $223.04m |
| Fleet | $77.38m | $77.38m |
| Energy | $0 | $1.769bn |
| Operations | $0 | $115.54m |
| Maintenance | $0 | $1.124bn |
| Renewals | $0 | $918.02m |
| Recovery | $26.49m | $53.97m |
| Reliability | $0 | $78.26m |
| Disposal | $0 | $35.95m |

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
| City project risk contingency | $777.25m | 20.0% |
| Network delivered assembled fleet | $674.91m | 17.4% |
| Design prototypes independent review | $229.58m | 5.9% |
| Repeat box beams | $164.75m | 4.2% |
| Shared access and transfer complexes | $158.76m | 4.1% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.138bn | $3.886bn | $22.285bn |
| Water-evidence alternative capital | $1.141bn | $3.902bn | $22.412bn |
| Alternative capital / route-km | $4.94m | $16.88m | $96.97m |
| Alternative whole-life NPV | $2.307bn | $7.971bn | $44.575bn |
| Included non-water obstruction reserve | $16,524 | $110,159 | $771,111 |

0.22 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 2 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-155.86m | $-7.535bn | -0.62 |
| 50% | 97.01m | 0.50 | $48.51m | $-131.60m | $-7.116bn | -0.52 |
| 50% | 97.01m | 1.00 | $97.01m | $-83.10m | $-6.277bn | -0.33 |
| 75% | 145.52m | 0.25 | $36.38m | $-143.73m | $-7.326bn | -0.57 |
| 75% | 145.52m | 0.50 | $72.76m | $-107.35m | $-6.697bn | -0.43 |
| 75% | 145.52m | 1.00 | $145.52m | $-34.59m | $-5.438bn | -0.14 |
| 100% | 194.02m | 0.25 | $48.51m | $-131.60m | $-7.116bn | -0.52 |
| 100% | 194.02m | 0.50 | $97.01m | $-83.10m | $-6.277bn | -0.33 |
| 100% | 194.02m | 1.00 | $194.02m | $13.91m | $-4.600bn | 0.06 |

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
| low | $796.80m | $341.48m | $73.67m |
| base | $2.720bn | $1.166bn | $251.53m |
| high | $15.600bn | $6.686bn | $1.442bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/kampala.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/east-africa/Uganda/Kampala) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `17309e464d35f35689441cfa00a83dec299ceaa27fb223300847577280239c35` |
| cost_evaluation_id | `9210d087b27a70a51f0d1f2aff8a7538a0ef7facc3a14244993552b28055f37a` |
| outline_evaluation_id | `7f0c246d2aee492c646d41a4efbdcc0de41ec912fe2637fbfd5af5d6341ddc28` |
| research_configuration_id | `c09a9a4c61144df7a4b3d583e43a627ad8b5f0bff9a652db8c68401275204b30` |
| seed_id | `e029946963d9f2fa515f70ae56be5e7a97716b36e477eba6d968188b48a84059` |
| selected_alignment_id | `912dfeb48ac0618fc094f2e4eed2c3098cf8628af6eb7969284807375d4a1c1e` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `359ee507bea7692c06864a170c9cc59b87b1759a49a9114351ece7958d08a474` |
| source_result_sha256 | `bdfbdfccd623345bcb8445da30ba5d00a629a873a723b70357214f4f44a33300` |

Atlas packet `ba9366e79a89243d7f0cac6d8e15f271b76aad5e3f7bbd6aeeb9345efa63b162`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
