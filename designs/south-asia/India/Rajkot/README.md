# Rajkot — Urban Rail Network

**Country:** IN · **Population:** 1,800,000

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey case, this OSR plan avoids **$1.80 bn (87.2%) of external capital** and **$2.21 bn of external interest**. Capital plus saved interest totals **$4.00 bn over the 40-year financing life**. Both cases use the same 4.5% external rate and financing schedule; the turnkey external requirement is assumed debt-financed, and the benchmark remains an editable sensitivity, not a vendor quote.

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Rajkot rail network on OpenStreetMap](rajkot-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`rajkot.corridor.geojson`](rajkot.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 47 |
| Interchange-class stations | 6 |
| Multi-line transfer reachability | 100% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 81.7% |
| Route length (double track) | 133.9 km |
| Revenue fleet | 145 × 4-car trainsets |
| Revenue fleet passenger capacity | 69,600 AW2 pax (92,800 AW3 crush) |
| Dedicated depot-service rotation fleet | 0 (off-peak service uses peak-fleet surplus) |
| Spare + cold-reserve | 17 × 4-car trainsets |
| Peak headway | 3 min |
| Station spacing policy | 1.6 km central / 3 km urban / up to 7 km on suburban approaches and the lowest-demand outer fringe |
| City-centre consolidation | Cross-line platforms within the 600 m station-complex envelope are emitted as one interchange |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Turnaround inspection and recharge

During the 07:00–09:00 and 15:00–17:00 peaks, trains make the normal quick terminal turnback: no depot-service hold is inserted, allowing more battery depletion while the 20% dispatch-reserve gate remains mandatory. In the 6- and 12-minute lower-frequency windows, each line's deterministic energy controller may widen the published headway when actual charging delivery leaves a departing set below the 40% normal-service SoC target (up to 3× the published headway). This automatically matches offered off-peak service to available traction energy without buying a separate service-rotation fleet. In those lower-frequency windows, each train receives a **12-minute service slot** at its designated powered service point. This may be a staffed terminal platform or the main depot; only defects and maintenance require a depot move. Interior cleaning, exterior and running-gear walk-around, door/coupler/emergency-equipment checks, fault-log download, and a 150 kW low-C recharge run concurrently. A red defect holds the set for maintenance; a clear inspection returns it to the revenue rotation.

The fleet is sized for the 3-minute peaks; when service relaxes to 6 or 12 minutes, the same peak fleet provides enough idle cover for service-point work. Therefore **0 additional trainsets** are required for depot service; only the existing 12 planned-maintenance spares and 5 cold-reserve sets are included in the rolling-stock, production-plant, maintenance, labour, and total CAPEX/OPEX figures below.

## Distributed overnight stabling

At service close, telemetry-healthy trainsets remain at selected powered passenger stations near their first morning departures. Every occupied station must provide at least 150 kW low-C charging, CCTV, remote traction isolation, protected emergency access, and an OCC-assigned train/track slot. Sets with red defects, overdue heavy maintenance, failed isolation, or failed security return to the main-heavy depot. OCC verifies charge completion and remote self-test before releasing all station-stabled sets together at service start. The generated default therefore builds one maintenance-focused main depot, not a parking depot at every terminus.

Circumferential lines use the same demand-based stop-spacing policy as radials (1.0× the equivalent radial spacing), while every forced radial-transfer platform is retained. Charging-platform dwell is 300 seconds, calculated from one circuit's climate-adjusted energy and the line's aggregate charging power; non-charging halts keep their ordinary dwell.

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 25.4 km | 10 | 43 | NE Outer ↔ S Mid |
| line-2 | 14.5 km | 7 | 28 | E Mid ↔ SW Mid |
| line-3 | 14.8 km | 6 | 27 | SE Mid ↔ NW Inner |
| line-4 | 23.7 km | 8 | 40 | W Mid ↔ SE Outer |
| line-5 | 55.4 km | 16 | 24 | NW Outer ↔ NW Outer |
| **Total** | **133.9 km** | **47 unique** | **162** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 720 kWh usable / 900 kWh nameplate per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 69,600 AW2 pax (92,800 AW3 crush) |
| Total fleet capacity | 77,760 AW2 pax (103,680 AW3 crush, incl. service rotation + spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 145 × 480 = **69,600 AW2 passengers** (92,800 AW3 crush)
- **Total fleet passenger capacity:** 162 × 480 = **77,760 AW2 passengers** (103,680 AW3 crush, incl. service rotation + spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 9,600 = **96,000 passengers/hour**
- **Scheduled one-way train journeys:** **2,092/day**
- **Daily theoretical capacity from timetable:** 2,092 scheduled one-way train journeys/day × 480 AW2 pax = **1,004,400 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **803,520 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **146.6 – 234.6 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **1,800,000**
- Anchor-weighted coverage: 81.7%
- Catchment population: **≈ 1,470,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 17 | 300 kW | 1500 kWh |
| Standard | 12 | 300 kW | 1500 kWh |
| Terminal | 7 | 300 kW | 1500 kWh |
| **Total installed** | **37** | **15,800 kW** | **94,000 kWh** |

Aggregate station-rail charging power: **55,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh usable (900 kWh nameplate) battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **145.3 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Onboard battery adequacy | 1.9× worst inter-charge run | OK: 900 kWh nameplate, 180 kWh protected reserve, and 334 kWh usable margin across the worst powered-stop gap (line-5) |
| Lowest traversal charging margin | 168 kWh | line-3 after climate load, 98% conversion, and the required 10% operating margin |
| PV daily yield proxy | 95 MWh/day | 6.0 peak-sun-hour planning proxy before local derates |
| Scheduled one-way train journeys | 2,092 / day | Train departures across both directions and all lines |
| Scheduled train journey-km | 49,364 train-km/day | One-way train journeys × route length |
| Annual service work | 19.5 M train-km/yr | Includes 108% depot/deadhead factor |
| Scheduled traction demand | 853 MWh/day | 77.8 M car-km/yr × 4.0 kWh/car-km |
| On-site PV shortfall before solar plant | 758 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 145.3 MW / 872 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 94 MWh | Distributed LFP buffer for charging peaks and grid outages |

Opportunity charging is checked line by line; ring trains remain in service while receiving the longer planned dwell at every powered platform.

| Line | Powered stops | Climate-adjusted traversal | Delivered per traversal | Required-margin surplus | Worst powered-stop gap |
|---|---:|---:|---:|---:|---:|
| line-1 | 10 | 273 kWh | 564 kWh | 263 kWh | 4.9 km / 53 kWh |
| line-2 | 7 | 156 kWh | 392 kWh | 220 kWh | 3.1 km / 33 kWh |
| line-3 | 6 | 160 kWh | 343 kWh | 168 kWh | 3.5 km / 38 kWh |
| line-4 | 7 | 255 kWh | 453 kWh | 173 kWh | 7.2 km / 78 kWh |
| line-5 | 7 | 596 kWh | 858 kWh | 202 kWh | 35.9 km / 386 kWh |

## CAPEX (planning grade)

Base figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Full generated bundles add the scenario-dependent dedicated solar plant and finance reconciliation under `build/`. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields are explicit converted reporting views at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), distributed overnight stabling that reduces depot parking and local commissioning-bay scope, at-grade depots without overhead bridge cranes, **trainset-family rolling-stock units** (for example $900 k per 3-car light-metro trainset, with the raw marketplace BOM retained only as an audit floor), commodity LFP packs + heavy-vehicle PMSM motors + matched commercial traction controllers, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line includes direct material, local assembly/labour, nominal per-train QA/acceptance, and modest local handover logistics. Fixtures, tooling, and production-readiness live in one shared national railway production plant at $60 k per supported vehicle/car module, with $120 k retained as the high sensitivity check. That national asset is excluded from city CAPEX and costed once in the country brief; warranty, spares, and routine commissioning support are OPEX rather than repeated train CAPEX. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

Rates are **design-derived planning targets**, generated from the parametric CAD quantity model and the reviewed benchmark calibration in `lib/templates/civil-cost-calibration.toml`. They are not quotations; foundation-zone schedules and normalized supplier offers remain release gates.

| Bucket | Value |
|---|---|
| At-grade (117.9 km @ $2.58 M/km) | $305 M |
| Elevated (15.9 km @ $9.75 M/km) | $155 M |
| Elevated-interchange premium (5 sites @ $4.50 M) | $22 M |
| **Civil subtotal** | **$483 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 10 | $600 k | $6.0 M |
| `standard` | 12 | $2.50 M | $30 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
| `interchange-elevated` | 15 | $12.0 M | $180 M |
| **Stations subtotal** | | | **$268 M** |

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
| `metro-4car` (revenue + service rotation + spare + cold reserve) | 162 | $1.12 M | $181 M |

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
| Fleet demand passed to national production plan | 648 | $60 k | **$0 k** |
| National high sensitivity (shown for scale, not added here) | 648 | $120 k | $0 |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 145,324 kW @ $700/kW | $102 M |
| Grid interconnection / PPA tie-in | 145,324 kW @ $100/kW | $15 M |
| Annual generation proxy | 145.3 MW × 6.0 peak-sun-h/day × 365 d/yr | 318.3 GWh/yr |
| **Dedicated solar plant subtotal** | | **$116 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 133.9 km × $0.050 M/km | $6.7 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $13 M |
| EPC integration + project management (7%) | on subtotal | $67 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $483 M |
| Stations | $268 M |
| Depots | $8.0 M |
| Rolling stock | $181 M |
| Shared national railway production plant (outside city CAPEX) | $0 k |
| Dedicated solar power plant | $116 M |
| Residual train-control wayside + charging microgrids | $19 M |
| EPC overhead (7%) | $67 M |
| **CAPEX total** | **$1.14 bn** |
| Per-route-km | $8.5 M / km |
| Per-capita (city pop) | $635 / person |


### Procurement origin and foreign-capital exposure

| Bucket | Total | Imported share | Imported / external capital | Local content / local funding |
|---|---:|---:|---:|---:|
| Civil works | $483 M | 15% | $72 M | $410 M |
| Stations | $268 M | 20% | $54 M | $215 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $181 M | 35% | $64 M | $118 M |
| Dedicated solar plant | $116 M | 45% | $52 M | $64 M |
| Residual signalling / train control | $6.7 M | 50% | $3.3 M | $3.3 M |
| Charging microgrids | $13 M | 40% | $5.1 M | $7.6 M |
| EPC / project services | $67 M | 15% | $10 M | $57 M |
| **Total city CAPEX** | **$1.14 bn** | **23.0%** | **$262 M** | **$881 M** |

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

Planning-grade procurement-origin and financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Imported content defines the minimum foreign-currency / international capital requirement; locally supplied content can be financed with domestic-currency bonds, public equity, or other local sources. It is a pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh rajkot`.

### Imported value and construction capital requirement

The localization-first import percentage is calculated bucket by bucket from the controlled procurement-origin assumptions in [`lib/templates/capex-costs.toml`](../../../../lib/templates/capex-costs.toml). It is not a tariff estimate: it identifies the value that must be paid in foreign currency or backed by an international financing source. The shared national trainset factory is outside this city CAPEX and appears once in the country `NATIONAL-BRIEF.md`.

| Capital boundary | Share of city CAPEX | Total requirement | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imported components / machinery** | **23.0%** | **$262 M** | **$52 M / yr** |
| **Local capital for domestic procurement / payroll** | **77.0%** | **$881 M** | **$176 M / yr** |
| of which planned local bond issuance | 61.6% of total CAPEX | $705 M | $141 M / yr |
| **Total city programme** | **100.0%** | **$1.14 bn** | **$229 M / yr** |

### Foreign-company turnkey comparison

This is an editable like-for-like sensitivity, not a vendor quotation. It multiplies OSR CAPEX for an equivalent network, fleet, service, and energy scope, then assumes 90% of the foreign contractor price requires foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price. Lifetime interest uses the same 4.5% rate, 5-year construction interest period, and 35-year amortization for both cases; the comparator external requirement is assumed debt-financed.

| Foreign-turnkey case | Cost multiplier vs OSR | Foreign-company external capital | OSR external capital saved | External interest saved over financing life | Capital + interest saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $1.54 bn | $1.28 bn (83.0%) | $1.58 bn | **$2.86 bn** |
| **Default** | 2.00× | $2.06 bn | $1.80 bn (87.2%) | $2.21 bn | **$4.00 bn** |
| High | 3.00× | $3.09 bn | $2.82 bn (91.5%) | $3.47 bn | **$6.30 bn** |

At the default 2.00× case, OSR's $262 M external requirement is 87.2% below the illustrative foreign-company requirement of $2.06 bn; the associated lifetime external-interest saving is $2.21 bn, and total project CAPEX is 50.0% lower. Replace both variables with normalized bids before an investment decision.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (local public-equity drawdown + interest-only grace on external import finance and local bonds; capital-raising draws are shown above; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$98 M / yr** | $54 |
| Steady-state, low capacity-use (year 6+) | **$3.4 M / yr** | $2 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$71 M / yr** | $39 |
| Lifecycle envelope (yr 1–40, low scenario) | **$608 M cumulative** | $338 |
| Lifecycle envelope (yr 1–40, high scenario) | **$489 M cumulative** | $272 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.96 bn cumulative** | $1,645 |

_Population basis: 1,800,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $67 M / yr → $71 M / yr._

### CAPEX funding sources

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| External climate/MDB debt for imported content (unconfirmed) | 23% | $262 M | 4.5% | 40 y, 5 y grace | $15 M / yr |
| Local-currency sovereign / project bonds for local content | 62% | $705 M | 7.2% | 40 y, 5 y grace | $56 M / yr |
| Local government equity / other domestic funding (no debt service) | 15% | $176 M | — | — | — |
| **Total** | **100%** | **$1.14 bn** | | | **$71 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — external import-finance debt $12 M / yr + local bonds $51 M / yr = **$63 M / yr** total. The base case assumes no climate-development grant. Local public equity is drawn across construction ($35 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

_Loan availability note: this is a finance placeholder, not a committed lender offer. Plausible providers would be a national government borrowing through an MDB or a climate fund accredited entity, such as the World Bank/IBRD, Islamic Development Bank, Climate Investment Funds, or Green Climate Fund channels. Official GCF policy allows grants and concessional loans, and World Bank/CIF material documents below-market climate finance, but this project still needs a lender mandate, eligibility screen, and signed term sheet before the 4.5% / 40-year assumption can be treated as real. Evidence anchors: [GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), [GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), [World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), [CIF funding instruments](https://www.cif.org/cif-funding), and [IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $7.3 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $15 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $335 k |
| Traction energy (311.3 GWh / yr) | 49,364 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 34.6 GWh/yr + dedicated solar plant 145.3 MW / 318.3 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $1.7 M |
| Labour (652 FTE) | driverless roster: OCC/remote 106, station/platform 207, passenger service 92, fleet maintenance 114, infrastructure/energy 108, admin/training 25; no train drivers × country median × 12 × engineer-premium 1.4 | $2.5 M |
| **OPEX subtotal** | | **$27 M / yr** |

_Annual service work: 49,364 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 19.5 M train-km / yr (77.8 M car-km / yr). On-site PV covers 34.6 GWh/yr and the dedicated solar plant adds 318.3 GWh/yr against 311.3 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

## Maintenance schedule system

Baseline scheduled work covers 162 trainsets, 47 stations, 133.9 route-km, 5 lines, and 49,364 scheduled train-km/day. Intervals are defined in [`lib/templates/maintenance-schedule.toml`](../../../../lib/templates/maintenance-schedule.toml) and governed by [RFC 0029](../../../../docs/rfcs/0029-maintenance-schedule-system.md).

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

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (803,520 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the external/local CAPEX funding sources, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 13% |
| Annual paid trips | 146.6 M | 234.6 M | 37.0 M |
| Annual paid trips / city resident | 81 | 130 | 21 |
| Farebox revenue | $90 M / yr | $144 M / yr | $23 M / yr |
| Station shop leases | $1.7 M / yr | $1.7 M / yr | $1.7 M / yr |
| Advertising boards | $2.6 M / yr | $2.6 M / yr | $2.6 M / yr |
| **Total revenue** | **$94 M / yr** | **$148 M / yr** | **$27 M / yr** |
| Revenue / OPEX recovery | 349% | 548% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $71 M / yr | $71 M / yr | **$71 M / yr** |
| Operating surplus applied to debt support | -$67 M / yr | -$71 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $3.4 M / yr | $0 k / yr | **$71 M / yr** |
| Operating surplus after OPEX (before debt support) | $67 M / yr | $121 M / yr | $0 / yr |

_Commercial-revenue assumptions: 8,840 m² of station shop/kiosk leases at $18/m²/month and 1,612 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-free procurement-origin funding boundary, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $26 M / yr | $42 M / yr | 16 min/trip × $0.66/h value-of-time proxy |
| Avoided road congestion | $42 M / yr | $68 M / yr | 528 M - 845 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $7.6 M / yr | $12 M / yr | 95.0–152.0 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $21 M / yr | $34 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $47 M / yr | $76 M / yr | 22% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $23 M / yr | $37 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$168 M / yr** | **$268 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 5 education anchors | 25,110 trips/school day; 5.5 M access-events/yr | 40,176 trips/school day; 8.8 M access-events/yr |
| Healthcare | 14 healthcare anchors | 43,792 trips/day; 16.0 M access-events/yr | 70,067 trips/day; 25.6 M access-events/yr |
| Commerce | 25 major/terminal/interchange nodes | 86,720 trips/trading day; 28.6 M access-events/yr | 138,753 trips/trading day; 45.8 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 42,587 trips/activity day; 12.8 M access-events/yr | 68,138 trips/activity day; 20.4 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $881 M | 77% of $1.14 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $1.41 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $282 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 79,801 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 146.6 M - 234.6 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Financial validation

The machine-readable finance check reconciles the design-base CAPEX with the scenario-dependent solar plant and records deterministic cash-flow sensitivities. It is a planning screen, not financial close.

| Check | Result |
|---|---:|
| Authoritative design-base CAPEX | $1.03 bn |
| Timetable-sized dedicated solar CAPEX | $116 M |
| **Reconciled project CAPEX** | **$1.14 bn** |
| Imported / external-capital requirement | $262 M (23.0%) |
| Local-content / local-funding requirement | $881 M (77.0%) |
| Default foreign-turnkey external-capital comparison | $2.06 bn; OSR saves $1.80 bn (87.2%) |
| Lifetime external interest and combined financing saving | $2.21 bn interest; $4.00 bn capital + interest |
| 15%–25% planning risk envelope | $1.31 bn–$1.43 bn |
| Annual OPEX | $27 M / yr |
| Low/high project NPV at 8% | $-379507 k / $49 M |
| Low/high project IRR | 4.1% / 8.4% |
| Low/high steady-state DSCR | 0.95 / 1.72 |

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
| 2-hour screenshot trace | 3,926.05 train-km; 42,217.21 kWh consumed; 41,962.53 kWh charged; 52 depot services completed; minimum SoC 57%; 0 onboard emergencies; 0 invariant violations |
| Full 05:30–02:00 service plus run-out | 49,361.92 train-km; 530,793.63 kWh consumed; 531,772.62 kWh charged; 816 depot services completed (9 active at cutoff); minimum SoC 32%; 0 onboard emergencies; 0 invariant violations; 100.0% of scheduled train-km delivered |

### Mandatory degraded-energy cases

| Case | Minimum SoC | Service delivered / required | Result |
|---|---:|---:|---:|
| 80% end-of-life battery capacity | 20.1% | 99.8% / 90% | pass |
| maximum planning climate/HVAC duty | 20.1% | 98.4% / 90% | pass |
| 50% charging-contact availability | 32.1% | 100.0% / 90% | pass |
| ten-hour all-site grid outage | 20.0% | 70.2% / 60% | pass |
| ten-hour single charging-pad outage | 32.1% | 100.0% / 90% | pass |

**Simulation acceptance:** passed — The full-window run includes 4.5 hours after the 02:00 service close so long ring and charging cycles can finish. Nominal and N-1/degraded screens protect 20% SoC and at least 90% of scheduled train-km. The ten-hour all-site grid outage is an emergency reduced-service case with a 60% floor. Energy-adaptive control may widen off-peak headways; calibrated timetable acceptance remains an operator gate.

Full evidence and provenance: [`engineering/simulation/validation-summary.json`](engineering/simulation/validation-summary.json).

| Simulation dashboard | Network visualizer |
|---|---|
| ![Rajkot energy and battery simulation dashboard](engineering/screenshots/rajkot-simulation-dashboard.png) | ![Rajkot simulator network visualizer](engineering/screenshots/rajkot-network-visualizer.png) |

## SUMO, QGIS, and energy screening

These are executed city-specific screening runs. They establish model consistency and expose planning findings; they are not a calibrated operational or construction acceptance.

| Package | Current result |
|---|---|
| SUMO | 20/20 screening services arrived; 0 input findings; status `completed` |
| QGIS/GDAL | GeoPackage generated with 5 corridors, 47 line platforms, 6 interchange complexes, 32 civil segments, and 0 input findings |
| pandapower/pvlib | Solver passed; grid-only max transformer loading 81.1%; coordinated-daylight max 30.6%; 0 open screening findings |

Evidence: [`engineering/sumo/summary.json`](engineering/sumo/summary.json), [`engineering/gis/summary.json`](engineering/gis/summary.json), and [`engineering/energy/summary.json`](engineering/energy/summary.json).

| QGIS engineering-layer review | SUMO executed timetable review |
|---|---|
| ![Rajkot QGIS engineering layers](engineering/screenshots/rajkot-qgis-engineering-map.png) | ![Rajkot SUMO timetable validation](engineering/screenshots/rajkot-sumo-validation.png) |

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`rajkot.toml`](rajkot.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`rajkot-network-map.png`](rajkot-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`rajkot.corridor.geojson`](rajkot.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`rajkot.stations.json`](rajkot.stations.json) | Machine-readable station list |
| [`rajkot.design-quality.yaml`](rajkot.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |


Run the city regeneration command below to refresh the full engineering and operations bundle in this city folder.

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug rajkot

# 2. full generated design, scenario, engineering, and operations bundle
scripts/regenerate-city.sh rajkot
```

The generated design, scenario, engineering, and operations evidence share this canonical city directory.
