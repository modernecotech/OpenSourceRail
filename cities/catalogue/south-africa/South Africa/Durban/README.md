# Durban — railway design and city programme

**ZA · Calculated outline complete · Class C estimates · Physical verification pending**

[City index](../../../README.md) · [National programme](../NATIONAL-BRIEF.md) · [Interactive map](../../../../../docs/workbench/current/index.html?outlineCity=durban) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=durban) · [Methods and assumptions](../../../../../docs/design-engine/city-dossiers/README.md)

![Durban current calculated railway network with operational platforms and geographic context](engineering/outline/network.svg)

[Open full-size map](engineering/outline/network.svg) · [Download GIS bundle](engineering/outline/gis.zip) · [Complete dossier data](engineering/outline/summary.json)

## City and network

This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.

| Network measure | Current outline |
|---|---|
| Population context | 3,900,000 — retained planning input; not a demand survey |
| Selected alignment | Anchor preserving chord research |
| Route length / trackways | 450.13 km / 2 trackways |
| Lines / operational platform groups | 14 / 175 |
| Original access markers / separately costed access sites | 201 / 95 |
| Explicit interchange references | 49 |
| Fleet including reserve | 511 six-car trainsets |
| Train distance | 291,684 train-km/day; 106,464,689 /year |
| Service span | 18 h/day, 365 days/year; clock timetable not yet assigned |
| Peak demand brief | 4,000 passengers/h/direction per line — assumed, not additive network ridership |
| Planning occupancy / availability | 85% / 99% — assumptions |

Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.

### Lines, service and fleet

| Line | Route km | Platform groups | Headway s | One-way / circuit min | Active + reserve | Usable pphpd | Mapped termini |
|---|---|---|---|---|---|---|---|
| line-1 | 61.33 | 20 | 200 | 86.2 | 54 + 9 | 4,181 | NE terminal ↔ S terminal |
| line-2 | 47.08 | 17 | 200 | 67.4 | 43 + 7 | 4,181 | S terminal ↔ NE terminal |
| line-3 | 51.40 | 22 | 200 | 78.5 | 49 + 8 | 4,181 | N terminal ↔ S terminal |
| line-4 | 26.85 | 14 | 200 | 47.2 | 31 + 5 | 4,181 | SW terminal ↔ E terminal |
| line-5 | 33.22 | 11 | 200 | 46.1 | 30 + 5 | 4,181 | E terminal ↔ W terminal |
| line-6 | 32.73 | 15 | 200 | 50.7 | 33 + 5 | 4,181 | W terminal ↔ SE terminal |
| line-7 | 33.73 | 14 | 200 | 50.0 | 32 + 5 | 4,181 | NW terminal ↔ E terminal |
| line-8 | 29.92 | 18 | 200 | 58.7 | 38 + 6 | 4,181 | W terminal ↔ E terminal |
| line-9 | 91.18 | 27 | 200 | 128.7 | 78 + 12 | 4,181 | Ring / closed circuit |
| line-10 | 10.30 | 4 | 200 | 19.4 | 14 + 3 | 4,181 | S terminal ↔ SW terminal |
| line-11 | 6.26 | 2 | 200 | 6.3 | 6 + 1 | 4,181 | N terminal ↔ N terminal |
| line-12 | 11.60 | 4 | 200 | 18.7 | 14 + 3 | 4,181 | NE terminal ↔ NW terminal |
| line-13 | 8.30 | 4 | 200 | 11.5 | 9 + 2 | 4,181 | S terminal ↔ S terminal |
| line-14 | 6.23 | 3 | 200 | 8.3 | 7 + 2 | 4,181 | N terminal ↔ NE terminal |

Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.

[Line details and energy](engineering/outline/lines.csv) · [Station and access register](engineering/outline/stations.csv)

### Connections and access

Declared transfer graph: 1 connected line group(s): line-1, line-10, line-11, line-12, line-13, line-14, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9. These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.

<details><summary>Access and catchment assumptions</summary>

Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.

| Radius m | Straight line walk minutes | Station circle area sum km2 | Overlaps removed | Population coverage |
|---|---|---|---|---|
| 400.00 | 6.67 | 87.96 | False | Unestablished |
| 800.00 | 13.33 | 351.86 | False | Unestablished |

</details>

## Energy and propulsion

| Energy measure | Daily | Annual |
|---|---|---|
| Mechanical traction work | 1,187,647 kWh mechanical | 433.49 GWh mechanical |
| Nominal auxiliary load | 1,655,640 kWh | 604.31 GWh |
| Auxiliary supply including scenario charging losses | 1,742,779 kWh | 636.11 GWh |
| Reserve-fleet auxiliary supply scenario | See annual budget | 10.60 GWh |
| Total priced grid-supply scenario | See annual budget | 1,186.08 GWh |
| Physically supported total grid demand | Unestablished | Unestablished |

| Annual electricity budget | Low | Base | High |
|---|---|---|---|
| Priced supply/efficiency scenario | $76.04m | $196.37m | $589.47m |

Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.

| Line | Propulsion research concept | Additional traction mass / car | Additional reserve / car |
|---|---|---|---|
| line-1 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-2 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-3 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-4 | Station launch reference | 0 kg | 250 kg |
| line-5 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-6 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-7 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-8 | Station launch reference | 0 kg | 250 kg |
| line-9 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-10 | Station launch reference | 0 kg | 250 kg |
| line-11 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-12 | Station launch reference | 0 kg | 250 kg |
| line-13 | Powered axle continuous research | 1,000 kg | 250 kg |
| line-14 | Powered axle continuous research | 1,000 kg | 250 kg |

The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; they do not silently change that reference or establish complete installed equipment.

| Line | Motors/car / rated kW per car | Continuous feed | Required train force | Required mechanical peak | Station-fin comparison envelope | Actual force map |
|---|---|---|---|---|---|---|
| line-1 | 4 / 749.2 kW | 61.33 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-2 | 4 / 749.2 kW | 47.08 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-3 | 4 / 749.2 kW | 51.40 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-4 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-5 | 4 / 749.2 kW | 33.22 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-6 | 4 / 749.2 kW | 32.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-7 | 4 / 749.2 kW | 33.73 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-8 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-9 | 4 / 749.2 kW | 91.18 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-10 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-11 | 4 / 749.2 kW | 6.26 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-12 | 0 / 0.0 kW | 0.00 km | 156.1 kN | 3.12 MW | 316.5 m | Unestablished |
| line-13 | 4 / 749.2 kW | 8.30 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |
| line-14 | 4 / 749.2 kW | 6.23 km | 162.9 kN | 3.26 MW | Other interface | Unestablished |

These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.

### Why some lines use a research alternative

The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; this does not prove every station-powered design impossible or qualify the replacement hardware.

| Line | Affected reference legs | Necessary-bound failure | Longest affected leg | Reference flat coast reach |
|---|---|---|---|---|
| line-1 | 1 | Coast stops before receiving zone | 5,616.7 m | 5,554.5 m |
| line-2 | 1 | Coast stops before receiving zone | 6,031.1 m | 5,554.5 m |
| line-3 | 2 | Coast stops before receiving zone | 6,756.1 m | 5,554.5 m |
| line-5 | 1 | Coast stops before receiving zone | 6,398.4 m | 5,554.5 m |
| line-6 | 1 | Coast stops before receiving zone | 6,144.1 m | 5,554.5 m |
| line-7 | 1 | Coast stops before receiving zone | 6,489.3 m | 5,554.5 m |
| line-9 | 3 | Coast stops before receiving zone | 5,893.7 m | 5,554.5 m |
| line-11 | 1 | Coast stops before receiving zone | 6,258.4 m | 5,554.5 m |
| line-13 | 1 | Coast stops before receiving zone | 5,985.9 m | 5,554.5 m |
| line-14 | 1 | Coast stops before receiving zone | 5,845.8 m | 5,554.5 m |

## Civil works, depot and manufacture

| Quantity / resource | Calculated requirement |
|---|---|
| At grade route | 14.01 km |
| Bridge route | 15.17 km |
| Elevated route | 420.95 km |
| Tunnel route | 0.00 km |
| Precast span stock | 44,260 spans |
| Independent supports | 45,534 |
| Running rail | 1,800.52 rail-km / 108,409 t |
| Complete fastening sets | 3,150,909 |
| Protected at-grade crossing packages | 230 |
| Bridge runs / tunnel portals | 206 / 0 |
| Additional station track | 0 m |
| Access connector allowance | 1,858.8 m; actual accessible paths require survey |
| Pooled depot area | 357,188 m²; location and line connections require a site plan |
| Factory / civil working pattern | 2 / 2 shifts/day |

Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.

### Factory capacity and make/buy

| Factory investment | Low | Base | High |
|---|---|---|---|
| Vehicle equipment, tooling and premises | $1.57m | $7.91m | $48.54m |
| Civil production campaign | $12.38m | $61.15m | $366.89m |

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
| low | make | 18 | 154,910 | 1,150,760 | 1,534,347 |
| base | make | 42 | 376,210 | 3,009,680 | 4,012,907 |
| high | make | 114 | 1,017,980 | 8,320,880 | 11,094,507 |

[Complete manufacturing routes and comparisons](engineering/outline/make_buy.csv) · [Quantities and delivery requirements](engineering/outline/delivery_requirements.csv) · [Vehicle, station and civil 3D models](../../../../../docs/engineering-models/README.md)

## Workforce and construction programme

Production and civil works use two shifts. The operating case uses 18 service hours/day and a 2-shift planning convention; named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.

| Domain / case | Covered positions per shift | Two-shift people floor | Paid person-hours | Paid FTE equivalent |
|---|---|---|---|---|
| Control room and access-site coverage / low | 97 | Unestablished | 701,019 | 350.5 |
| Vehicle production / low | 72 | 144 | Unestablished | Unestablished |
| Civil field / low | 161 | 322 | 1,665,963 | Unestablished |
| Civil other installation / low | 1,012 | 2,024 | 10,519,295 | Unestablished |
| Civil precast / low | 144 | 288 | 1,534,347 | Unestablished |
| Control room and access-site coverage / base | 194 | Unestablished | 1,593,225 | 796.6 |
| Vehicle production / base | 205 | 410 | Unestablished | Unestablished |
| Civil field / base | 595 | 1,190 | 5,233,941 | Unestablished |
| Civil other installation / base | 7,424 | 14,848 | 65,328,594 | Unestablished |
| Civil precast / base | 336 | 672 | 4,012,907 | Unestablished |
| Control room and access-site coverage / high | 388 | Unestablished | 3,823,740 | 1,911.9 |
| Vehicle production / high | 562 | 1,124 | Unestablished | Unestablished |
| Civil field / high | 2,591 | 5,182 | 14,507,968 | Unestablished |
| Civil other installation / high | 75,543 | 151,086 | 423,040,581 | Unestablished |
| Civil precast / high | 912 | 1,824 | 11,094,507 | Unestablished |

Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.

| Function / skills | Base coverage posts | Paid FTE | Authority / staffing boundary |
|---|---|---|---|
| Control room / dispatch / response | 4 | 16.4 | Source control/access coverage; operations authority requires separate assurance |
| Station and access-site service | 190 | 780.2 | Source access coverage; accessible assistance and local duties require roster design |
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
| Installed capital | $2.112bn | $7.616bn | $46.533bn |
| Installed capital / route-km | $4.69m | $16.92m | $103.38m |
| 30-year whole-life NPV | $4.257bn | $15.030bn | $86.886bn |
| Annual operating provision | $101.64m | $333.40m | $1.690bn |

US dollars, 4% real discount rate, 30-year horizon. Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.

| Scope | Installed capital · base | Whole-life NPV · base |
|---|---|---|
| Rolling stock | $1.608bn | $1.608bn |
| Guideway | $655.73m | $655.73m |
| Stations power | $1.072bn | $1.072bn |
| Factory tooling | $69.06m | $69.06m |
| Construction | $3.593bn | $3.593bn |
| Land utilities depot | $419.88m | $419.88m |
| Fleet | $147.23m | $147.23m |
| Energy | $0 | $3.396bn |
| Operations | $0 | $215.52m |
| Maintenance | $0 | $1.948bn |
| Renewals | $0 | $1.578bn |
| Recovery | $51.32m | $104.57m |
| Reliability | $0 | $152.40m |
| Disposal | $0 | $70.45m |

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
| City project risk contingency | $1.523bn | 20.0% |
| Network delivered assembled fleet | $1.245bn | 16.3% |
| Bridge special foundations deck temporary | $653.15m | 8.6% |
| Design prototypes independent review | $450.34m | 5.9% |
| Repeat box beams | $325.70m | 4.3% |

[Annual energy budget](engineering/outline/energy_budget.csv) · [Local operating inputs](engineering/outline/local_cost_inputs.csv)

### Civil classification comparison

The headline retains the mapped civil allowances. A separate alternative uses the retained WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.

| Same-route, same-service estimate | Low | Base | High |
|---|---|---|---|
| Headline installed capital | $2.112bn | $7.616bn | $46.533bn |
| Water-evidence alternative capital | $2.077bn | $7.413bn | $44.880bn |
| Alternative capital / route-km | $4.62m | $16.47m | $99.70m |
| Alternative whole-life NPV | $4.222bn | $14.825bn | $85.195bn |
| Included non-water obstruction reserve | $563,730 | $3.76m | $26.31m |

7.52 km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. 14 water/civil interface holds require investigation. The reserve is a provisional estimate, not evidence that the crossing work is fully sized. Historical evidence revision: `a0389044828f`. This comparison does not select a new alignment, civil design or physical baseline.

### Passenger receipts and funding scenarios

The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.

| Demand sensitivity | Assumed annual paid trips | Fare US$ | Annual receipts | Operating balance | 30-year receipts less costs NPV | Post-grace DSCR |
|---|---|---|---|---|---|---|
| 50% | 150.91m | 0.25 | $37.73m | $-295.67m | $-14.377bn | -0.60 |
| 50% | 150.91m | 0.50 | $75.45m | $-257.94m | $-13.725bn | -0.52 |
| 50% | 150.91m | 1.00 | $150.91m | $-182.49m | $-12.420bn | -0.37 |
| 75% | 226.36m | 0.25 | $56.59m | $-276.81m | $-14.051bn | -0.56 |
| 75% | 226.36m | 0.50 | $113.18m | $-220.22m | $-13.073bn | -0.45 |
| 75% | 226.36m | 1.00 | $226.36m | $-107.04m | $-11.116bn | -0.22 |
| 100% | 301.81m | 0.25 | $75.45m | $-257.94m | $-13.725bn | -0.52 |
| 100% | 301.81m | 0.50 | $150.91m | $-182.49m | $-12.420bn | -0.37 |
| 100% | 301.81m | 1.00 | $301.81m | $-31.58m | $-9.811bn | -0.06 |

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
| low | $1.479bn | $633.74m | $136.73m |
| base | $5.331bn | $2.285bn | $492.95m |
| high | $32.573bn | $13.960bn | $3.012bn |

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
| [Current outline record](../../../../../docs/design-engine/city-atlas/cities/durban.json.gz) | Same-candidate service, costs and selected geometry |
| [Geographic source](city.json) / [context](map-context.json.gz) | Planning inputs and attribution |

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
```

A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.

[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/south-africa/South%20Africa/Durban) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.

<details><summary>Candidate and calculation identities</summary>

| Identity | Value |
|---|---|
| city_input_id | `df989851953169e9d11213000290fad2d08c8463435f3ac8bb6d22f2ec34b808` |
| cost_evaluation_id | `d021268e717c5806f8ff518cf158870b0bac22b1b916e6fc6ad041c625b13558` |
| outline_evaluation_id | `6276417c3f92d6bbe7659768f978a8b3f0722efb53bfd87ad27f05cebbaf04fe` |
| research_configuration_id | `4ad9b50db2cc32e6a47fbc44c84f67064be80428c31ccdf99d4c175fc6900b92` |
| seed_id | `f55da2f3d165f33f5387f93b40c835605aedb4a1f7d537327c22baaa14a1d0dd` |
| selected_alignment_id | `f50fe81e245941db1051ba87afd6835554697a0c0b6669f4a4d665ab29b0ba8f` |
| selected_alignment_kind | `anchor-preserving-chord-research` |
| selection_id | `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803` |
| service_evaluation_id | `4824c7bd52f80b629041a092fe283e67c6b7698f5e95c45cc384afe09f33e468` |
| source_result_sha256 | `9d6337e7c57b105b6e06fa00b56cc6bdb9e0fc1e1c3726958386b296ce1c8855` |

Atlas packet `8463e6bd2c58039e7bd8b131b0713809045c5521126e9616f253916ae0c247d3`. Physical reference `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.

</details>

[Project introduction](../../../../../README.md) · [Current engineering](../../../../../docs/design-engine/current/README.md)
