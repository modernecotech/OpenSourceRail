# Vijayawada — Urban Rail Network

**Country:** IN · **Population:** 1,500,000

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey case, this OSR plan avoids **$2.82 bn (86.5%) of external capital** and **$3.47 bn of external interest**. Capital plus saved interest totals **$6.29 bn over the 40-year financing life**. Both cases use the same 4.5% external rate and financing schedule; the turnkey external requirement is assumed debt-financed, and the benchmark remains an editable sensitivity, not a vendor quote.

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Vijayawada rail network on OpenStreetMap](vijayawada-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`vijayawada.corridor.geojson`](vijayawada.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 67 |
| Interchange-class stations | 10 |
| Multi-line transfer reachability | 47% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 82.8% |
| Route length (double track) | 228.3 km |
| Revenue fleet | 239 × 4-car trainsets |
| Revenue fleet passenger capacity | 114,720 AW2 pax (152,960 AW3 crush) |
| Dedicated depot-service rotation fleet | 0 (off-peak service uses peak-fleet surplus) |
| Spare + cold-reserve | 27 × 4-car trainsets |
| Peak headway | 3 min |
| Station spacing policy | 1.6 km central / 3 km urban / up to 7 km on suburban approaches and the lowest-demand outer fringe |
| City-centre consolidation | Cross-line platforms within the 600 m station-complex envelope are emitted as one interchange |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Turnaround inspection and recharge

During the 07:00–09:00 and 15:00–17:00 peaks, trains make the normal quick terminal turnback: no depot-service hold is inserted, allowing more battery depletion while the 20% dispatch-reserve gate remains mandatory. In the 6- and 12-minute lower-frequency windows, each line's deterministic energy controller may widen the published headway when actual charging delivery leaves a departing set below the 40% normal-service SoC target (up to 3× the published headway). This automatically matches offered off-peak service to available traction energy without buying a separate service-rotation fleet. In those lower-frequency windows, each train receives a **12-minute service slot** at its designated powered service point. This may be a staffed terminal platform or the main depot; only defects and maintenance require a depot move. Interior cleaning, exterior and running-gear walk-around, door/coupler/emergency-equipment checks, fault-log download, and a 150 kW low-C recharge run concurrently. A red defect holds the set for maintenance; a clear inspection returns it to the revenue rotation.

The fleet is sized for the 3-minute peaks; when service relaxes to 6 or 12 minutes, the same peak fleet provides enough idle cover for service-point work. Therefore **0 additional trainsets** are required for depot service; only the existing 21 planned-maintenance spares and 6 cold-reserve sets are included in the rolling-stock, production-plant, maintenance, labour, and total CAPEX/OPEX figures below.

## Distributed overnight stabling

At service close, telemetry-healthy trainsets remain at selected powered passenger stations near their first morning departures. Every occupied station must provide at least 150 kW low-C charging, CCTV, remote traction isolation, protected emergency access, and an OCC-assigned train/track slot. Sets with red defects, overdue heavy maintenance, failed isolation, or failed security return to the main-heavy depot. OCC verifies charge completion and remote self-test before releasing all station-stabled sets together at service start. The generated default therefore builds one maintenance-focused main depot, not a parking depot at every terminus.

Circumferential lines use the same demand-based stop-spacing policy as radials (1.0× the equivalent radial spacing), while every forced radial-transfer platform is retained. Charging-platform dwell is 240 seconds, calculated from one circuit's climate-adjusted energy and the line's aggregate charging power; non-charging halts keep their ordinary dwell.

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 33.1 km | 11 | 52 | NW Outer ↔ SE Mid |
| line-2 | 28.8 km | 10 | 45 | NE Mid ↔ SW Outer |
| line-3 | 43.4 km | 13 | 65 | E Outer ↔ W Outer |
| line-4 | 25.0 km | 8 | 41 | E Mid ↔ NW Outer |
| line-5 | 23.3 km | 7 | 34 | NE Inner ↔ S Outer |
| line-6 | 74.7 km | 18 | 29 | NW Mid ↔ W Mid |
| **Total** | **228.3 km** | **67 unique** | **266** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 720 kWh usable / 900 kWh nameplate per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 114,720 AW2 pax (152,960 AW3 crush) |
| Total fleet capacity | 127,680 AW2 pax (170,240 AW3 crush, incl. service rotation + spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 239 × 480 = **114,720 AW2 passengers** (152,960 AW3 crush)
- **Total fleet passenger capacity:** 266 × 480 = **127,680 AW2 passengers** (170,240 AW3 crush, incl. service rotation + spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Scheduled one-way train journeys:** **2,558/day**
- **Daily theoretical capacity from timetable:** 2,558 scheduled one-way train journeys/day × 480 AW2 pax = **1,227,600 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **982,080 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **179.2 – 286.8 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **1,500,000**
- Anchor-weighted coverage: 82.8%
- Catchment population: **≈ 1,242,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 19 | 300 kW | 1500 kWh |
| Major | 2 | 300 kW | 1500 kWh |
| Standard | 24 | 300 kW | 1500 kWh |
| Terminal | 9 | 300 kW | 1500 kWh |
| **Total installed** | **55** | **21,200 kW** | **121,000 kWh** |

Aggregate station-rail charging power: **82,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh usable (900 kWh nameplate) battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **343.2 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Onboard battery adequacy | 4.8× worst inter-charge run | OK: 900 kWh nameplate, 180 kWh protected reserve, and 569 kWh usable margin across the worst powered-stop gap (line-6) |
| Lowest traversal charging margin | 136 kWh | line-5 after climate load, 98% conversion, and the required 10% operating margin |
| PV daily yield proxy | 102 MWh/day | 4.8 peak-sun-hour planning proxy before local derates |
| Scheduled one-way train journeys | 2,558 / day | Train departures across both directions and all lines |
| Scheduled train journey-km | 88,781 train-km/day | One-way train journeys × route length |
| Annual service work | 35.0 M train-km/yr | Includes 108% depot/deadhead factor |
| Scheduled traction demand | 1,534 MWh/day | 140.0 M car-km/yr × 4.0 kWh/car-km |
| On-site PV shortfall before solar plant | 1,432 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 343.2 MW / 1,647 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 121 MWh | Distributed LFP buffer for charging peaks and grid outages |

Opportunity charging is checked line by line; ring trains remain in service while receiving the longer planned dwell at every powered platform.

| Line | Powered stops | Climate-adjusted traversal | Delivered per traversal | Required-margin surplus | Worst powered-stop gap |
|---|---:|---:|---:|---:|---:|
| line-1 | 9 | 330 kWh | 576 kWh | 212 kWh | 9.5 km / 94 kWh |
| line-2 | 10 | 287 kWh | 539 kWh | 223 kWh | 3.5 km / 35 kWh |
| line-3 | 11 | 433 kWh | 723 kWh | 246 kWh | 13.1 km / 130 kWh |
| line-4 | 6 | 250 kWh | 441 kWh | 166 kWh | 11.8 km / 118 kWh |
| line-5 | 7 | 233 kWh | 392 kWh | 136 kWh | 6.6 km / 66 kWh |
| line-6 | 12 | 746 kWh | 1,176 kWh | 356 kWh | 15.1 km / 151 kWh |

## CAPEX (planning grade)

Base figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Full generated bundles add the scenario-dependent dedicated solar plant and finance reconciliation under `build/`. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields are explicit converted reporting views at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), distributed overnight stabling that reduces depot parking and local commissioning-bay scope, at-grade depots without overhead bridge cranes, **trainset-family rolling-stock units** (for example $900 k per 3-car light-metro trainset, with the raw marketplace BOM retained only as an audit floor), commodity LFP packs + heavy-vehicle PMSM motors + matched commercial traction controllers, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line includes direct material, local assembly/labour, nominal per-train QA/acceptance, and modest local handover logistics. Fixtures, tooling, and production-readiness live in one shared national railway production plant at $60 k per supported vehicle/car module, with $120 k retained as the high sensitivity check. That national asset is excluded from city CAPEX and costed once in the country brief; warranty, spares, and routine commissioning support are OPEX rather than repeated train CAPEX. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

Rates are **design-derived planning targets**, generated from the parametric CAD quantity model and the reviewed benchmark calibration in `lib/templates/civil-cost-calibration.toml`. They are not quotations; foundation-zone schedules and normalized supplier offers remain release gates.

| Bucket | Value |
|---|---|
| At-grade (210.2 km @ $2.58 M/km) | $543 M |
| Elevated (18.1 km @ $9.75 M/km) | $176 M |
| Elevated-interchange premium (9 sites @ $4.50 M) | $40 M |
| **Civil subtotal** | **$760 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 12 | $600 k | $7.2 M |
| `standard` | 24 | $2.50 M | $60 M |
| `major` | 2 | $4.50 M | $9.0 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
| `interchange-elevated` | 17 | $12.0 M | $204 M |
| **Stations subtotal** | | | **$342 M** |

### Depots

At-grade workshop and inspection facilities sized for maintenance, not fleet-wide parking. Healthy trainsets stable and recharge at powered passenger stations overnight; depot roads retain defect, wheel, wash, inspection, and heavy-maintenance functions.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $8.0 M | $8.0 M |
| **Depots subtotal** | | | **$8.0 M** |

### Rolling stock

Rolling stock is costed by **local-owner trainset-family unit**, not by multiplying an inflated per-car price. The anchor 3-car light-metro BOM floor is 662,590 USD direct material plus 28 % local assembly/labour allowance = 848,115 USD per 3-car consist. City CAPEX rounds this to a $900 k local-owner unit for a 3-car light-metro trainset, leaving only nominal QA/acceptance evidence and handover inside the trainset line. Fixtures, tooling, and production-readiness are carried in the railway production plant line below. Warranty, initial spares, and routine commissioning support are treated as operating costs. Motors, sensors, train-control computers, onboard batteries, roof PV, and charge hardware appear here ONLY — never re-billed elsewhere in the city cost stack.

| 3-car light-metro anchor bucket | Basis | Cost |
|---|---|---|
| Direct material BOM floor | Welded frame, panels, glazing, doors, articulation/gangways, end couplers, bogies, suspension air supply, traction, batteries, HVAC, electronics, interiors | $663 k |
| Local assembly/labour allowance | 28% BOM allowance after one-shift clip-on body installation; includes fit-out, harnessing, paint, shop supervision, utilities, and rework reserve | $186 k |
| Nominal QA + handover allowance | Acceptance evidence, test dossier, local movement, manuals/training handover; warranty/spares stay in OPEX | $52 k |
| **Total per 3-car trainset** | Local-owner production planning unit | **$900 k** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-4car` (revenue + service rotation + spare + cold reserve) | 266 | $1.12 M | $298 M |

#### 800 V procurement basis

The following RFC 0021 commodity-component reconciliation is already included in the delivered rolling-stock and charging-site planning units; it is shown for auditability and is not additive.

| Component | Current design basis |
|---|---:|
| Onboard architecture | 800 V-class; 650-700 V nominal traction DC bus |
| Gross traction battery | 225 kWh/car; 24,167 USD/car |
| PMSM motor + controller sets | 2/car @ 10,000 USD/set |
| Core electrical subtotal | 51,000 USD/car; 204,000 USD/trainset |
| Normal 500 kWh / 500 kW station equipment | 65,000 USD; 100,000 USD integrated allowance |

### Shared national railway production plant

This city does **not** carry a separate trainset factory. One national plant supplies every city through a phased production programme, while rails, viaducts, stations, and depots remain city/regional delivery scope. The national plant includes tooling, fixtures, plant services, production-readiness, and commissioning-bay setup. Standard 1 m fiberglass body moulds, dry clips, and compact gauges replace a full-length body mould and adhesive cure hall. It is costed per vehicle/car module, not per trainset, and the factory is sized to the largest single-city fleet programme rather than duplicated for every network. See [`../NATIONAL-BRIEF.md`](../NATIONAL-BRIEF.md).

| City treatment | Indicative modules | National sizing unit | City CAPEX |
|---|---:|---:|---:|
| Fleet demand passed to national production plan | 1064 | $60 k | **$0 k** |
| National high sensitivity (shown for scale, not added here) | 1064 | $120 k | $0 |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 343,175 kW @ $700/kW | $240 M |
| Grid interconnection / PPA tie-in | 343,175 kW @ $100/kW | $34 M |
| Annual generation proxy | 343.2 MW × 4.8 peak-sun-h/day × 365 d/yr | 601.2 GWh/yr |
| **Dedicated solar plant subtotal** | | **$275 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 228.3 km × $0.050 M/km | $11 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $18 M |
| EPC integration + project management (7%) | on subtotal | $101 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $760 M |
| Stations | $342 M |
| Depots | $8.0 M |
| Rolling stock | $298 M |
| Shared national railway production plant (outside city CAPEX) | $0 k |
| Dedicated solar power plant | $275 M |
| Residual train-control wayside + charging microgrids | $30 M |
| EPC overhead (7%) | $101 M |
| **CAPEX total** | **$1.81 bn** |
| Per-route-km | $7.9 M / km |
| Per-capita (city pop) | $1,208 / person |


### Procurement origin and foreign-capital exposure

| Bucket | Total | Imported share | Imported / external capital | Local content / local funding |
|---|---:|---:|---:|---:|
| Civil works | $760 M | 15% | $114 M | $646 M |
| Stations | $342 M | 20% | $68 M | $273 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $298 M | 35% | $104 M | $194 M |
| Dedicated solar plant | $275 M | 45% | $124 M | $151 M |
| Residual signalling / train control | $11 M | 50% | $5.7 M | $5.7 M |
| Charging microgrids | $18 M | 40% | $7.3 M | $11 M |
| EPC / project services | $101 M | 15% | $15 M | $86 M |
| **Total city CAPEX** | **$1.81 bn** | **24.3%** | **$440 M** | **$1.37 bn** |

## Construction QA system

Every locally built trainset and every fixed-asset package moves through owner-controlled hold points before the next construction stage starts. The machine-readable gate list is in [`lib/templates/construction-qa.toml`](../../../../lib/templates/construction-qa.toml); the governing doctrine is [RFC 0028](../../../../docs/rfcs/0028-construction-quality-assurance.md).

| Gate | Domain | Asset coverage | Hold point / evidence |
|---|---|---|---|
| `qa-00-design-freeze` | system | whole railway | design freeze: approved drawing register, interface control document, hazard-log snapshot, inspection/test plan, material and supplier register |
| `qa-10-carbody-structure` | rolling-stock | carbody, underframe, crash structure, coupler pockets | fabrication: EN 15085 weld pack, welder qualifications, material certificates, dimensional report, NDT report, coating record |
| `qa-11-bogie-wheelset` | rolling-stock | bogies, wheelsets, suspension, brake rigging | subassembly: bogie frame NDT, wheel profile and axle UT/MT, bearing certificate, brake static test, torque/fastener log |
| `qa-12-traction-brake-battery` | rolling-stock | traction motors, inverters, brake blending, onboard battery, thermal system | systems integration: motor/inverter factory test, insulation resistance, BMS cell map, contactor test, thermal soak, brake-rate test |
| `qa-13-passenger-systems` | rolling-stock | doors, HVAC, lighting, interiors, accessibility, passenger information | fit-out: door cycle log, HVAC performance test, saloon inspection, PRM checklist, emergency equipment inventory |
| `qa-14-onboard-control` | rolling-stock | TCN-E, onboard ATP/ATO computers, odometry, radios, sensor suite | software/hardware acceptance: hardware serial register, firmware hash register, cybersecurity checklist, simulator replay, trainline continuity test |
| `qa-15-first-article-trainset` | rolling-stock | complete trainset | first article and batch release: first-article inspection report, 1,000 km fault-free run, braking curves, charging logs, rescue/coupling drill, maintainability demonstration |
| `qa-20-survey-geotech` | infrastructure | alignment, ROW, geotechnical and utilities | pre-construction: topographic survey, utility scan, borehole/test-pit log, flood/drainage map, ROW constraint register |
| `qa-21-earthworks-drainage` | infrastructure | earthworks, subgrade, drainage, fencing | civil works: compaction test, material gradation, drainage as-built, culvert inspection, fence/gate punch list |
| `qa-22-trackform-rail` | infrastructure | slab track, rail, fasteners, welds, turnouts, level crossings | track installation: track geometry run, weld NDT, fastener torque log, turnout detection test, crossing functional test |
| `qa-23-structures` | infrastructure | viaducts, bridges, bearings, expansion joints, parapets, walkways | structures: concrete/rebar records, bearing survey, load/test certificate where required, expansion-joint record, walkway inspection |
| `qa-24-stations-depots-plant` | infrastructure | stations, depots, railway production plant, public realm | building works: platform gauge survey, canopy inspection, fire/life-safety signoff, accessibility audit, tool calibration, depot bay test |
| `qa-25-power-energy` | infrastructure | PV, stationary storage, chargers, grid/PPA interconnection, earthing | energy commissioning: PV string test, BESS commissioning record, charger load test, protection relay settings, earthing test, isolation drill |
| `qa-26-wayside-comms-safety` | infrastructure | wayside nodes, switches, intrusion sensors, comms, fare and passenger systems | systems commissioning: W-SBC identity register, radio coverage, switch proof test, sensor calibration, CCTV/fare-system test, penetration-test closeout |
| `qa-30-integrated-trial-running` | system | whole railway | trial running and handover: trial-running log, timetable reliability report, emergency exercise, possession/handback records, open-defect register, safety-case release note |

## Funding & affordability

Planning-grade procurement-origin and financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Imported content defines the minimum foreign-currency / international capital requirement; locally supplied content can be financed with domestic-currency bonds, public equity, or other local sources. It is a pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh vijayawada`.

### Imported value and construction capital requirement

The localization-first import percentage is calculated bucket by bucket from the controlled procurement-origin assumptions in [`lib/templates/capex-costs.toml`](../../../../lib/templates/capex-costs.toml). It is not a tariff estimate: it identifies the value that must be paid in foreign currency or backed by an international financing source. The shared national trainset factory is outside this city CAPEX and appears once in the country `NATIONAL-BRIEF.md`.

| Capital boundary | Share of city CAPEX | Total requirement | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imported components / machinery** | **24.3%** | **$440 M** | **$88 M / yr** |
| **Local capital for domestic procurement / payroll** | **75.7%** | **$1.37 bn** | **$274 M / yr** |
| of which planned local bond issuance | 60.6% of total CAPEX | $1.10 bn | $220 M / yr |
| **Total city programme** | **100.0%** | **$1.81 bn** | **$362 M / yr** |

### Foreign-company turnkey comparison

This is an editable like-for-like sensitivity, not a vendor quotation. It multiplies OSR CAPEX for an equivalent network, fleet, service, and energy scope, then assumes 90% of the foreign contractor price requires foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price. Lifetime interest uses the same 4.5% rate, 5-year construction interest period, and 35-year amortization for both cases; the comparator external requirement is assumed debt-financed.

| Foreign-turnkey case | Cost multiplier vs OSR | Foreign-company external capital | OSR external capital saved | External interest saved over financing life | Capital + interest saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $2.45 bn | $2.01 bn (82.0%) | $2.47 bn | **$4.47 bn** |
| **Default** | 2.00× | $3.26 bn | $2.82 bn (86.5%) | $3.47 bn | **$6.29 bn** |
| High | 3.00× | $4.89 bn | $4.45 bn (91.0%) | $5.47 bn | **$9.93 bn** |

At the default 2.00× case, OSR's $440 M external requirement is 86.5% below the illustrative foreign-company requirement of $3.26 bn; the associated lifetime external-interest saving is $3.47 bn, and total project CAPEX is 50.0% lower. Replace both variables with normalized bids before an investment decision.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (local public-equity drawdown + interest-only grace on external import finance and local bonds; capital-raising draws are shown above; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$154 M / yr** | $102 |
| Steady-state, low capacity-use (year 6+) | **$39 M / yr** | $26 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$112 M / yr** | $75 |
| Lifecycle envelope (yr 1–40, low scenario) | **$2.12 bn cumulative** | $1,415 |
| Lifecycle envelope (yr 1–40, high scenario) | **$769 M cumulative** | $512 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$4.68 bn cumulative** | $3,122 |

_Population basis: 1,500,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $73 M / yr → $112 M / yr._

### CAPEX funding sources

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| External climate/MDB debt for imported content (unconfirmed) | 24% | $440 M | 4.5% | 40 y, 5 y grace | $25 M / yr |
| Local-currency sovereign / project bonds for local content | 61% | $1.10 bn | 7.2% | 40 y, 5 y grace | $87 M / yr |
| Local government equity / other domestic funding (no debt service) | 15% | $274 M | — | — | — |
| **Total** | **100%** | **$1.81 bn** | | | **$112 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — external import-finance debt $20 M / yr + local bonds $79 M / yr = **$99 M / yr** total. The base case assumes no climate-development grant. Local public equity is drawn across construction ($55 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

_Loan availability note: this is a finance placeholder, not a committed lender offer. Plausible providers would be a national government borrowing through an MDB or a climate fund accredited entity, such as the World Bank/IBRD, Islamic Development Bank, Climate Investment Funds, or Green Climate Fund channels. Official GCF policy allows grants and concessional loans, and World Bank/CIF material documents below-market climate finance, but this project still needs a lender mandate, eligibility screen, and signed term sheet before the 4.5% / 40-year assumption can be treated as real. Evidence anchors: [GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), [GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), [World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), [CIF funding instruments](https://www.cif.org/cif-funding), and [IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $12 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $22 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $571 k |
| Traction energy (560.0 GWh / yr) | 88,781 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 37.1 GWh/yr + dedicated solar plant 343.2 MW / 601.2 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $4.1 M |
| Labour (931 FTE) | driverless roster: OCC/remote 154, station/platform 266, passenger service 111, fleet maintenance 197, infrastructure/energy 176, admin/training 27; no train drivers × country median × 12 × engineer-premium 1.4 | $3.6 M |
| **OPEX subtotal** | | **$42 M / yr** |

_Annual service work: 88,781 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 35.0 M train-km / yr (140.0 M car-km / yr). On-site PV covers 37.1 GWh/yr and the dedicated solar plant adds 601.2 GWh/yr against 560.0 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

## Maintenance schedule system

Baseline scheduled work covers 266 trainsets, 67 stations, 228.3 route-km, 6 lines, and 88,781 scheduled train-km/day. Intervals are defined in [`lib/templates/maintenance-schedule.toml`](../../../../lib/templates/maintenance-schedule.toml) and governed by [RFC 0029](../../../../docs/rfcs/0029-maintenance-schedule-system.md).

| Asset group | Cadence / trigger | Scope | Evidence owner |
|---|---|---|---|
| rolling-stock | daily / each depot return; calendar | walk-around, wheel/tread visual, doors, HVAC, coupler face, saloon damage, emergency equipment, fault-log download | daily inspection work order; fleet maintenance |
| rolling-stock | 7 days; calendar | wheel wear, brake pad thickness, BMS cell spread, under-car chafe, roof/PV cleaner, door obstruction sensors | weekly inspection measurements; fleet maintenance |
| rolling-stock | 30 days; calendar | BMS deep scan, motor-bearing vibration, inverter thermal log, HVAC filters, passenger information, CCTV, firmware inventory | monthly A-class service report; fleet maintenance |
| rolling-stock | 150,000 km or wear limit; km / condition | wheel profile measurement, lathe reprofiling, post-lathe inspection | wheel profile before/after record; main-heavy depot |
| rolling-stock | 600,000 km; km | bogie strip, frame inspection, bearing renewal, suspension check, brake rigging overhaul | bogie overhaul dossier; main-heavy depot |
| rolling-stock | 10 years; calendar | corrosion inspection, interior refurbishment, cable replacement, HVAC renewal, paint/body repairs | body overhaul acceptance record; main-heavy depot |
| stations | daily; calendar | cleaning, lighting, platform edge inspection, PA/PIS/fare equipment check, CCTV status, emergency equipment check | station opening/closing checklist; station operations |
| stations | 7 days; calendar | canopy/fixing visual, platform drainage, ramps/tactiles, charger cabinet visual, fire extinguishers, signage | weekly station inspection; station maintenance |
| stations | 30 days; calendar | emergency lighting, fire alarm, UPS, lift/escalator where fitted, access control, public Wi-Fi/comms cabinets | monthly station systems test; station maintenance |
| stations | 12 months; calendar | structural survey, canopy PV fixings, drainage capacity, accessibility audit, passenger-flow and wayfinding review | annual station condition report; owner engineer |
| track-civil | 7 days; calendar | visual walk for rail damage, fasteners, slab cracking, drainage blockages, fence/gate damage, vegetation | track walk log; maintenance of way |
| track-civil | 60-90 days by preset; calendar | geometry recording run, trend comparison, gauge/cant/alignment/twist defect classification | geometry report and defect register; maintenance of way |
| track-civil | 30 days; calendar | point closure, detection, lubrication, bolt torque, weld cracks, stretcher/drive inspection | switch inspection and functional test; maintenance of way |
| structures | 12 months; calendar | visual structure inspection, bearing/joint survey, parapets, walkways, drainage, scour check for water crossings | annual structures inspection; civil structures engineer |
| energy | daily remote; calendar / telemetry | SCADA alarm review, charger availability, battery SOC/temperature, PV yield anomaly, grid import/export | daily energy dashboard signoff; energy operations |
| energy | 30 days; calendar | charger load test sample, BESS thermal inspection, PV soiling/cleaning, cabinet seals, protection status | monthly energy maintenance report; energy maintenance |
| energy | 12 months; calendar | protection relay test, earthing resistance, emergency isolation drill, battery capacity sample, PV string insulation | annual electrical safety certificate; energy systems lead |
| signalling-comms | daily remote; calendar / telemetry | health dashboard, radio coverage alarms, time sync, message-authentication failures, CCTV/fare/PIS fault queue | daily systems health report; systems operations |
| signalling-comms | 30 days; calendar | switch proof test, sensor calibration sample, comms cabinet inspection, backup link test, UPS test | monthly systems maintenance report; systems maintenance |
| signalling-comms | 90 days; calendar | firmware inventory, vulnerability review, backup restore test, degraded-mode drill, simulator replay of safety scenarios | quarterly assurance report; systems assurance |
| depots-production | 30-180 days by tool criticality; calendar / usage | tool calibration, lifting equipment inspection, pit/stinger checks, wheel-lathe calibration, welding fixture survey | tool calibration and workshop safety register; depot workshop manager |

_Amber defects are scheduled within 7 days; red defects hold the asset out of service or isolate the affected railway section until rectified. Every task produces a signed work order, asset id, date/time, finding code, defect severity, parts used, and return-to-service authority._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.61 |
| Day pass (3 trips) | $1.56 (15 % bulk discount) |
| Monthly unlimited pass | $18.40 (~8 % of median monthly income) |
| Annual pass | $202.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (982,080 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the external/local CAPEX funding sources, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 17% |
| Annual paid trips | 179.2 M | 286.8 M | 60.0 M |
| Annual paid trips / city resident | 119 | 191 | 40 |
| Farebox revenue | $110 M / yr | $176 M / yr | $37 M / yr |
| Station shop leases | $2.2 M / yr | $2.2 M / yr | $2.2 M / yr |
| Advertising boards | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| **Total revenue** | **$116 M / yr** | **$182 M / yr** | **$42 M / yr** |
| Revenue / OPEX recovery | 273% | 428% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $112 M / yr | $112 M / yr | **$112 M / yr** |
| Operating surplus applied to debt support | -$73 M / yr | -$112 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $39 M / yr | $0 k / yr | **$112 M / yr** |
| Operating surplus after OPEX (before debt support) | $73 M / yr | $139 M / yr | $0 / yr |

_Commercial-revenue assumptions: 11,272 m² of station shop/kiosk leases at $18/m²/month and 2,092 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-free procurement-origin funding boundary, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $32 M / yr | $51 M / yr | 16 min/trip × $0.66/h value-of-time proxy |
| Avoided road congestion | $52 M / yr | $83 M / yr | 645 M - 1,032 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $9.3 M / yr | $15 M / yr | 116.1–185.8 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $26 M / yr | $41 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $56 M / yr | $90 M / yr | 21% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $28 M / yr | $46 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$203 M / yr** | **$325 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 3 education anchors | 24,061 trips/school day; 5.3 M access-events/yr | 38,498 trips/school day; 8.5 M access-events/yr |
| Healthcare | 19 healthcare anchors | 51,232 trips/day; 18.7 M access-events/yr | 81,971 trips/day; 29.9 M access-events/yr |
| Commerce | 31 major/terminal/interchange nodes | 102,422 trips/trading day; 33.8 M access-events/yr | 163,875 trips/trading day; 54.1 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 52,050 trips/activity day; 15.6 M access-events/yr | 83,280 trips/activity day; 25.0 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $1.37 bn | 76% of $1.81 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $2.20 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $439 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 124,287 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 179.2 M - 286.8 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Financial validation

The machine-readable finance check reconciles the design-base CAPEX with the scenario-dependent solar plant and records deterministic cash-flow sensitivities. It is a planning screen, not financial close.

| Check | Result |
|---|---:|
| Authoritative design-base CAPEX | $1.54 bn |
| Timetable-sized dedicated solar CAPEX | $275 M |
| **Reconciled project CAPEX** | **$1.81 bn** |
| Imported / external-capital requirement | $440 M (24.3%) |
| Local-content / local-funding requirement | $1.37 bn (75.7%) |
| Default foreign-turnkey external-capital comparison | $3.26 bn; OSR saves $2.82 bn (86.5%) |
| Lifetime external interest and combined financing saving | $3.47 bn interest; $6.29 bn capital + interest |
| 15%–25% planning risk envelope | $2.08 bn–$2.27 bn |
| Annual OPEX | $42 M / yr |
| Low/high project NPV at 8% | $-866972 k / $-343811 k |
| Low/high project IRR | 1.8% / 5.9% |
| Low/high steady-state DSCR | 0.65 / 1.24 |

Evidence and limitations: [`engineering/finance/summary.json`](engineering/finance/summary.json).

## Simulation validation

The results below are measured `osr-sim` outputs for the scenario hash recorded in the city-local validation file, not timetable or spreadsheet projections.

| Local time | Headway | Operating treatment |
|---|---:|---|
| 05:30–07:00 | 6 min | off-peak depot service enabled |
| 07:00–09:00 | 3 min | peak quick turnaround |
| 09:00–15:00 | 6 min | off-peak depot service enabled |
| 15:00–17:00 | 3 min | peak quick turnaround |
| 17:00–23:30 | 6 min | off-peak depot service enabled |
| 23:30–02:00 | 12 min | off-peak depot service enabled |

| Verified run | Result |
|---|---|
| 2-hour screenshot trace | 6,403.67 train-km; 63,938.74 kWh consumed; 64,593.06 kWh charged; 42 depot services completed; minimum SoC 80%; 0 onboard emergencies; 0 invariant violations |
| Full 05:30–02:00 service plus run-out | 85,448.27 train-km; 853,176.22 kWh consumed; 861,293.31 kWh charged; 1,000 depot services completed (8 active at cutoff); minimum SoC 73%; 0 onboard emergencies; 0 invariant violations; 96.2% of scheduled train-km delivered |

### Mandatory degraded-energy cases

| Case | Minimum SoC | Service delivered / required | Result |
|---|---:|---:|---:|
| 80% end-of-life battery capacity | 66.5% | 96.2% / 90% | pass |
| maximum planning climate/HVAC duty | 27.9% | 96.2% / 90% | pass |
| 50% charging-contact availability | 73.2% | 96.2% / 90% | pass |
| ten-hour all-site grid outage | 20.0% | 64.8% / 60% | pass |
| ten-hour single charging-pad outage | 67.4% | 96.2% / 90% | pass |

**Simulation acceptance:** passed — The full-window run includes 4.5 hours after the 02:00 service close so long ring and charging cycles can finish. Nominal and N-1/degraded screens protect 20% SoC and at least 90% of scheduled train-km. The ten-hour all-site grid outage is an emergency reduced-service case with a 60% floor. Energy-adaptive control may widen off-peak headways; calibrated timetable acceptance remains an operator gate.

Full evidence and provenance: [`engineering/simulation/validation-summary.json`](engineering/simulation/validation-summary.json).

| Simulation dashboard | Network visualizer |
|---|---|
| ![Vijayawada energy and battery simulation dashboard](engineering/screenshots/vijayawada-simulation-dashboard.png) | ![Vijayawada simulator network visualizer](engineering/screenshots/vijayawada-network-visualizer.png) |

## SUMO, QGIS, and energy screening

These are executed city-specific screening runs. They establish model consistency and expose planning findings; they are not a calibrated operational or construction acceptance.

| Package | Current result |
|---|---|
| SUMO | 24/24 screening services arrived; 0 input findings; status `completed` |
| QGIS/GDAL | GeoPackage generated with 6 corridors, 67 line platforms, 10 interchange complexes, 105 civil segments, and 0 input findings |
| pandapower/pvlib | Solver passed; grid-only max transformer loading 81.1%; coordinated-daylight max 30.6%; 0 open screening findings |

Evidence: [`engineering/sumo/summary.json`](engineering/sumo/summary.json), [`engineering/gis/summary.json`](engineering/gis/summary.json), and [`engineering/energy/summary.json`](engineering/energy/summary.json).

| QGIS engineering-layer review | SUMO executed timetable review |
|---|---|
| ![Vijayawada QGIS engineering layers](engineering/screenshots/vijayawada-qgis-engineering-map.png) | ![Vijayawada SUMO timetable validation](engineering/screenshots/vijayawada-sumo-validation.png) |

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`vijayawada.toml`](vijayawada.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`vijayawada-network-map.png`](vijayawada-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`vijayawada.corridor.geojson`](vijayawada.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`vijayawada.stations.json`](vijayawada.stations.json) | Machine-readable station list |
| [`vijayawada.design-quality.yaml`](vijayawada.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |


Run the city regeneration command below to refresh the full engineering and operations bundle in this city folder.

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug vijayawada

# 2. full generated design, scenario, engineering, and operations bundle
scripts/regenerate-city.sh vijayawada
```

The generated design, scenario, engineering, and operations evidence share this canonical city directory.
