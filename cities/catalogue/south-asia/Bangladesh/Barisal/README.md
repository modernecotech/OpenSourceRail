# Barisal — railway design and city programme

**BD · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=barisal) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=barisal) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Barisal current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 550,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 75.45 km / 2 trackways |
| Lines / operational platform groups | 5 / 31 |
| Original access markers / separately costed access sites | 33 / 21 |
| Explicit interchange references | 6 |
| Fleet including reserve | 87 six-car trainsets |
| Train distance | 48,889 train-km/day; 17,844,341 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 13.73 | 5 | 200 | 18.5 | 13 + 2 | 4,181 | N terminal ↔ S terminal |
| line-2 | 21.40 | 10 | 200 | 31.8 | 21 + 4 | 4,181 | E terminal ↔ S terminal |
| line-3 | 28.09 | 10 | 200 | 39.1 | 26 + 4 | 4,181 | NW terminal ↔ SE terminal |
| line-4 | 6.37 | 4 | 200 | 10.1 | 8 + 2 | 4,181 | S terminal ↔ SE terminal |
| line-5 | 5.85 | 2 | 200 | 5.9 | 6 + 1 | 4,181 | NW terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 15.58 | False | Unestablished |
| 800.00 | 13.33 | 62.33 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 208,276 kWh mechanical | 76.02 GWh mechanical |
| Nominal auxiliary load | 279,720 kWh | 102.10 GWh |
| Auxiliary supply including scenario charging losses | 294,442 kWh | 107.47 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 1.89 GWh |
| Total priced grid-supply scenario | See annual budget | 205.97 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $13.11m | $34.10m | $103.73m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 13.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 21.40 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 28.09 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 5.85 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,735.5 m | 5,554.5 m |
| line-2 | 2 | Coast stops before receiving zone | 6,225.4 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,421.3 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 5,854.6 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 12.86 km |
| Bridge route | 13.56 km |
| Elevated route | 49.02 km |
| Tunnel route | 0.00 km |
| Precast span stock | 6,476 spans |
| Independent supports | 7,124 |
| Running rail | 301.78 rail-km / 18,170 t |
| Complete fastening sets | 528,118 |
| Protected at-grade crossing packages | 52 |
| Bridge runs / tunnel portals | 137 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 168.3 m; actual accessible paths require survey |
| Pooled depot area | 60,996 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $636,311 | $2.12m | $9.61m |
| Civil production campaign | $2.34m | $10.65m | $61.22m |

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
| low | make | 3 | 22,673 | 168,428 | 224,571 |
| base | make | 7 | 55,063 | 440,504 | 587,339 |
| high | make | 17 | 148,994 | 1,217,864 | 1,623,819 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 23 | Unestablished | 166,221 | 83.1 |
| Vehicle production / low | 13 | 26 | Unestablished | Unestablished |
| Civil field / low | 24 | 48 | 248,683 | Unestablished |
| Civil other installation / low | 283 | 566 | 2,933,926 | Unestablished |
| Civil precast / low | 24 | 48 | 224,571 | Unestablished |
| Control room and access-site coverage / base | 46 | Unestablished | 377,775 | 188.9 |
| Vehicle production / base | 35 | 70 | Unestablished | Unestablished |
| Civil field / base | 89 | 178 | 780,587 | Unestablished |
| Civil other installation / base | 2,393 | 4,786 | 21,051,665 | Unestablished |
| Civil precast / base | 56 | 112 | 587,339 | Unestablished |
| Control room and access-site coverage / high | 92 | Unestablished | 906,660 | 453.3 |
| Vehicle production / high | 96 | 192 | Unestablished | Unestablished |
| Civil field / high | 387 | 774 | 2,162,155 | Unestablished |
| Civil other installation / high | 26,541 | 53,082 | 148,628,318 | Unestablished |
| Civil precast / high | 136 | 272 | 1,623,819 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 42 | 172.5 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $444.24m | $1.808bn | $12.112bn |
| Installed capital / route-km | $5.89m | $23.96m | $160.53m |
| 30-year whole-life NPV | $817.92m | $3.113bn | $19.483bn |
| Annual operating provision | $17.68m | $58.50m | $301.75m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $282.13m | $282.13m |
| Guideway | $100.16m | $100.16m |
| Stations power | $187.86m | $187.86m |
| Factory tooling | $12.77m | $12.77m |
| Construction | $1.114bn | $1.114bn |
| Land utilities depot | $75.50m | $75.50m |
| Fleet | $25.57m | $25.57m |
| Energy | $0 | $589.66m |
| Operations | $0 | $51.10m |
| Maintenance | $0 | $334.94m |
| Renewals | $0 | $277.02m |
| Recovery | $9.93m | $20.24m |
| Reliability | $0 | $25.54m |
| Disposal | $0 | $16.72m |

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
| Bridge special foundations deck temporary | $504.14m | 27.9% |
| City project risk contingency | $361.59m | 20.0% |
| Network delivered assembled fleet | $211.97m | 11.7% |
| Design prototypes independent review | $106.96m | 5.9% |
| Shared access and transfer complexes | $63.02m | 3.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $444.24m | $1.808bn | $12.112bn |
| Water-evidence alternative capital | $386.98m | $1.476bn | $9.411bn |
| Alternative capital / route-km | $5.13m | $19.56m | $124.75m |
| Alternative whole-life NPV | $760.47m | $2.778bn | $16.716bn |
| Included non-water obstruction reserve | $731,662 | $4.88m | $34.14m |

9.76 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 4 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 53.89m | 0.25 | $13.47m | $-45.02m | $-2.880bn | -0.38 |
| 50% | 53.89m | 0.50 | $26.95m | $-31.55m | $-2.647bn | -0.27 |
| 50% | 53.89m | 1.00 | $53.89m | $-4.60m | $-2.181bn | -0.04 |
| 75% | 80.84m | 0.25 | $20.21m | $-38.29m | $-2.764bn | -0.33 |
| 75% | 80.84m | 0.50 | $40.42m | $-18.08m | $-2.414bn | -0.15 |
| 75% | 80.84m | 1.00 | $80.84m | $22.34m | $-1.715bn | 0.19 |
| 100% | 107.79m | 0.25 | $26.95m | $-31.55m | $-2.647bn | -0.27 |
| 100% | 107.79m | 0.50 | $53.89m | $-4.60m | $-2.181bn | -0.04 |
| 100% | 107.79m | 1.00 | $107.79m | $49.29m | $-1.249bn | 0.42 |

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
| low | $310.97m | $133.27m | $28.75m |
| base | $1.266bn | $542.39m | $117.02m |
| high | $8.478bn | $3.633bn | $783.90m |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/barisal.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/Bangladesh/Barisal) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `4f6a97f3ee890e7f1eb58f142b4d6c0191afeb7caacb49ef5494b808468e83ed` |
| cost_evaluation_id | `472a6ed12e268c19f15d7b444c5e0bdf66ee9ca003a950844be46822407562fe` |
| outline_evaluation_id | `7df7221500232706478a8061d4feed7d5b1dca42d82ec184e18fad9ee3adb403` |
| research_configuration_id | `69b17924c2999152258f992bb6e3af587f935a8f8217f883870156ce1c66342c` |
| seed_id | `28dce16d7a360942e4578c4745057f8000185f775cd22a80ee78a14b48a6b6f1` |
| selected_alignment_id | `6707e32e000c40b2d7dfe79c70d91d2a79f7ef1a2d08fa54c8cfe367170c22f6` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `a93e0cd85a7eedf6f255d45aa82cb2a5d2f73dd638636502a78c31f3399c7228` |
| source_result_sha256 | `8794c5d9c5ec68bb83805c1e4879ca967a6b3f21b1c58ccd48e911f43a3a2d04` |

Atlas packet `58baca5182287ce3d4e8709ded9081e2a271bb9dcd0e23342242ea5263ea2e1c`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
