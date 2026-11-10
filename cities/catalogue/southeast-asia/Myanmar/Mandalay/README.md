# Mandalay — railway design and city programme

**MM · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=mandalay) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=mandalay) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Mandalay current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 1,726,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 243.26 km / 2 trackways |
| Lines / operational platform groups | 9 / 80 |
| Original access markers / separately costed access sites | 81 / 53 |
| Explicit interchange references | 22 |
| Fleet including reserve | 269 six-car trainsets |
| Train distance | 157,635 train-km/day; 57,536,612 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 35.88 | 12 | 200 | 50.6 | 33 + 5 | 4,181 | N terminal ↔ S terminal |
| line-2 | 28.92 | 13 | 200 | 44.2 | 29 + 5 | 4,181 | NW terminal ↔ SE terminal |
| line-3 | 28.53 | 9 | 200 | 38.8 | 26 + 4 | 4,181 | SW terminal ↔ NE terminal |
| line-4 | 20.14 | 7 | 200 | 35.4 | 24 + 4 | 4,181 | N terminal ↔ NE terminal |
| line-5 | 21.69 | 8 | 200 | 37.7 | 25 + 4 | 4,181 | E terminal ↔ SW terminal |
| line-6 | 82.73 | 21 | 200 | 112.4 | 68 + 11 | 4,181 | Ring / closed circuit |
| line-7 | 6.18 | 2 | 200 | 6.2 | 6 + 1 | 4,181 | S terminal ↔ SE terminal |
| line-8 | 5.59 | 2 | 200 | 5.7 | 6 + 1 | 4,181 | SW terminal ↔ SW terminal |
| line-9 | 13.60 | 6 | 200 | 20.0 | 14 + 3 | 4,181 | SE terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 40.21 | False | Unestablished |
| 800.00 | 13.33 | 160.85 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 615,650 kWh mechanical | 224.71 GWh mechanical |
| Nominal auxiliary load | 873,180 kWh | 318.71 GWh |
| Auxiliary supply including scenario charging losses | 919,137 kWh | 335.48 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 5.52 GWh |
| Total priced grid-supply scenario | See annual budget | 622.02 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $39.83m | $102.98m | $309.91m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Station launch reference | 0 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 35.88 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 28.92 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 28.53 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-6 | 4 / 749.2 kW | 82.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 6.18 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 4 / 749.2 kW | 5.59 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-9 | 4 / 749.2 kW | 13.60 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 2 | Coast stops before receiving zone | 6,538.8 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,840.2 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 5,889.2 m | 5,554.5 m |
| line-6 | 4 | Coast stops before receiving zone | 6,816.5 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,182.2 m | 5,554.5 m |
| line-8 | 1 | Coast stops before receiving zone | 5,594.0 m | 5,554.5 m |
| line-9 | 1 | Coast stops before receiving zone | 6,502.0 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 41.76 km |
| Bridge route | 26.76 km |
| Elevated route | 174.75 km |
| Tunnel route | 0.00 km |
| Precast span stock | 20,734 spans |
| Independent supports | 21,822 |
| Running rail | 973.05 rail-km / 58,588 t |
| Complete fastening sets | 1,702,843 |
| Protected at-grade crossing packages | 274 |
| Bridge runs / tunnel portals | 149 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 100.0 m; actual accessible paths require survey |
| Pooled depot area | 187,564 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.04m | $4.22m | $27.12m |
| Civil production campaign | $6.12m | $29.71m | $176.23m |

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
| low | make | 9 | 72,569 | 539,084 | 718,779 |
| base | make | 20 | 176,239 | 1,409,912 | 1,879,883 |
| high | make | 53 | 476,882 | 3,897,992 | 5,197,323 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 55 | Unestablished | 397,485 | 198.7 |
| Vehicle production / low | 38 | 76 | Unestablished | Unestablished |
| Civil field / low | 76 | 152 | 785,675 | Unestablished |
| Civil other installation / low | 700 | 1,400 | 7,271,705 | Unestablished |
| Civil precast / low | 72 | 144 | 718,779 | Unestablished |
| Control room and access-site coverage / base | 110 | Unestablished | 903,375 | 451.7 |
| Vehicle production / base | 108 | 216 | Unestablished | Unestablished |
| Civil field / base | 281 | 562 | 2,467,605 | Unestablished |
| Civil other installation / base | 5,644 | 11,288 | 49,658,849 | Unestablished |
| Civil precast / base | 160 | 320 | 1,879,883 | Unestablished |
| Control room and access-site coverage / high | 220 | Unestablished | 2,168,100 | 1,084.0 |
| Vehicle production / high | 296 | 592 | Unestablished | Unestablished |
| Civil field / high | 1,222 | 2,444 | 6,838,304 | Unestablished |
| Civil other installation / high | 60,652 | 121,304 | 339,646,450 | Unestablished |
| Civil precast / high | 424 | 848 | 5,197,323 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 106 | 435.3 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $1.226bn | $4.749bn | $30.601bn |
| Installed capital / route-km | $5.04m | $19.52m | $125.79m |
| 30-year whole-life NPV | $2.343bn | $8.620bn | $51.863bn |
| Annual operating provision | $53.08m | $174.07m | $883.20m |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $849.03m | $849.03m |
| Guideway | $321.44m | $321.44m |
| Stations power | $522.87m | $522.87m |
| Factory tooling | $33.92m | $33.92m |
| Construction | $2.691bn | $2.691bn |
| Land utilities depot | $225.59m | $225.59m |
| Fleet | $77.66m | $77.66m |
| Energy | $0 | $1.781bn |
| Operations | $0 | $122.20m |
| Maintenance | $0 | $995.47m |
| Renewals | $0 | $817.08m |
| Recovery | $28.15m | $57.35m |
| Reliability | $0 | $82.36m |
| Disposal | $0 | $43.93m |

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
| City project risk contingency | $949.88m | 20.0% |
| Bridge special foundations deck temporary | $810.34m | 17.1% |
| Network delivered assembled fleet | $655.41m | 13.8% |
| Design prototypes independent review | $280.96m | 5.9% |
| Shared access and transfer complexes | $165.91m | 3.5% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $1.226bn | $4.749bn | $30.601bn |
| Water-evidence alternative capital | $1.134bn | $4.217bn | $26.270bn |
| Alternative capital / route-km | $4.66m | $17.33m | $107.99m |
| Alternative whole-life NPV | $2.251bn | $8.084bn | $47.431bn |
| Included non-water obstruction reserve | $1.58m | $10.53m | $73.73m |

21.06 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 14 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 97.01m | 0.25 | $24.25m | $-149.82m | $-8.201bn | -0.49 |
| 50% | 97.01m | 0.50 | $48.51m | $-125.56m | $-7.782bn | -0.41 |
| 50% | 97.01m | 1.00 | $97.01m | $-77.06m | $-6.943bn | -0.25 |
| 75% | 145.52m | 0.25 | $36.38m | $-137.69m | $-7.991bn | -0.45 |
| 75% | 145.52m | 0.50 | $72.76m | $-101.31m | $-7.362bn | -0.33 |
| 75% | 145.52m | 1.00 | $145.52m | $-28.55m | $-6.104bn | -0.09 |
| 100% | 194.02m | 0.25 | $48.51m | $-125.56m | $-7.782bn | -0.41 |
| 100% | 194.02m | 0.50 | $97.01m | $-77.06m | $-6.943bn | -0.25 |
| 100% | 194.02m | 1.00 | $194.02m | $19.95m | $-5.265bn | 0.06 |

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
| low | $857.94m | $367.69m | $79.33m |
| base | $3.325bn | $1.425bn | $307.40m |
| high | $21.421bn | $9.180bn | $1.981bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/mandalay.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/southeast-asia/Myanmar/Mandalay) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `10a33b0f66863e3ba100b2dce0a6095571ddc468b8f99dbbc2703685a45180f3` |
| cost_evaluation_id | `1d9a7d25358affabb6e1973612640dab38e1c2c3fb649bd9025656e760ac5c73` |
| outline_evaluation_id | `1595a4f2428c5ca9cae8c678d1978e1f65b1e7c6524abdc38d4edc6f79d2ad37` |
| research_configuration_id | `677652108c3ec7568911ca1f625a027f0005bf851524de897cdea810025a19f0` |
| seed_id | `0393cb80ec7a9d04a244334a78613790c2b583a3d3e7f0b18326b9aa8bb0fc1e` |
| selected_alignment_id | `cee7ed2cbf0ef191adc7a7a72031edd6d926ad185aa4ff04afceda4036dca1da` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `fedf9d4d66340d33f94306a029bb368573c06b028f5bcb862297434687244ec9` |
| source_result_sha256 | `468de65c1308c85bff3da7713c8c63d1969afc951f226c93850e6459d2fc083f` |

Atlas packet `b4be0ab134936f3ba5f6ecfea9810a23aecb131522db8379d08ef922b5f151c1`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
