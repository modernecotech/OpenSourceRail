# Maiduguri — railway design and city programme

**NG · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=maiduguri) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=maiduguri) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Maiduguri current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,200,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 189.45 km / 2 trackways |
| Lines / operational platform groups | 8 / 66 |
| Original access markers / separately costed access sites | 68 / 42 |
| Explicit interchange references | 18 |
| Fleet including reserve | 220 six-car trainsets |
| Train distance | 122,762 train-km/day; 44,808,051 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 22.97 | 8 | 200 | 32.2 | 22 + 4 | 4,181 | NW terminal ↔ SE terminal |
| line-2 | 20.01 | 9 | 200 | 29.9 | 20 + 3 | 4,181 | W terminal ↔ E terminal |
| line-3 | 29.99 | 12 | 200 | 44.9 | 29 + 5 | 4,181 | N terminal ↔ SW terminal |
| line-4 | 27.95 | 10 | 200 | 48.2 | 31 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-5 | 63.85 | 17 | 200 | 88.5 | 54 + 9 | 4,181 | Ring / closed circuit |
| line-6 | 5.60 | 2 | 200 | 5.7 | 6 + 1 | 4,181 | NE terminal ↔ N terminal |
| line-7 | 14.27 | 6 | 200 | 27.1 | 19 + 3 | 4,181 | S terminal ↔ W terminal |
| line-8 | 4.80 | 2 | 200 | 7.1 | 7 + 2 | 4,181 | NE terminal ↔ E terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 33.18 | False | Unestablished |
| 800.00 | 13.33 | 132.70 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 468,939 kWh mechanical | 171.16 GWh mechanical |
| Nominal auxiliary load | 710,640 kWh | 259.38 GWh |
| Auxiliary supply including scenario charging losses | 748,042 kWh | 273.04 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.65 GWh |
| Total priced grid-supply scenario | See annual budget | 492.98 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $31.62m | $81.62m | $244.63m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 22.97 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 20.01 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 29.99 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 63.85 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 5.60 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,822.3 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,088.0 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,567.4 m | 5,554.5 m |
| line-5 | 4 | Coast stops before receiving zone | 6,221.3 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 5,602.9 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 9.95 km |
| Bridge route | 24.90 km |
| Elevated route | 154.60 km |
| Tunnel route | 0.00 km |
| Precast span stock | 18,222 spans |
| Independent supports | 18,952 |
| Running rail | 757.79 rail-km / 45,626 t |
| Complete fastening sets | 1,326,131 |
| Protected at-grade crossing packages | 45 |
| Bridge runs / tunnel portals | 160 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 126.4 m; actual accessible paths require survey |
| Pooled depot area | 153,296 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $888,450 | $3.64m | $21.10m |
| Civil production campaign | $5.45m | $26.32m | $155.98m |

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
| low | make | 8 | 63,777 | 473,772 | 631,696 |
| base | make | 18 | 154,887 | 1,239,096 | 1,652,128 |
| high | make | 47 | 419,106 | 3,425,736 | 4,567,648 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 44 | Unestablished | 317,988 | 159.0 |
| Vehicle production / low | 31 | 62 | Unestablished | Unestablished |
| Civil field / low | 67 | 134 | 688,075 | Unestablished |
| Civil other installation / low | 565 | 1,130 | 5,874,300 | Unestablished |
| Civil precast / low | 64 | 128 | 631,696 | Unestablished |
| Control room and access-site coverage / base | 88 | Unestablished | 722,700 | 361.4 |
| Vehicle production / base | 88 | 176 | Unestablished | Unestablished |
| Civil field / base | 246 | 492 | 2,161,408 | Unestablished |
| Civil other installation / base | 4,538 | 9,076 | 39,929,921 | Unestablished |
| Civil precast / base | 144 | 288 | 1,652,128 | Unestablished |
| Control room and access-site coverage / high | 176 | Unestablished | 1,734,480 | 867.2 |
| Vehicle production / high | 242 | 484 | Unestablished | Unestablished |
| Civil field / high | 1,070 | 2,140 | 5,990,517 | Unestablished |
| Civil other installation / high | 48,863 | 97,726 | 273,627,564 | Unestablished |
| Civil precast / high | 376 | 752 | 4,567,648 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 84 | 344.9 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $990.63m | $3.853bn | $25.002bn |
| Installed capital / route-km | $5.23m | $20.34m | $131.97m |
| 30-year whole-life NPV | $1.884bn | $6.958bn | $42.143bn |
| Annual operating provision | $42.33m | $139.19m | $710.03m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $676.17m | $676.17m |
| Guideway | $271.78m | $271.78m |
| Stations power | $435.14m | $435.14m |
| Factory tooling | $29.96m | $29.96m |
| Construction | $2.175bn | $2.175bn |
| Land utilities depot | $180.91m | $180.91m |
| Fleet | $62.42m | $62.42m |
| Energy | $0 | $1.411bn |
| Operations | $0 | $97.76m |
| Maintenance | $0 | $811.34m |
| Renewals | $0 | $662.70m |
| Recovery | $21.52m | $43.85m |
| Reliability | $0 | $64.14m |
| Disposal | $0 | $35.64m |

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
| Bridge special foundations deck temporary | $779.74m | 20.2% |
| City project risk contingency | $770.54m | 20.0% |
| Network delivered assembled fleet | $536.03m | 13.9% |
| Design prototypes independent review | $227.91m | 5.9% |
| Repeat box beams | $134.09m | 3.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $990.63m | $3.853bn | $25.002bn |
| Water-evidence alternative capital | $815.39m | $2.837bn | $16.752bn |
| Alternative capital / route-km | $4.30m | $14.97m | $88.43m |
| Alternative whole-life NPV | $1.708bn | $5.931bn | $33.680bn |
| Included non-water obstruction reserve | $1.84m | $12.28m | $85.95m |

24.56 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 0 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 86.23m | 0.25 | $21.56m | $-117.64m | $-6.585bn | -0.47 |
| 50% | 86.23m | 0.50 | $43.12m | $-96.08m | $-6.212bn | -0.39 |
| 50% | 86.23m | 1.00 | $86.23m | $-52.96m | $-5.467bn | -0.21 |
| 75% | 129.35m | 0.25 | $32.34m | $-106.86m | $-6.399bn | -0.43 |
| 75% | 129.35m | 0.50 | $64.67m | $-74.52m | $-5.840bn | -0.30 |
| 75% | 129.35m | 1.00 | $129.35m | $-9.85m | $-4.721bn | -0.04 |
| 100% | 172.46m | 0.25 | $43.12m | $-96.08m | $-6.212bn | -0.39 |
| 100% | 172.46m | 0.50 | $86.23m | $-52.96m | $-5.467bn | -0.21 |
| 100% | 172.46m | 1.00 | $172.46m | $33.27m | $-3.976bn | 0.13 |

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
| low | $693.44m | $297.19m | $64.12m |
| base | $2.697bn | $1.156bn | $249.36m |
| high | $17.501bn | $7.501bn | $1.618bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/maiduguri.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-africa/Nigeria/Maiduguri) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `31a715e29621fc57d2311a94c59cb104fb83ef46e19efb5a2696fe2cc7c7dcd8` |
| cost_evaluation_id | `54fea81729fe489b60c90c1e49a21626e49bce38c2a18191867d174658c973b5` |
| outline_evaluation_id | `f67c829709a51c111f31e13887d0b5e47f3fcef3eda1abfcd1e8e3653f82432b` |
| research_configuration_id | `b5320ce9a7bd657444071b5493ff04bcff8e481ad5e25b9786122dbd3c9fa652` |
| seed_id | `cab9de0114a9da88baf13efea7e76428dc97359249a170ec3518d872c5ed2ada` |
| selected_alignment_id | `13127163df71b207190007760cb623e1fe7dde74769be05d3e83160cc124f91d` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `4bba94508606c4163304d302b3233c9a66fc8cc3c4ee97ca8ff9b39b9fe5d7f9` |
| source_result_sha256 | `edd70a5860c6298792ea1588797160da08b0dcdf1e5c3637f314ce39eb52c0e3` |

Atlas packet `9221b7e02b643ef41066ffc001e482395e0991676efe1ae7b30c86b3ff38401f`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
