# Visakhapatnam — railway design and city programme

**IN · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=visakhapatnam) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=visakhapatnam) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Visakhapatnam current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 2,300,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 244.98 km / 2 trackways |
| Lines / operational platform groups | 6 / 74 |
| Original access markers / separately costed access sites | 82 / 47 |
| Explicit interchange references | 19 |
| Fleet including reserve | 253 six-car trainsets |
| Train distance | 158,750 train-km/day; 57,943,725 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 43.72 | 12 | 200 | 57.6 | 37 + 6 | 4,181 | E terminal ↔ SW terminal |
| line-2 | 49.15 | 13 | 200 | 64.9 | 41 + 7 | 4,181 | S terminal ↔ NE terminal |
| line-3 | 32.46 | 12 | 200 | 47.0 | 30 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-4 | 27.11 | 11 | 200 | 45.0 | 29 + 5 | 4,181 | W terminal ↔ NE terminal |
| line-5 | 22.19 | 9 | 200 | 32.6 | 22 + 4 | 4,181 | N terminal ↔ S terminal |
| line-6 | 70.36 | 17 | 200 | 95.0 | 58 + 9 | 4,181 | Ring / closed circuit |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 37.20 | False | Unestablished |
| 800.00 | 13.33 | 148.79 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 609,860 kWh mechanical | 222.60 GWh mechanical |
| Nominal auxiliary load | 820,260 kWh | 299.39 GWh |
| Auxiliary supply including scenario charging losses | 863,432 kWh | 315.15 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.23 GWh |
| Total priced grid-supply scenario | See annual budget | 596.89 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $38.19m | $98.82m | $297.96m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 43.72 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 49.15 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 32.46 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 22.19 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 70.36 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,834.3 m | 5,554.5 m |
| line-2 | 3 | Coast stops before receiving zone | 5,849.0 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,578.0 m | 5,554.5 m |
| line-5 | 2 | Coast stops before receiving zone | 6,912.1 m | 5,554.5 m |
| line-6 | 4 | Coast stops before receiving zone | 6,611.1 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 27.62 km |
| Bridge route | 14.10 km |
| Elevated route | 203.27 km |
| Tunnel route | 0.00 km |
| Precast span stock | 22,066 spans |
| Independent supports | 22,890 |
| Running rail | 979.94 rail-km / 59,002 t |
| Complete fastening sets | 1,714,892 |
| Protected at-grade crossing packages | 232 |
| Bridge runs / tunnel portals | 93 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 510.4 m; actual accessible paths require survey |
| Pooled depot area | 177,164 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $25.93m |
| Civil production campaign | $6.46m | $31.48m | $187.36m |

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
| low | make | 9 | 77,231 | 573,716 | 764,955 |
| base | make | 21 | 187,561 | 1,500,488 | 2,000,651 |
| high | make | 57 | 507,518 | 4,148,408 | 5,531,211 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 49 | Unestablished | 354,123 | 177.1 |
| Vehicle production / low | 36 | 72 | Unestablished | Unestablished |
| Civil field / low | 81 | 162 | 832,587 | Unestablished |
| Civil other installation / low | 528 | 1,056 | 5,487,381 | Unestablished |
| Civil precast / low | 72 | 144 | 764,955 | Unestablished |
| Control room and access-site coverage / base | 98 | Unestablished | 804,825 | 402.4 |
| Vehicle production / base | 102 | 204 | Unestablished | Unestablished |
| Civil field / base | 298 | 596 | 2,615,445 | Unestablished |
| Civil other installation / base | 4,081 | 8,162 | 35,909,256 | Unestablished |
| Civil precast / base | 168 | 336 | 2,000,651 | Unestablished |
| Control room and access-site coverage / high | 196 | Unestablished | 1,931,580 | 965.8 |
| Vehicle production / high | 278 | 556 | Unestablished | Unestablished |
| Civil field / high | 1,295 | 2,590 | 7,249,120 | Unestablished |
| Civil other installation / high | 42,895 | 85,790 | 240,210,356 | Unestablished |
| Civil precast / high | 456 | 912 | 5,531,211 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 94 | 386.0 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.093bn | $4.014bn | $24.982bn |
| Installed capital / route-km | $4.46m | $16.38m | $101.97m |
| 30-year whole-life NPV | $2.163bn | $7.712bn | $45.054bn |
| Annual operating provision | $51.01m | $167.19m | $845.84m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $816.05m | $816.05m |
| Guideway | $335.97m | $335.97m |
| Stations power | $480.76m | $480.76m |
| Factory tooling | $35.69m | $35.69m |
| Construction | $2.023bn | $2.023bn |
| Land utilities depot | $220.19m | $220.19m |
| Fleet | $74.10m | $74.10m |
| Energy | $0 | $1.709bn |
| Operations | $0 | $108.87m |
| Maintenance | $0 | $961.25m |
| Renewals | $0 | $770.25m |
| Recovery | $28.15m | $57.35m |
| Reliability | $0 | $82.94m |
| Disposal | $0 | $37.13m |

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
| City project risk contingency | $802.76m | 20.0% |
| Network delivered assembled fleet | $616.43m | 15.4% |
| Bridge special foundations deck temporary | $444.95m | 11.1% |
| Design prototypes independent review | $237.41m | 5.9% |
| Repeat box beams | $162.38m | 4.0% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.093bn | $4.014bn | $24.982bn |
| Water-evidence alternative capital | $1.048bn | $3.750bn | $22.838bn |
| Alternative capital / route-km | $4.28m | $15.31m | $93.22m |
| Alternative whole-life NPV | $2.118bn | $7.446bn | $42.860bn |
| Included non-water obstruction reserve | $738,450 | $4.92m | $34.46m |

9.85 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 4 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 64.67m | 0.25 | $16.17m | $-151.02m | $-7.433bn | -0.58 |
| 50% | 64.67m | 0.50 | $32.34m | $-134.86m | $-7.153bn | -0.52 |
| 50% | 64.67m | 1.00 | $64.67m | $-102.52m | $-6.594bn | -0.39 |
| 75% | 97.01m | 0.25 | $24.25m | $-142.94m | $-7.293bn | -0.55 |
| 75% | 97.01m | 0.50 | $48.51m | $-118.69m | $-6.873bn | -0.46 |
| 75% | 97.01m | 1.00 | $97.01m | $-70.18m | $-6.035bn | -0.27 |
| 100% | 129.35m | 0.25 | $32.34m | $-134.86m | $-7.153bn | -0.52 |
| 100% | 129.35m | 0.50 | $64.67m | $-102.52m | $-6.594bn | -0.39 |
| 100% | 129.35m | 1.00 | $129.35m | $-37.84m | $-5.476bn | -0.15 |

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
| low | $764.97m | $327.85m | $70.73m |
| base | $2.810bn | $1.204bn | $259.79m |
| high | $17.487bn | $7.495bn | $1.617bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/visakhapatnam.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-asia/India/Visakhapatnam) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `36443585f632b439e48d78bda041f0ba7b8dd40a8681aba5a4a6471029225524` |
| cost_evaluation_id | `443fc95aeb6c7be0021dc2500963358e4b463320f18e7f62d8f4d799748165e8` |
| outline_evaluation_id | `b0bd0481a68a7ab5db10808e7943caa66ba22ac6999a9b0993f9a10d95e7fb40` |
| research_configuration_id | `5f714e954106037c67522d44b13a45e495990725ec9807bddf4ea8b0fcab9655` |
| seed_id | `191001d3366484fe1b4063ade9e00e7328834eeed8e5d173e36fdf64b2b09903` |
| selected_alignment_id | `05a1420d3f6cb53e14dc65b068195b132920709985a2a396ec3935b55b9aa05e` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `3467dd4982c2ca8d348c358f3e57031ce0aff6f71bf57617c3311fdec1249cd7` |
| source_result_sha256 | `dd46f193021c96f082a329b1d460ae3e46987a4c02fa45f9f013fde887cb80ef` |

Atlas packet `81000933a2f8ffa923a657cf6f1941664d30584d86f2b3310d412c5d15509fc8`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
