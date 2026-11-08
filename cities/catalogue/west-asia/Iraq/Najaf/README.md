# Najaf — railway design and city programme

**IQ · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=najaf) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=najaf) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Najaf current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,540,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 189.69 km / 2 trackways |
| Lines / operational platform groups | 9 / 73 |
| Original access markers / separately costed access sites | 84 / 41 |
| Explicit interchange references | 22 |
| Fleet including reserve | 244 six-car trainsets |
| Train distance | 122,921 train-km/day; 44,866,014 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 17.93 | 8 | 200 | 32.2 | 22 + 4 | 4,181 | S terminal ↔ NE terminal |
| line-2 | 37.01 | 14 | 200 | 52.8 | 34 + 6 | 4,181 | SE terminal ↔ N terminal |
| line-3 | 17.40 | 9 | 200 | 30.9 | 21 + 4 | 4,181 | N terminal ↔ SE terminal |
| line-4 | 27.59 | 9 | 200 | 50.3 | 32 + 5 | 4,181 | E terminal ↔ NW terminal |
| line-5 | 26.97 | 9 | 200 | 37.1 | 25 + 4 | 4,181 | SW terminal ↔ E terminal |
| line-6 | 31.54 | 13 | 200 | 48.6 | 30 + 5 | 4,181 | Ring / closed circuit |
| line-7 | 5.09 | 3 | 200 | 7.7 | 7 + 2 | 4,181 | E terminal ↔ SW terminal |
| line-8 | 14.04 | 4 | 200 | 27.4 | 19 + 3 | 4,181 | SW terminal ↔ W terminal |
| line-9 | 12.13 | 4 | 200 | 26.0 | 18 + 3 | 4,181 | NE terminal ↔ NW terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 36.69 | False | Unestablished |
| 800.00 | 13.33 | 146.78 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 432,501 kWh mechanical | 157.86 GWh mechanical |
| Nominal auxiliary load | 786,240 kWh | 286.98 GWh |
| Auxiliary supply including scenario charging losses | 827,621 kWh | 302.08 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.23 GWh |
| Total priced grid-supply scenario | See annual budget | 508.47 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $32.85m | $84.18m | $248.39m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Station launch reference | 0 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Station launch reference | 0 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Station launch reference | 0 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-2 | 4 / 749.2 kW | 37.01 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 26.97 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 31.54 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-2 | 1 | Coast stops before receiving zone | 6,795.2 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,424.2 m | 5,554.5 m |
| line-6 | 3 | Coast stops before receiving zone | 6,093.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 30.32 km |
| Bridge route | 12.08 km |
| Elevated route | 147.29 km |
| Tunnel route | 0.00 km |
| Precast span stock | 16,360 spans |
| Independent supports | 16,786 |
| Running rail | 770.21 rail-km / 46,374 t |
| Complete fastening sets | 1,347,866 |
| Protected at-grade crossing packages | 128 |
| Bridge runs / tunnel portals | 47 / 0 |
| Additional station track | 5,720 m |
| Access connector allowance | 818.7 m; actual accessible paths require survey |
| Pooled depot area | 170,768 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $956,219 | $4.00m | $24.92m |
| Civil production campaign | $4.97m | $23.86m | $140.85m |

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
| low | make | 7 | 57,260 | 425,360 | 567,147 |
| base | make | 16 | 139,060 | 1,112,480 | 1,483,307 |
| high | make | 42 | 376,280 | 3,075,680 | 4,100,907 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 43 | Unestablished | 310,761 | 155.4 |
| Vehicle production / low | 35 | 70 | Unestablished | Unestablished |
| Civil field / low | 60 | 120 | 615,317 | Unestablished |
| Civil other installation / low | 553 | 1,106 | 5,748,024 | Unestablished |
| Civil precast / low | 56 | 112 | 567,147 | Unestablished |
| Control room and access-site coverage / base | 86 | Unestablished | 706,275 | 353.1 |
| Vehicle production / base | 98 | 196 | Unestablished | Unestablished |
| Civil field / base | 220 | 440 | 1,933,205 | Unestablished |
| Civil other installation / base | 3,811 | 7,622 | 33,534,564 | Unestablished |
| Civil precast / base | 128 | 256 | 1,483,307 | Unestablished |
| Control room and access-site coverage / high | 172 | Unestablished | 1,695,060 | 847.5 |
| Vehicle production / high | 268 | 536 | Unestablished | Unestablished |
| Civil field / high | 957 | 1,914 | 5,358,805 | Unestablished |
| Civil other installation / high | 37,137 | 74,274 | 207,965,349 | Unestablished |
| Civil precast / high | 336 | 672 | 4,100,907 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 82 | 336.7 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $956.31m | $3.484bn | $21.061bn |
| Installed capital / route-km | $5.04m | $18.37m | $111.03m |
| 30-year whole-life NPV | $1.905bn | $6.800bn | $39.249bn |
| Annual operating provision | $44.35m | $146.48m | $747.49m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $691.27m | $691.27m |
| Guideway | $253.90m | $253.90m |
| Stations power | $589.79m | $589.79m |
| Factory tooling | $27.86m | $27.86m |
| Construction | $1.643bn | $1.643bn |
| Land utilities depot | $190.41m | $190.41m |
| Fleet | $65.71m | $65.71m |
| Energy | $0 | $1.456bn |
| Operations | $0 | $95.54m |
| Maintenance | $0 | $895.05m |
| Renewals | $0 | $751.49m |
| Recovery | $21.52m | $43.85m |
| Reliability | $0 | $64.22m |
| Disposal | $0 | $32.22m |

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
| City project risk contingency | $696.76m | 20.0% |
| Network delivered assembled fleet | $594.50m | 17.1% |
| Bridge special foundations deck temporary | $331.92m | 9.5% |
| Design prototypes independent review | $205.90m | 5.9% |
| Shared access and transfer complexes | $133.32m | 3.8% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $956.31m | $3.484bn | $21.061bn |
| Water-evidence alternative capital | $919.48m | $3.269bn | $19.313bn |
| Alternative capital / route-km | $4.85m | $17.23m | $101.81m |
| Alternative whole-life NPV | $1.868bn | $6.584bn | $37.463bn |
| Included non-water obstruction reserve | $649,974 | $4.33m | $30.33m |

8.67 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 7 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-122.22m | $-6.381bn | -0.54 |
| 50% | 97.01m | 0.50 | $48.51m | $-97.97m | $-5.962bn | -0.43 |
| 50% | 97.01m | 1.00 | $97.01m | $-49.46m | $-5.123bn | -0.22 |
| 75% | 145.52m | 0.25 | $36.38m | $-110.10m | $-6.171bn | -0.49 |
| 75% | 145.52m | 0.50 | $72.76m | $-73.72m | $-5.542bn | -0.33 |
| 75% | 145.52m | 1.00 | $145.52m | $-959,296 | $-4.284bn | -0.00 |
| 100% | 194.02m | 0.25 | $48.51m | $-97.97m | $-5.962bn | -0.43 |
| 100% | 194.02m | 0.50 | $97.01m | $-49.46m | $-5.123bn | -0.22 |
| 100% | 194.02m | 1.00 | $194.02m | $47.55m | $-3.445bn | 0.21 |

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
| low | $669.42m | $286.89m | $61.90m |
| base | $2.439bn | $1.045bn | $225.48m |
| high | $14.743bn | $6.318bn | $1.363bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/najaf.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Najaf) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `3078dff30266d0faf12b157d7c39db61060bfb6ab94cb97d9a0b8ec9f53bb26c` |
| cost_evaluation_id | `fa32b3d5b852f9353ea20fa2326d67805ffb2aa45446ab8e03b9c5ff525cf7c7` |
| outline_evaluation_id | `606d7d4a46a84dd38ab0d6e84fbae2b8be6bfa9023d060a74525098d409abaad` |
| research_configuration_id | `4e00645743b6dbbe4e499423af4041b678b557815f8e74cb9cc036b79bd6d9d6` |
| seed_id | `aa9d4bbbf32b18923b0f456fbe4030920090afb61fb6ea8ab535edb297c12cd3` |
| selected_alignment_id | `ea2bd1d75443afda819930943db20d28b629bced7235c9facf4a9e429a87dbfb` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `0400f78e7d7fa7fb22efa9b41997427d011e500074ea2f614600bacc170cef07` |
| source_result_sha256 | `61e873f20897e18bdf06d2d7e9d0d355ed97299e59eb234b08af65c4a9c6a8cf` |

Atlas packet `e75718468239452943d2cd9802e74f6f77877fee43701d68346e3ba48aa79d8a`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
