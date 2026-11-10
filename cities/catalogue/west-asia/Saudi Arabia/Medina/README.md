# Medina — railway design and city programme

**SA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=medina) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=medina) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Medina current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,500,000 — retained planning input; not a demand survey |
| Selected alignment | Original |
| Route length / trackways | 202.71 km / 2 trackways |
| Lines / operational platform groups | 9 / 63 |
| Original access markers / separately costed access sites | 63 / 41 |
| Explicit interchange references | 18 |
| Fleet including reserve | 231 six-car trainsets |
| Train distance | 131,357 train-km/day; 47,945,482 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 32.73 | 9 | 200 | 42.8 | 28 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-2 | 19.11 | 7 | 200 | 33.2 | 22 + 4 | 4,181 | SW terminal ↔ NE terminal |
| line-3 | 22.68 | 8 | 200 | 38.5 | 25 + 4 | 4,181 | W terminal ↔ S terminal |
| line-4 | 25.52 | 8 | 200 | 34.2 | 23 + 4 | 4,181 | NE terminal ↔ W terminal |
| line-5 | 19.43 | 7 | 200 | 32.4 | 22 + 4 | 4,181 | NW terminal ↔ E terminal |
| line-6 | 62.18 | 16 | 200 | 84.7 | 52 + 8 | 4,181 | Ring / closed circuit |
| line-7 | 5.74 | 3 | 200 | 7.6 | 7 + 2 | 4,181 | SE terminal ↔ E terminal |
| line-8 | 9.68 | 3 | 200 | 16.0 | 12 + 2 | 4,181 | W terminal ↔ SW terminal |
| line-9 | 5.64 | 2 | 200 | 5.7 | 6 + 1 | 4,181 | E terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 31.67 | False | Unestablished |
| 800.00 | 13.33 | 126.67 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 452,587 kWh mechanical | 165.19 GWh mechanical |
| Nominal auxiliary load | 744,660 kWh | 271.80 GWh |
| Auxiliary supply including scenario charging losses | 783,853 kWh | 286.11 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 4.94 GWh |
| Total priced grid-supply scenario | See annual budget | 499.83 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $32.17m | $82.75m | $246.23m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Station launch reference | 0 kg | 250 kg |
| line-3 | Station launch reference | 0 kg | 250 kg |
| line-4 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 32.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-3 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-4 | 4 / 749.2 kW | 25.52 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 62.18 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 5.74 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 5.64 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 6,201.3 m | 5,554.5 m |
| line-4 | 1 | Coast stops before receiving zone | 6,490.8 m | 5,554.5 m |
| line-6 | 2 | Coast stops before receiving zone | 5,867.8 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 5,572.7 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 5,635.3 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 24.72 km |
| Bridge route | 3.83 km |
| Elevated route | 174.16 km |
| Tunnel route | 0.00 km |
| Precast span stock | 17,932 spans |
| Independent supports | 18,356 |
| Running rail | 810.85 rail-km / 48,821 t |
| Complete fastening sets | 1,418,986 |
| Protected at-grade crossing packages | 125 |
| Bridge runs / tunnel portals | 49 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 0.0 m; actual accessible paths require survey |
| Pooled depot area | 162,084 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $898,384 | $3.86m | $24.10m |
| Civil production campaign | $5.34m | $25.92m | $153.58m |

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
| low | make | 7 | 62,762 | 466,232 | 621,643 |
| base | make | 17 | 152,422 | 1,219,376 | 1,625,835 |
| high | make | 46 | 412,436 | 3,371,216 | 4,494,955 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 43 | Unestablished | 310,761 | 155.4 |
| Vehicle production / low | 33 | 66 | Unestablished | Unestablished |
| Civil field / low | 65 | 130 | 673,984 | Unestablished |
| Civil other installation / low | 395 | 790 | 4,101,682 | Unestablished |
| Civil precast / low | 56 | 112 | 621,643 | Unestablished |
| Control room and access-site coverage / base | 86 | Unestablished | 706,275 | 353.1 |
| Vehicle production / base | 93 | 186 | Unestablished | Unestablished |
| Civil field / base | 241 | 482 | 2,117,589 | Unestablished |
| Civil other installation / base | 2,763 | 5,526 | 24,314,252 | Unestablished |
| Civil precast / base | 136 | 272 | 1,625,835 | Unestablished |
| Control room and access-site coverage / high | 172 | Unestablished | 1,695,060 | 847.5 |
| Vehicle production / high | 254 | 508 | Unestablished | Unestablished |
| Civil field / high | 1,049 | 2,098 | 5,870,059 | Unestablished |
| Civil other installation / high | 27,515 | 55,030 | 154,078,590 | Unestablished |
| Civil precast / high | 368 | 736 | 4,494,955 | Unestablished |

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
| Installed capital | $859.04m | $3.046bn | $18.266bn |
| Installed capital / route-km | $4.24m | $15.03m | $90.11m |
| 30-year whole-life NPV | $1.770bn | $6.217bn | $35.628bn |
| Annual operating provision | $43.13m | $142.02m | $725.41m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $687.96m | $687.96m |
| Guideway | $274.62m | $274.62m |
| Stations power | $456.82m | $456.82m |
| Factory tooling | $29.78m | $29.78m |
| Construction | $1.316bn | $1.316bn |
| Land utilities depot | $193.48m | $193.48m |
| Fleet | $64.22m | $64.22m |
| Energy | $0 | $1.431bn |
| Operations | $0 | $95.54m |
| Maintenance | $0 | $836.70m |
| Renewals | $0 | $686.58m |
| Recovery | $23.18m | $47.23m |
| Reliability | $0 | $68.63m |
| Disposal | $0 | $28.18m |

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
| City project risk contingency | $609.27m | 20.0% |
| Network delivered assembled fleet | $562.83m | 18.5% |
| Design prototypes independent review | $180.10m | 5.9% |
| Bridge special foundations deck temporary | $156.74m | 5.1% |
| Repeat box beams | $131.96m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $859.04m | $3.046bn | $18.266bn |
| Water-evidence alternative capital | $842.76m | $2.951bn | $17.494bn |
| Alternative capital / route-km | $4.16m | $14.56m | $86.30m |
| Alternative whole-life NPV | $1.754bn | $6.121bn | $34.838bn |
| Included non-water obstruction reserve | $234,604 | $1.56m | $10.95m |

3.13 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 2 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-117.77m | $-5.798bn | -0.60 |
| 50% | 97.01m | 0.50 | $48.51m | $-93.52m | $-5.378bn | -0.47 |
| 50% | 97.01m | 1.00 | $97.01m | $-45.01m | $-4.539bn | -0.23 |
| 75% | 145.52m | 0.25 | $36.38m | $-105.64m | $-5.588bn | -0.54 |
| 75% | 145.52m | 0.50 | $72.76m | $-69.27m | $-4.959bn | -0.35 |
| 75% | 145.52m | 1.00 | $145.52m | $3.49m | $-3.701bn | 0.02 |
| 100% | 194.02m | 0.25 | $48.51m | $-93.52m | $-5.378bn | -0.47 |
| 100% | 194.02m | 0.50 | $97.01m | $-45.01m | $-4.539bn | -0.23 |
| 100% | 194.02m | 1.00 | $194.02m | $52.00m | $-2.862bn | 0.26 |

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
| low | $601.33m | $257.71m | $55.60m |
| base | $2.132bn | $913.91m | $197.17m |
| high | $12.786bn | $5.480bn | $1.182bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/medina.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Saudi%20Arabia/Medina) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `e8daffd83a60751c6e91d4a01cdd64c52aafca150c9a7446375e203aae13d266` |
| cost_evaluation_id | `40fb7df8dd67edcbdf507e937946da7b0d08d878501b2edaa1d6b6d33bd0897b` |
| outline_evaluation_id | `d767ea1340e7162cfc0159bdc4db96c0c097f41023d20816d250ede4fb10f140` |
| research_configuration_id | `c7cc6b126952f97fe3f637634c920fb239a478d32fc2f4d14416287821f700f3` |
| seed_id | `362d69d4edcf1abc255fe06b7f7d4ecd1129c9905b27cd76721ab2b644fcc96a` |
| selected_alignment_id | `606ec4d388d6828b5cef6b795c06745799b5aabf91138c64dafb95625b143b5c` |
| selected_alignment_kind | `original` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `7d5ba0d0677eb00ed13676546676f9025d79b9abf69214045594095339ad43a2` |
| source_result_sha256 | `0d2e4d42afcc55cddfcea3e30721eb4f119796b76d638edf412a94a15c0e0a98` |

Atlas packet `697c5b56253a82d8ff36bc18beaa7723669e60fb8535358b6fee9afb303b9a8a`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
