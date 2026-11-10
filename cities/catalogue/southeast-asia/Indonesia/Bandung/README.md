# Bandung — railway design and city programme

**ID · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=bandung) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=bandung) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Bandung current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,615,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 250.08 km / 2 trackways |
| Lines / operational platform groups | 6 / 139 |
| Original access markers / separately costed access sites | 189 / 59 |
| Explicit interchange references | 23 |
| Fleet including reserve | 325 six-car trainsets |
| Train distance | 162,053 train-km/day; 59,149,286 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 40.67 | 15 | 200 | 58.2 | 37 + 6 | 4,181 | E terminal ↔ W terminal |
| line-2 | 47.55 | 27 | 200 | 79.1 | 50 + 8 | 4,181 | SE terminal ↔ NW terminal |
| line-3 | 23.86 | 25 | 200 | 56.0 | 36 + 6 | 4,181 | S terminal ↔ NE terminal |
| line-4 | 34.26 | 23 | 200 | 77.1 | 49 + 8 | 4,181 | S terminal ↔ NE terminal |
| line-5 | 32.05 | 18 | 200 | 63.0 | 40 + 6 | 4,181 | SE terminal ↔ N terminal |
| line-6 | 71.69 | 31 | 200 | 112.2 | 68 + 11 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 69.87 | False | Unestablished |
| 800.00 | 13.33 | 279.48 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 643,700 kWh mechanical | 234.95 GWh mechanical |
| Nominal auxiliary load | 1,058,400 kWh | 386.32 GWh |
| Auxiliary supply including scenario charging losses | 1,114,105 kWh | 406.65 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 6.54 GWh |
| Total priced grid-supply scenario | See annual budget | 710.22 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $45.76m | $117.59m | $349.11m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 40.67 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 47.55 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 71.69 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,092.6 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,297.8 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,654.8 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 16.03 km |
| Bridge route | 9.06 km |
| Elevated route | 224.99 km |
| Tunnel route | 0.00 km |
| Precast span stock | 24,172 spans |
| Independent supports | 25,114 |
| Running rail | 1,020.57 rail-km / 61,448 t |
| Complete fastening sets | 1,785,991 |
| Protected at-grade crossing packages | 205 |
| Bridge runs / tunnel portals | 132 / 0 |
| Additional station track | 10,120 m |
| Access connector allowance | 3,597.8 m; actual accessible paths require survey |
| Pooled depot area | 227,084 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.14m | $4.97m | $30.80m |
| Civil production campaign | $7.01m | $34.22m | $204.09m |

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
| low | make | 10 | 84,602 | 628,472 | 837,963 |
| base | make | 23 | 205,462 | 1,643,696 | 2,191,595 |
| high | make | 62 | 555,956 | 4,544,336 | 6,059,115 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 61 | Unestablished | 440,847 | 220.4 |
| Vehicle production / low | 46 | 92 | Unestablished | Unestablished |
| Civil field / low | 88 | 176 | 912,469 | Unestablished |
| Civil other installation / low | 869 | 1,738 | 9,036,104 | Unestablished |
| Civil precast / low | 80 | 160 | 837,963 | Unestablished |
| Control room and access-site coverage / base | 122 | Unestablished | 1,001,925 | 501.0 |
| Vehicle production / base | 130 | 260 | Unestablished | Unestablished |
| Civil field / base | 326 | 652 | 2,866,325 | Unestablished |
| Civil other installation / base | 5,590 | 11,180 | 49,186,938 | Unestablished |
| Civil precast / base | 184 | 368 | 2,191,595 | Unestablished |
| Control room and access-site coverage / high | 244 | Unestablished | 2,404,620 | 1,202.3 |
| Vehicle production / high | 357 | 714 | Unestablished | Unestablished |
| Civil field / high | 1,419 | 2,838 | 7,944,341 | Unestablished |
| Civil other installation / high | 51,017 | 102,034 | 285,693,618 | Unestablished |
| Civil precast / high | 496 | 992 | 6,059,115 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 118 | 484.5 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.426bn | $5.011bn | $29.293bn |
| Installed capital / route-km | $5.70m | $20.04m | $117.14m |
| 30-year whole-life NPV | $2.795bn | $9.802bn | $55.349bn |
| Annual operating provision | $63.17m | $209.97m | $1.071bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $957.79m | $957.79m |
| Guideway | $362.21m | $362.21m |
| Stations power | $1.032bn | $1.032bn |
| Factory tooling | $39.19m | $39.19m |
| Construction | $2.255bn | $2.255bn |
| Land utilities depot | $246.95m | $246.95m |
| Fleet | $89.75m | $89.75m |
| Energy | $0 | $2.033bn |
| Operations | $0 | $135.53m |
| Maintenance | $0 | $1.348bn |
| Renewals | $0 | $1.115bn |
| Recovery | $28.15m | $57.35m |
| Reliability | $0 | $84.67m |
| Disposal | $0 | $46.35m |

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
| City project risk contingency | $1.002bn | 20.0% |
| Network delivered assembled fleet | $791.86m | 15.8% |
| Bridge special foundations deck temporary | $388.39m | 7.8% |
| Design prototypes independent review | $295.97m | 5.9% |
| Shared access and transfer complexes | $183.20m | 3.7% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.426bn | $5.011bn | $29.293bn |
| Water-evidence alternative capital | $1.399bn | $4.851bn | $27.993bn |
| Alternative capital / route-km | $5.59m | $19.40m | $111.94m |
| Alternative whole-life NPV | $2.768bn | $9.642bn | $54.022bn |
| Included non-water obstruction reserve | $497,934 | $3.32m | $23.24m |

6.64 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 14 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 64.67m | 0.25 | $16.17m | $-193.80m | $-9.523bn | -0.60 |
| 50% | 64.67m | 0.50 | $32.34m | $-177.63m | $-9.243bn | -0.55 |
| 50% | 64.67m | 1.00 | $64.67m | $-145.29m | $-8.684bn | -0.45 |
| 75% | 97.01m | 0.25 | $24.25m | $-185.71m | $-9.383bn | -0.57 |
| 75% | 97.01m | 0.50 | $48.51m | $-161.46m | $-8.964bn | -0.50 |
| 75% | 97.01m | 1.00 | $97.01m | $-112.96m | $-8.125bn | -0.35 |
| 100% | 129.35m | 0.25 | $32.34m | $-177.63m | $-9.243bn | -0.55 |
| 100% | 129.35m | 0.50 | $64.67m | $-145.29m | $-8.684bn | -0.45 |
| 100% | 129.35m | 1.00 | $129.35m | $-80.62m | $-7.566bn | -0.25 |

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
| low | $998.13m | $427.77m | $92.29m |
| base | $3.507bn | $1.503bn | $324.31m |
| high | $20.505bn | $8.788bn | $1.896bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/bandung.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/southeast-asia/Indonesia/Bandung) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `f490cc2496a1f1cbe41acd34646bbc63c48ccbd763ae476221d8aa431e5e52a2` |
| cost_evaluation_id | `d9bc467eaadfedba79e75bdec433e5419d109c00f6fba099a9298cd1c496ccef` |
| outline_evaluation_id | `4dd920c2419a4e5aedf59fa51f14116eb81da8b5e6bf91bcabf8b72a9ef319b1` |
| research_configuration_id | `5a90f259373fa5ad1223100b4ce88b8891e7588ec3c7a21db1496264247d24cc` |
| seed_id | `48b39e7afde84cce080e5076e9a22bcf37cfb777127174dde6d4f6d7b2bdf402` |
| selected_alignment_id | `b39b5ef38dd17aec3a58da610214612e86c4ee58e64b2f7cb330fa1753e744aa` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `ec435b0af261b907c64c67e7e8d181dd204f663b9c8628b7ca9958a205fbeec3` |
| source_result_sha256 | `7ea123defefc59655ff99bb2e7c661f2d18e0584181001edb2a3c0de90bd8aaa` |

Atlas packet `29f65d37ca9a96492f45e6ea982c7c530ae05148fdccc044407845032e9edb93`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
