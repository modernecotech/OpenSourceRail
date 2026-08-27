# Jeddah — Urban Rail Network

**Country:** SA · **Population:** 4,700,000

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey case, this OSR plan avoids **$5.78 bn (85.4%) of external capital** and **$7.11 bn of external interest**. Capital plus saved interest totals **$12.90 bn over the 40-year financing life**. Both cases use the same 4.5% external rate and financing schedule; the turnkey external requirement is assumed debt-financed, and the benchmark remains an editable sensitivity, not a vendor quote.

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Jeddah rail network on OpenStreetMap](jeddah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`jeddah.corridor.geojson`](jeddah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 127 |
| Interchange-class stations | 19 |
| Multi-line transfer reachability | 44% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 69.3% |
| Route length (double track) | 375.4 km |
| Revenue fleet | 535 × 6-car trainsets |
| Revenue fleet passenger capacity | 385,200 AW2 pax (513,600 AW3 crush) |
| Dedicated depot-service rotation fleet | 0 (off-peak service uses peak-fleet surplus) |
| Spare + cold-reserve | 57 × 6-car trainsets |
| Peak headway | 3 min |
| Station spacing policy | 1.6 km central / 3 km urban / up to 7 km on suburban approaches and the lowest-demand outer fringe |
| City-centre consolidation | Cross-line platforms within the 600 m station-complex envelope are emitted as one interchange |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Turnaround inspection and recharge

During the 07:00–09:00 and 15:00–17:00 peaks, trains make the normal quick terminal turnback: no depot-service hold is inserted, allowing more battery depletion while the 20% dispatch-reserve gate remains mandatory. In the 6- and 12-minute lower-frequency windows, each line's deterministic energy controller may widen the published headway when actual charging delivery leaves a departing set below the 40% normal-service SoC target (up to 3× the published headway). This automatically matches offered off-peak service to available traction energy without buying a separate service-rotation fleet. In those lower-frequency windows, each train receives a **12-minute service slot** at its designated powered service point. This may be a staffed terminal platform or the main depot; only defects and maintenance require a depot move. Interior cleaning, exterior and running-gear walk-around, door/coupler/emergency-equipment checks, fault-log download, and a 150 kW low-C recharge run concurrently. A red defect holds the set for maintenance; a clear inspection returns it to the revenue rotation.

The fleet is sized for the 3-minute peaks; when service relaxes to 6 or 12 minutes, the same peak fleet provides enough idle cover for service-point work. Therefore **0 additional trainsets** are required for depot service; only the existing 48 planned-maintenance spares and 9 cold-reserve sets are included in the rolling-stock, production-plant, maintenance, labour, and total CAPEX/OPEX figures below.

## Distributed overnight stabling

At service close, telemetry-healthy trainsets remain at selected powered passenger stations near their first morning departures. Every occupied station must provide at least 150 kW low-C charging, CCTV, remote traction isolation, protected emergency access, and an OCC-assigned train/track slot. Sets with red defects, overdue heavy maintenance, failed isolation, or failed security return to the main-heavy depot. OCC verifies charge completion and remote self-test before releasing all station-stabled sets together at service start. The generated default therefore builds one maintenance-focused main depot, not a parking depot at every terminus.

Circumferential lines use the same demand-based stop-spacing policy as radials (1.0× the equivalent radial spacing), while every forced radial-transfer platform is retained. Charging-platform dwell is 150 seconds, calculated from one circuit's climate-adjusted energy and the line's aggregate charging power; non-charging halts keep their ordinary dwell.

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 50.2 km | 17 | 93 | S Mid ↔ NW Outer |
| line-2 | 28.7 km | 10 | 51 | S Mid ↔ NW Mid |
| line-3 | 44.4 km | 14 | 81 | N Outer ↔ SE Outer |
| line-4 | 43.6 km | 17 | 86 | N Mid ↔ S Outer |
| line-5 | 37.1 km | 12 | 72 | E Outer ↔ W Mid |
| line-6 | 32.4 km | 12 | 63 | SE Outer ↔ W Inner |
| line-7 | 29.0 km | 9 | 54 | NE Outer ↔ S Inner |
| line-8 | 27.4 km | 10 | 54 | NE Mid ↔ SW Inner |
| line-9 | 82.5 km | 26 | 38 | NW Mid ↔ NW Mid |
| **Total** | **375.4 km** | **127 unique** | **592** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 1,080 kWh usable / 1,350 kWh nameplate per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 385,200 AW2 pax (513,600 AW3 crush) |
| Total fleet capacity | 426,240 AW2 pax (568,320 AW3 crush, incl. service rotation + spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 535 × 720 = **385,200 AW2 passengers** (513,600 AW3 crush)
- **Total fleet passenger capacity:** 592 × 720 = **426,240 AW2 passengers** (568,320 AW3 crush, incl. service rotation + spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 14,400 = **259,200 passengers/hour**
- **Scheduled one-way train journeys:** **3,952/day**
- **Daily theoretical capacity from timetable:** 3,952 scheduled one-way train journeys/day × 720 AW2 pax = **2,845,800 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **2,276,640 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **415.5 – 664.8 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **4,700,000**
- Anchor-weighted coverage: 69.3%
- Catchment population: **≈ 3,257,099** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 38 | 300 kW | 2000 kWh |
| Major | 1 | 300 kW | 2000 kWh |
| Standard | 58 | 300 kW | 2000 kWh |
| Terminal | 15 | 300 kW | 2000 kWh |
| **Total installed** | **113** | **38,600 kW** | **264,000 kWh** |

Aggregate station-rail charging power: **226,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 1,080 kWh usable (1,350 kWh nameplate) battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **727.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Onboard battery adequacy | 4.6× worst inter-charge run | OK: 1,350 kWh nameplate, 270 kWh protected reserve, and 848 kWh usable margin across the worst powered-stop gap (line-4) |
| Lowest traversal charging margin | 172 kWh | line-7 after climate load, 98% conversion, and the required 10% operating margin |
| PV daily yield proxy | 232 MWh/day | 6.0 peak-sun-hour planning proxy before local derates |
| Scheduled one-way train journeys | 3,952 / day | Train departures across both directions and all lines |
| Scheduled train journey-km | 155,381 train-km/day | One-way train journeys × route length |
| Annual service work | 61.3 M train-km/yr | Includes 108% depot/deadhead factor |
| Scheduled traction demand | 4,027 MWh/day | 367.5 M car-km/yr × 4.0 kWh/car-km |
| On-site PV shortfall before solar plant | 3,796 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 727.5 MW / 4,365 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 264 MWh | Distributed LFP buffer for charging peaks and grid outages |

Opportunity charging is checked line by line; ring trains remain in service while receiving the longer planned dwell at every powered platform.

| Line | Powered stops | Climate-adjusted traversal | Delivered per traversal | Required-margin surplus | Worst powered-stop gap |
|---|---:|---:|---:|---:|---:|
| line-1 | 15 | 810 kWh | 1,290 kWh | 399 kWh | 13.3 km / 215 kWh |
| line-2 | 10 | 463 kWh | 719 kWh | 210 kWh | 4.7 km / 75 kWh |
| line-3 | 13 | 716 kWh | 1,094 kWh | 307 kWh | 7.0 km / 113 kWh |
| line-4 | 14 | 704 kWh | 1,176 kWh | 402 kWh | 14.4 km / 232 kWh |
| line-5 | 10 | 598 kWh | 980 kWh | 322 kWh | 11.8 km / 190 kWh |
| line-6 | 10 | 523 kWh | 849 kWh | 274 kWh | 12.0 km / 193 kWh |
| line-7 | 7 | 467 kWh | 686 kWh | 172 kWh | 10.9 km / 176 kWh |
| line-8 | 9 | 442 kWh | 768 kWh | 281 kWh | 7.4 km / 120 kWh |
| line-9 | 25 | 1,330 kWh | 2,042 kWh | 579 kWh | 7.6 km / 123 kWh |

## CAPEX (planning grade)

Base figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Full generated bundles add the scenario-dependent dedicated solar plant and finance reconciliation under `build/`. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields are explicit converted reporting views at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), distributed overnight stabling that reduces depot parking and local commissioning-bay scope, at-grade depots without overhead bridge cranes, **trainset-family rolling-stock units** (for example $900 k per 3-car light-metro trainset, with the raw marketplace BOM retained only as an audit floor), commodity LFP packs + heavy-vehicle PMSM motors + matched commercial traction controllers, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line includes direct material, local assembly/labour, nominal per-train QA/acceptance, and modest local handover logistics. Fixtures, tooling, and production-readiness live in one shared national railway production plant at $60 k per supported vehicle/car module, with $120 k retained as the high sensitivity check. That national asset is excluded from city CAPEX and costed once in the country brief; warranty, spares, and routine commissioning support are OPEX rather than repeated train CAPEX. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

Rates are **design-derived planning targets**, generated from the parametric CAD quantity model and the reviewed benchmark calibration in `lib/templates/civil-cost-calibration.toml`. They are not quotations; foundation-zone schedules and normalized supplier offers remain release gates.

| Bucket | Value |
|---|---|
| At-grade (352.8 km @ $2.58 M/km) | $912 M |
| Elevated (22.6 km @ $9.75 M/km) | $220 M |
| Elevated-interchange premium (19 sites @ $4.50 M) | $86 M |
| **Civil subtotal** | **$1.22 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 14 | $600 k | $8.4 M |
| `standard` | 58 | $2.50 M | $145 M |
| `major` | 1 | $4.50 M | $4.5 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 38 | $12.0 M | $456 M |
| **Stations subtotal** | | | **$686 M** |

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
| `metro-6car` (revenue + service rotation + spare + cold reserve) | 592 | $1.68 M | $995 M |

#### 800 V procurement basis

The following RFC 0021 commodity-component reconciliation is already included in the delivered rolling-stock and charging-site planning units; it is shown for auditability and is not additive.

| Component | Current design basis |
|---|---:|
| Onboard architecture | 800 V-class; 650-700 V nominal traction DC bus |
| Gross traction battery | 225 kWh/car; 24,167 USD/car |
| PMSM motor + controller sets | 2/car @ 10,000 USD/set |
| Core electrical subtotal | 51,000 USD/car; 306,000 USD/trainset |
| Normal 500 kWh / 500 kW station equipment | 65,000 USD; 100,000 USD integrated allowance |

### Shared national railway production plant

This city does **not** carry a separate trainset factory. One national plant supplies every city through a phased production programme, while rails, viaducts, stations, and depots remain city/regional delivery scope. The national plant includes tooling, fixtures, plant services, production-readiness, and commissioning-bay setup. Standard 1 m fiberglass body moulds, dry clips, and compact gauges replace a full-length body mould and adhesive cure hall. It is costed per vehicle/car module, not per trainset, and the factory is sized to the largest single-city fleet programme rather than duplicated for every network. See [`../NATIONAL-BRIEF.md`](../NATIONAL-BRIEF.md).

| City treatment | Indicative modules | National sizing unit | City CAPEX |
|---|---:|---:|---:|
| Fleet demand passed to national production plan | 3552 | $60 k | **$0 k** |
| National high sensitivity (shown for scale, not added here) | 3552 | $120 k | $0 |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 727,541 kW @ $700/kW | $509 M |
| Grid interconnection / PPA tie-in | 727,541 kW @ $100/kW | $73 M |
| Annual generation proxy | 727.5 MW × 6.0 peak-sun-h/day × 365 d/yr | 1,593.3 GWh/yr |
| **Dedicated solar plant subtotal** | | **$582 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 375.4 km × $0.050 M/km | $19 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $50 M |
| EPC integration + project management (7%) | on subtotal | $208 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.22 bn |
| Stations | $686 M |
| Depots | $8.0 M |
| Rolling stock | $995 M |
| Shared national railway production plant (outside city CAPEX) | $0 k |
| Dedicated solar power plant | $582 M |
| Residual train-control wayside + charging microgrids | $68 M |
| EPC overhead (7%) | $208 M |
| **CAPEX total** | **$3.76 bn** |
| Per-route-km | $10 M / km |
| Per-capita (city pop) | $801 / person |


### Procurement origin and foreign-capital exposure

| Bucket | Total | Imported share | Imported / external capital | Local content / local funding |
|---|---:|---:|---:|---:|
| Civil works | $1.22 bn | 15% | $183 M | $1.03 bn |
| Stations | $686 M | 20% | $137 M | $549 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $995 M | 35% | $348 M | $646 M |
| Dedicated solar plant | $582 M | 45% | $262 M | $320 M |
| Residual signalling / train control | $19 M | 50% | $9.4 M | $9.4 M |
| Charging microgrids | $50 M | 40% | $20 M | $30 M |
| EPC / project services | $208 M | 15% | $31 M | $177 M |
| **Total city CAPEX** | **$3.76 bn** | **26.4%** | **$992 M** | **$2.77 bn** |

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

Planning-grade procurement-origin and financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Imported content defines the minimum foreign-currency / international capital requirement; locally supplied content can be financed with domestic-currency bonds, public equity, or other local sources. It is a pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh jeddah`.

### Imported value and construction capital requirement

The localization-first import percentage is calculated bucket by bucket from the controlled procurement-origin assumptions in [`lib/templates/capex-costs.toml`](../../../../lib/templates/capex-costs.toml). It is not a tariff estimate: it identifies the value that must be paid in foreign currency or backed by an international financing source. The shared national trainset factory is outside this city CAPEX and appears once in the country `NATIONAL-BRIEF.md`.

| Capital boundary | Share of city CAPEX | Total requirement | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imported components / machinery** | **26.4%** | **$992 M** | **$198 M / yr** |
| **Local capital for domestic procurement / payroll** | **73.6%** | **$2.77 bn** | **$555 M / yr** |
| of which planned local bond issuance | 58.9% of total CAPEX | $2.22 bn | $444 M / yr |
| **Total city programme** | **100.0%** | **$3.76 bn** | **$753 M / yr** |

### Foreign-company turnkey comparison

This is an editable like-for-like sensitivity, not a vendor quotation. It multiplies OSR CAPEX for an equivalent network, fleet, service, and energy scope, then assumes 90% of the foreign contractor price requires foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price. Lifetime interest uses the same 4.5% rate, 5-year construction interest period, and 35-year amortization for both cases; the comparator external requirement is assumed debt-financed.

| Foreign-turnkey case | Cost multiplier vs OSR | Foreign-company external capital | OSR external capital saved | External interest saved over financing life | Capital + interest saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $5.08 bn | $4.09 bn (80.5%) | $5.03 bn | **$9.12 bn** |
| **Default** | 2.00× | $6.78 bn | $5.78 bn (85.4%) | $7.11 bn | **$12.90 bn** |
| High | 3.00× | $10.17 bn | $9.17 bn (90.2%) | $11.28 bn | **$20.45 bn** |

At the default 2.00× case, OSR's $992 M external requirement is 85.4% below the illustrative foreign-company requirement of $6.78 bn; the associated lifetime external-interest saving is $7.11 bn, and total project CAPEX is 50.0% lower. Replace both variables with normalized bids before an investment decision.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (local public-equity drawdown + interest-only grace on external import finance and local bonds; capital-raising draws are shown above; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$255 M / yr** | $54 |
| Steady-state, low capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$184 M / yr** | $39 |
| Lifecycle envelope (yr 1–40, low scenario) | **$1.28 bn cumulative** | $272 |
| Lifecycle envelope (yr 1–40, high scenario) | **$1.28 bn cumulative** | $272 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$7.71 bn cumulative** | $1,641 |

_Population basis: 4,700,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $184 M / yr → $184 M / yr._

### CAPEX funding sources

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| External climate/MDB debt for imported content (unconfirmed) | 26% | $992 M | 4.5% | 40 y, 5 y grace | $57 M / yr |
| Local-currency sovereign / project bonds for local content | 59% | $2.22 bn | 4.5% | 40 y, 5 y grace | $127 M / yr |
| Local government equity / other domestic funding (no debt service) | 15% | $555 M | — | — | — |
| **Total** | **100%** | **$3.76 bn** | | | **$184 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — external import-finance debt $45 M / yr + local bonds $100 M / yr = **$144 M / yr** total. The base case assumes no climate-development grant. Local public equity is drawn across construction ($111 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

_Loan availability note: this is a finance placeholder, not a committed lender offer. Plausible providers would be a national government borrowing through an MDB or a climate fund accredited entity, such as the World Bank/IBRD, Islamic Development Bank, Climate Investment Funds, or Green Climate Fund channels. Official GCF policy allows grants and concessional loans, and World Bank/CIF material documents below-market climate finance, but this project still needs a lender mandate, eligibility screen, and signed term sheet before the 4.5% / 40-year assumption can be treated as real. Evidence anchors: [GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), [GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), [World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), [CIF funding instruments](https://www.cif.org/cif-funding), and [IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $40 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $38 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $938 k |
| Traction energy (1470.0 GWh / yr) | 155,381 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 84.5 GWh/yr + dedicated solar plant 727.5 MW / 1593.3 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $8.7 M |
| Labour (1,766 FTE) | driverless roster: OCC/remote 316, station/platform 511, passenger service 231, fleet maintenance 382, infrastructure/energy 293, admin/training 33; no train drivers × country median × 12 × engineer-premium 1.4 | $50 M |
| **OPEX subtotal** | | **$138 M / yr** |

_Annual service work: 155,381 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 61.3 M train-km / yr (367.5 M car-km / yr). On-site PV covers 84.5 GWh/yr and the dedicated solar plant adds 1593.3 GWh/yr against 1470.0 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

## Maintenance schedule system

Baseline scheduled work covers 592 trainsets, 127 stations, 375.4 route-km, 9 lines, and 155,381 scheduled train-km/day. Intervals are defined in [`lib/templates/maintenance-schedule.toml`](../../../../lib/templates/maintenance-schedule.toml) and governed by [RFC 0029](../../../../docs/rfcs/0029-maintenance-schedule-system.md).

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

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $4.53 |
| Day pass (3 trips) | $11.56 (15 % bulk discount) |
| Monthly unlimited pass | $136.00 (~8 % of median monthly income) |
| Annual pass | $1496.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (2,276,640 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the external/local CAPEX funding sources, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 2% |
| Annual paid trips | 415.5 M | 664.8 M | 14.9 M |
| Annual paid trips / city resident | 88 | 141 | 3 |
| Farebox revenue | $1.88 bn / yr | $3.01 bn / yr | $68 M / yr |
| Station shop leases | $21 M / yr | $21 M / yr | $21 M / yr |
| Advertising boards | $50 M / yr | $50 M / yr | $50 M / yr |
| **Total revenue** | **$1.95 bn / yr** | **$3.08 bn / yr** | **$138 M / yr** |
| Revenue / OPEX recovery | 1415% | 2233% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Gross repayable-debt service + residual OPEX subsidy | $184 M / yr | $184 M / yr | **$184 M / yr** |
| Operating surplus applied to debt support | -$184 M / yr | -$184 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$184 M / yr** |
| Operating surplus after OPEX (before debt support) | $1.82 bn / yr | $2.95 bn / yr | $0 / yr |

_Commercial-revenue assumptions: 22,080 m² of station shop/kiosk leases at $90/m²/month and 4,080 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The grant-free procurement-origin funding boundary, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $543 M / yr | $869 M / yr | 16 min/trip × $4.90/h value-of-time proxy |
| Avoided road congestion | $120 M / yr | $191 M / yr | 1,496 M - 2,393 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $22 M / yr | $34 M / yr | 269.2–430.8 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $60 M / yr | $96 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $726 M / yr | $1.16 bn / yr | 21% of paid trips × $8.50 local spend proxy |
| Entertainment / community activity supported | $374 M / yr | $599 M / yr | 11% of paid trips × $8.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$1.84 bn / yr** | **$2.95 bn / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 6 education anchors | 63,974 trips/school day; 14.1 M access-events/yr | 102,358 trips/school day; 22.5 M access-events/yr |
| Healthcare | 11 healthcare anchors | 94,594 trips/day; 34.5 M access-events/yr | 151,351 trips/day; 55.2 M access-events/yr |
| Commerce | 55 major/terminal/interchange nodes | 233,893 trips/trading day; 77.2 M access-events/yr | 374,229 trips/trading day; 123.5 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 120,662 trips/activity day; 36.2 M access-events/yr | 193,059 trips/activity day; 57.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $2.77 bn | 74% of $3.76 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $4.44 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $887 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 33,978 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 415.5 M - 664.8 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Financial validation

The machine-readable finance check reconciles the design-base CAPEX with the scenario-dependent solar plant and records deterministic cash-flow sensitivities. It is a planning screen, not financial close.

| Check | Result |
|---|---:|
| Authoritative design-base CAPEX | $3.18 bn |
| Timetable-sized dedicated solar CAPEX | $582 M |
| **Reconciled project CAPEX** | **$3.76 bn** |
| Imported / external-capital requirement | $992 M (26.4%) |
| Local-content / local-funding requirement | $2.77 bn (73.6%) |
| Default foreign-turnkey external-capital comparison | $6.78 bn; OSR saves $5.78 bn (85.4%) |
| Lifetime external interest and combined financing saving | $7.11 bn interest; $12.90 bn capital + interest |
| 15%–25% planning risk envelope | $4.33 bn–$4.71 bn |
| Annual OPEX | $138 M / yr |
| Low/high project NPV at 8% | $11.40 bn / $20.36 bn |
| Low/high project IRR | 27.8% / 37.5% |
| Low/high steady-state DSCR | 9.88 / 16.02 |

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
| 2-hour screenshot trace | 10,628.66 train-km; 171,436.63 kWh consumed; 171,019.02 kWh charged; 49 depot services completed; minimum SoC 75%; 0 onboard emergencies; 0 invariant violations |
| Full 05:30–02:00 service plus run-out | 154,387.55 train-km; 2,490,213.93 kWh consumed; 2,515,850.71 kWh charged; 1,568 depot services completed (9 active at cutoff); minimum SoC 27%; 0 onboard emergencies; 0 invariant violations; 99.4% of scheduled train-km delivered; 2 SoC warnings |

### Mandatory degraded-energy cases

| Case | Minimum SoC | Service delivered / required | Result |
|---|---:|---:|---:|
| 80% end-of-life battery capacity | 20.0% | 99.4% / 90% | pass |
| maximum planning climate/HVAC duty | 20.0% | 99.2% / 90% | pass |
| 50% charging-contact availability | 26.6% | 99.4% / 90% | pass |
| ten-hour all-site grid outage | 20.0% | 74.4% / 60% | pass |
| ten-hour single charging-pad outage | 26.6% | 99.4% / 90% | pass |

**Simulation acceptance:** passed — The full-window run includes 4.5 hours after the 02:00 service close so long ring and charging cycles can finish. Nominal and N-1/degraded screens protect 20% SoC and at least 90% of scheduled train-km. The ten-hour all-site grid outage is an emergency reduced-service case with a 60% floor. Energy-adaptive control may widen off-peak headways; calibrated timetable acceptance remains an operator gate.

Full evidence and provenance: [`engineering/simulation/validation-summary.json`](engineering/simulation/validation-summary.json).

| Simulation dashboard | Network visualizer |
|---|---|
| ![Jeddah energy and battery simulation dashboard](engineering/screenshots/jeddah-simulation-dashboard.png) | ![Jeddah simulator network visualizer](engineering/screenshots/jeddah-network-visualizer.png) |

## SUMO, QGIS, and energy screening

These are executed city-specific screening runs. They establish model consistency and expose planning findings; they are not a calibrated operational or construction acceptance.

| Package | Current result |
|---|---|
| SUMO | 36/36 screening services arrived; 0 input findings; status `completed` |
| QGIS/GDAL | GeoPackage generated with 9 corridors, 127 line platforms, 19 interchange complexes, 53 civil segments, and 0 input findings |
| pandapower/pvlib | Solver passed; grid-only max transformer loading 81.1%; coordinated-daylight max 33.0%; 0 open screening findings |

Evidence: [`engineering/sumo/summary.json`](engineering/sumo/summary.json), [`engineering/gis/summary.json`](engineering/gis/summary.json), and [`engineering/energy/summary.json`](engineering/energy/summary.json).

| QGIS engineering-layer review | SUMO executed timetable review |
|---|---|
| ![Jeddah QGIS engineering layers](engineering/screenshots/jeddah-qgis-engineering-map.png) | ![Jeddah SUMO timetable validation](engineering/screenshots/jeddah-sumo-validation.png) |

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`jeddah.toml`](jeddah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`jeddah-network-map.png`](jeddah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`jeddah.corridor.geojson`](jeddah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`jeddah.stations.json`](jeddah.stations.json) | Machine-readable station list |
| [`jeddah.design-quality.yaml`](jeddah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |


Run the city regeneration command below to refresh the full engineering and operations bundle in this city folder.

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug jeddah

# 2. full generated design, scenario, engineering, and operations bundle
scripts/regenerate-city.sh jeddah
```

The generated design, scenario, engineering, and operations evidence share this canonical city directory.
