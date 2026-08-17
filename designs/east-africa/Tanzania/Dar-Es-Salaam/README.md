# Dar-Es-Salaam — Urban Rail Network

**Country:** TZ · **Population:** 7,404,689

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Dar-Es-Salaam rail network on OpenStreetMap](dar-es-salaam-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 132 |
| Interchange-class stations | 18 |
| Multi-line transfer reachability | 56% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.8% |
| Route length (double track) | 443.7 km |
| Revenue fleet | 640 × 6-car trainsets |
| Revenue fleet passenger capacity | 460,800 AW2 pax (614,400 AW3 crush) |
| Dedicated depot-service rotation fleet | 0 (off-peak service uses peak-fleet surplus) |
| Spare + cold-reserve | 69 × 6-car trainsets |
| Peak headway | 3 min |
| Station spacing policy | 1.6 km central / 3 km urban / up to 7 km on suburban approaches and the lowest-demand outer fringe |
| City-centre consolidation | Cross-line platforms within the 600 m station-complex envelope are emitted as one interchange |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Turnaround inspection and recharge

During the 07:00–09:00 and 15:00–17:00 peaks, trains make the normal quick terminal turnback: no depot-service hold is inserted, allowing more battery depletion while the 20% dispatch-reserve gate remains mandatory. In the 6- and 12-minute lower-frequency windows, each line's deterministic energy controller may widen the published headway when actual charging delivery leaves a departing set below the 40% normal-service SoC target (up to 3× the published headway). This automatically matches offered off-peak service to available traction energy without buying a separate service-rotation fleet. In those lower-frequency windows, each train receives a **12-minute service slot** at its designated powered service point. This may be a staffed terminal platform or the main depot; only defects and maintenance require a depot move. Interior cleaning, exterior and running-gear walk-around, door/coupler/emergency-equipment checks, fault-log download, and a 150 kW low-C recharge run concurrently. A red defect holds the set for maintenance; a clear inspection returns it to the revenue rotation.

The fleet is sized for the 3-minute peaks; when service relaxes to 6 or 12 minutes, the same peak fleet provides enough idle cover for service-point work. Therefore **0 additional trainsets** are required for depot service; only the existing 60 planned-maintenance spares and 9 cold-reserve sets are included in the rolling-stock, production-plant, maintenance, labour, and total CAPEX/OPEX figures below.

## Distributed overnight stabling

At service close, telemetry-healthy trainsets remain at selected powered passenger stations near their first morning departures. Every occupied station must provide at least 150 kW low-C charging, CCTV, remote traction isolation, protected emergency access, and an OCC-assigned train/track slot. Sets with red defects, overdue heavy maintenance, failed isolation, or failed security return to the main-heavy depot. OCC verifies charge completion and remote self-test before releasing all station-stabled sets together at service start. The generated default therefore builds one maintenance-focused main depot, not a parking depot at every terminus.

Circumferential lines use the same demand-based stop-spacing policy as radials (1.0× the equivalent radial spacing), while every forced radial-transfer platform is retained. Charging-platform dwell is 180 seconds, calculated from one circuit's climate-adjusted energy and the line's aggregate charging power; non-charging halts keep their ordinary dwell.

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 55.0 km | 16 | 102 | S Outer ↔ N Mid |
| line-2 | 59.0 km | 18 | 108 | SE Mid ↔ NW Outer |
| line-3 | 49.0 km | 15 | 95 | W Inner ↔ SE Outer |
| line-4 | 48.0 km | 13 | 85 | N Mid ↔ S Mid |
| line-5 | 35.9 km | 13 | 69 | S Mid ↔ NE Inner |
| line-6 | 39.5 km | 12 | 74 | NW Outer ↔ S Inner |
| line-7 | 34.2 km | 11 | 67 | NE Inner ↔ W Mid |
| line-8 | 37.4 km | 11 | 69 | NE Inner ↔ SW Mid |
| line-9 | 85.6 km | 23 | 40 | NW Inner ↔ W Mid |
| **Total** | **443.7 km** | **132 unique** | **709** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 1,080 kWh usable / 1,350 kWh nameplate per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 460,800 AW2 pax (614,400 AW3 crush) |
| Total fleet capacity | 510,480 AW2 pax (680,640 AW3 crush, incl. service rotation + spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 640 × 720 = **460,800 AW2 passengers** (614,400 AW3 crush)
- **Total fleet passenger capacity:** 709 × 720 = **510,480 AW2 passengers** (680,640 AW3 crush, incl. service rotation + spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 14,400 = **259,200 passengers/hour**
- **Scheduled one-way train journeys:** **3,952/day**
- **Daily theoretical capacity from timetable:** 3,952 scheduled one-way train journeys/day × 720 AW2 pax = **2,845,800 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **2,276,640 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **415.5 – 664.8 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **7,404,689**
- Anchor-weighted coverage: 56.8%
- Catchment population: **≈ 4,205,863** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 41 | 300 kW | 2000 kWh |
| Major | 3 | 300 kW | 2000 kWh |
| Standard | 50 | 300 kW | 2000 kWh |
| Terminal | 15 | 300 kW | 2000 kWh |
| **Total installed** | **110** | **37,700 kW** | **258,000 kWh** |

Aggregate station-rail charging power: **220,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 1,080 kWh usable (1,350 kWh nameplate) battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,114.3 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Onboard battery adequacy | 3.3× worst inter-charge run | OK: 1,350 kWh nameplate, 270 kWh protected reserve, and 753 kWh usable margin across the worst powered-stop gap (line-3) |
| Lowest traversal charging margin | 263 kWh | line-6 after climate load, 98% conversion, and the required 10% operating margin |
| PV daily yield proxy | 181 MWh/day | 4.8 peak-sun-hour planning proxy before local derates |
| Scheduled one-way train journeys | 3,952 / day | Train departures across both directions and all lines |
| Scheduled train journey-km | 186,424 train-km/day | One-way train journeys × route length |
| Annual service work | 73.5 M train-km/yr | Includes 108% depot/deadhead factor |
| Scheduled traction demand | 4,832 MWh/day | 440.9 M car-km/yr × 4.0 kWh/car-km |
| On-site PV shortfall before solar plant | 4,651 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,114.3 MW / 5,349 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 258 MWh | Distributed LFP buffer for charging peaks and grid outages |

Opportunity charging is checked line by line; ring trains remain in service while receiving the longer planned dwell at every powered platform.

| Line | Powered stops | Climate-adjusted traversal | Delivered per traversal | Required-margin surplus | Worst powered-stop gap |
|---|---:|---:|---:|---:|---:|
| line-1 | 14 | 823 kWh | 1,372 kWh | 467 kWh | 14.5 km / 218 kWh |
| line-2 | 14 | 883 kWh | 1,405 kWh | 433 kWh | 15.9 km / 237 kWh |
| line-3 | 11 | 734 kWh | 1,258 kWh | 450 kWh | 21.8 km / 327 kWh |
| line-4 | 11 | 719 kWh | 1,078 kWh | 287 kWh | 14.2 km / 213 kWh |
| line-5 | 11 | 538 kWh | 931 kWh | 339 kWh | 9.6 km / 143 kWh |
| line-6 | 8 | 592 kWh | 915 kWh | 263 kWh | 20.6 km / 309 kWh |
| line-7 | 9 | 513 kWh | 882 kWh | 318 kWh | 10.0 km / 150 kWh |
| line-8 | 9 | 560 kWh | 882 kWh | 266 kWh | 15.7 km / 235 kWh |
| line-9 | 23 | 1,283 kWh | 2,254 kWh | 843 kWh | 7.4 km / 111 kWh |

## CAPEX (planning grade)

Base figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Full generated bundles add the scenario-dependent dedicated solar plant and finance reconciliation under `build/`. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields are explicit converted reporting views at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), distributed overnight stabling that reduces depot parking and local commissioning-bay scope, at-grade depots without overhead bridge cranes, **trainset-family rolling-stock units** (for example $900 k per 3-car light-metro trainset, with the raw marketplace BOM retained only as an audit floor), commodity LFP packs + heavy-vehicle PMSM motors + matched commercial traction controllers, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line includes direct material, local assembly/labour, nominal per-train QA/acceptance, and modest local handover logistics. Fixtures, tooling, and production-readiness live in one shared national railway production plant at $60 k per supported vehicle/car module, with $120 k retained as the high sensitivity check. That national asset is excluded from city CAPEX and costed once in the country brief; warranty, spares, and routine commissioning support are OPEX rather than repeated train CAPEX. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (401.0 km @ $3.0 M/km) | $1.20 bn |
| Elevated (42.8 km @ $12.0 M/km) | $513 M |
| Elevated-interchange premium (15 sites @ $4.50 M) | $68 M |
| **Civil subtotal** | **$1.78 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 22 | $600 k | $13 M |
| `standard` | 50 | $2.50 M | $125 M |
| `major` | 3 | $4.50 M | $14 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 6 | $8.0 M | $48 M |
| `interchange-elevated` | 35 | $12.0 M | $420 M |
| **Stations subtotal** | | | **$692 M** |

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
| `metro-6car` (revenue + service rotation + spare + cold reserve) | 709 | $1.68 M | $1.19 bn |

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
| Fleet demand passed to national production plan | 4254 | $60 k | **$0 k** |
| National high sensitivity (shown for scale, not added here) | 4254 | $120 k | $0 |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,114,336 kW @ $700/kW | $780 M |
| Grid interconnection / PPA tie-in | 1,114,336 kW @ $100/kW | $111 M |
| Annual generation proxy | 1,114.3 MW × 4.8 peak-sun-h/day × 365 d/yr | 1,952.3 GWh/yr |
| **Dedicated solar plant subtotal** | | **$891 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 443.7 km × $0.050 M/km | $22 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $48 M |
| EPC integration + project management (7%) | on subtotal | $262 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.78 bn |
| Stations | $692 M |
| Depots | $8.0 M |
| Rolling stock | $1.19 bn |
| Shared national railway production plant (outside city CAPEX) | $0 k |
| Dedicated solar power plant | $891 M |
| Residual train-control wayside + charging microgrids | $70 M |
| EPC overhead (7%) | $262 M |
| **CAPEX total** | **$4.90 bn** |
| Per-route-km | $11 M / km |
| Per-capita (city pop) | $662 / person |


### Procurement origin and foreign-capital exposure

| Bucket | Total | Imported share | Imported / external capital | Local content / local funding |
|---|---:|---:|---:|---:|
| Civil works | $1.78 bn | 15% | $268 M | $1.52 bn |
| Stations | $692 M | 20% | $138 M | $554 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $1.19 bn | 35% | $417 M | $774 M |
| Dedicated solar plant | $891 M | 45% | $401 M | $490 M |
| Residual signalling / train control | $22 M | 50% | $11 M | $11 M |
| Charging microgrids | $48 M | 40% | $19 M | $29 M |
| EPC / project services | $262 M | 15% | $39 M | $223 M |
| **Total city CAPEX** | **$4.90 bn** | **26.4%** | **$1.30 bn** | **$3.60 bn** |

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

Planning-grade procurement-origin and financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Imported content defines the minimum foreign-currency / international capital requirement; locally supplied content can be financed with domestic-currency bonds, public equity, or other local sources. It is a pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh dar-es-salaam`.

### Imported value and construction capital requirement

The localization-first import percentage is calculated bucket by bucket from the controlled procurement-origin assumptions in [`lib/templates/capex-costs.toml`](../../../../lib/templates/capex-costs.toml). It is not a tariff estimate: it identifies the value that must be paid in foreign currency or backed by an international financing source. The shared national trainset factory is outside this city CAPEX and appears once in the country `NATIONAL-BRIEF.md`.

| Capital boundary | Share of city CAPEX | Total requirement | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imported components / machinery** | **26.4%** | **$1.30 bn** | **$185 M / yr** |
| **Local capital for domestic procurement / payroll** | **73.6%** | **$3.60 bn** | **$515 M / yr** |
| of which planned local bond issuance | 58.8% of total CAPEX | $2.88 bn | $412 M / yr |
| **Total city programme** | **100.0%** | **$4.90 bn** | **$700 M / yr** |

### Foreign-company turnkey comparison

This is an editable like-for-like sensitivity, not a vendor quotation. It multiplies OSR CAPEX for an equivalent network, fleet, service, and energy scope, then assumes 90% of the foreign contractor price requires foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Foreign-turnkey case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $7.35 bn | $6.61 bn | $5.32 bn (80.4%) | $760 M / yr |
| **Default** | 2.00× | $9.80 bn | $8.82 bn | $7.52 bn (85.3%) | $1.07 bn / yr |
| High | 3.00× | $14.70 bn | $13.23 bn | $11.93 bn (90.2%) | $1.70 bn / yr |

At the default 2.00× case, OSR's $1.30 bn external requirement is 85.3% below the illustrative foreign-company requirement of $8.82 bn; total project CAPEX is 50.0% lower. Replace both variables with normalized bids before an investment decision.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (local public-equity drawdown + interest-only grace on external import finance and local bonds; capital-raising draws are shown above; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$435 M / yr** | $59 |
| Steady-state, low capacity-use (year 8+) | **$291 M / yr** | $39 |
| Steady-state, high capacity-use (year 8+) | **$181 M / yr** | $24 |
| Steady-state, operating-neutral revenue case | **$364 M / yr** | $49 |
| Lifecycle envelope (yr 1–40, low scenario) | **$12.64 bn cumulative** | $1,707 |
| Lifecycle envelope (yr 1–40, high scenario) | **$9.02 bn cumulative** | $1,218 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$15.07 bn cumulative** | $2,035 |

_Population basis: 7,404,689 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $74 M / yr → $183 M / yr._

### CAPEX funding sources

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| External climate/MDB debt for imported content (unconfirmed) | 26% | $1.30 bn | 4.5% | 40 y, 7 y grace | $76 M / yr |
| Local-currency sovereign / project bonds for local content | 59% | $2.88 bn | 9.5% | 40 y, 7 y grace | $288 M / yr |
| Local government equity / other domestic funding (no debt service) | 15% | $721 M | — | — | — |
| **Total** | **100%** | **$4.90 bn** | | | **$364 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — external import-finance debt $58 M / yr + local bonds $274 M / yr = **$332 M / yr** total. The base case assumes no climate-development grant. Local public equity is drawn across construction ($103 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

_Loan availability note: this is a finance placeholder, not a committed lender offer. Plausible providers would be a national government borrowing through an MDB or a climate fund accredited entity, such as the World Bank/IBRD, Islamic Development Bank, Climate Investment Funds, or Green Climate Fund channels. Official GCF policy allows grants and concessional loans, and World Bank/CIF material documents below-market climate finance, but this project still needs a lender mandate, eligibility screen, and signed term sheet before the 4.5% / 40-year assumption can be treated as real. Evidence anchors: [GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), [GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), [World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), [CIF funding instruments](https://www.cif.org/cif-funding), and [IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $48 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $50 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.1 M |
| Traction energy (1763.7 GWh / yr) | 186,424 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 66.1 GWh/yr + dedicated solar plant 1114.3 MW / 1952.3 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $13 M |
| Labour (1,965 FTE) | driverless roster: OCC/remote 369, station/platform 535, passenger service 231, fleet maintenance 458, infrastructure/energy 339, admin/training 33; no train drivers × country median × 12 × engineer-premium 1.4 | $5.4 M |
| **OPEX subtotal** | | **$117 M / yr** |

_Annual service work: 186,424 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 73.5 M train-km / yr (440.9 M car-km / yr). On-site PV covers 66.1 GWh/yr and the dedicated solar plant adds 1952.3 GWh/yr against 1763.7 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

## Maintenance schedule system

Baseline scheduled work covers 709 trainsets, 132 stations, 443.7 route-km, 9 lines, and 186,424 scheduled train-km/day. Intervals are defined in [`lib/templates/maintenance-schedule.toml`](../../../../lib/templates/maintenance-schedule.toml) and governed by [RFC 0029](../../../../docs/rfcs/0029-maintenance-schedule-system.md).

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

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.44 |
| Day pass (3 trips) | $1.12 (15 % bulk discount) |
| Monthly unlimited pass | $13.20 (~8 % of median monthly income) |
| Annual pass | $145.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (2,276,640 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the external/local CAPEX funding sources, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 30% |
| Annual paid trips | 415.5 M | 664.8 M | 248.0 M |
| Annual paid trips / city resident | 56 | 90 | 33 |
| Farebox revenue | $183 M / yr | $293 M / yr | $109 M / yr |
| Station shop leases | $3.2 M / yr | $3.2 M / yr | $3.2 M / yr |
| Advertising boards | $4.9 M / yr | $4.9 M / yr | $4.9 M / yr |
| **Total revenue** | **$191 M / yr** | **$301 M / yr** | **$117 M / yr** |
| Revenue / OPEX recovery | 163% | 256% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $364 M / yr | $364 M / yr | **$364 M / yr** |
| Operating surplus applied to debt support | -$74 M / yr | -$183 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $291 M / yr | $181 M / yr | **$364 M / yr** |
| Operating surplus after OPEX (before debt support) | $74 M / yr | $183 M / yr | $0 / yr |

_Commercial-revenue assumptions: 22,832 m² of station shop/kiosk leases at $13/m²/month and 4,200 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The grant-free procurement-origin funding boundary, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $53 M / yr | $84 M / yr | 16 min/trip × $0.48/h value-of-time proxy |
| Avoided road congestion | $120 M / yr | $191 M / yr | 1,496 M - 2,393 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $22 M / yr | $34 M / yr | 269.2–430.8 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $60 M / yr | $96 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $129 M / yr | $207 M / yr | 21% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $66 M / yr | $106 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$449 M / yr** | **$719 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 14 education anchors | 73,293 trips/school day; 16.1 M access-events/yr | 117,269 trips/school day; 25.8 M access-events/yr |
| Healthcare | 15 healthcare anchors | 91,433 trips/day; 33.4 M access-events/yr | 146,292 trips/day; 53.4 M access-events/yr |
| Commerce | 60 major/terminal/interchange nodes | 236,460 trips/trading day; 78.0 M access-events/yr | 378,336 trips/trading day; 124.9 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 120,662 trips/activity day; 36.2 M access-events/yr | 193,059 trips/activity day; 57.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $3.60 bn | 74% of $4.90 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $5.76 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $824 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 454,930 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 415.5 M - 664.8 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Financial validation

The machine-readable finance check reconciles the design-base CAPEX with the scenario-dependent solar plant and records deterministic cash-flow sensitivities. It is a planning screen, not financial close.

| Check | Result |
|---|---:|
| Authoritative design-base CAPEX | $4.01 bn |
| Timetable-sized dedicated solar CAPEX | $891 M |
| **Reconciled project CAPEX** | **$4.90 bn** |
| Imported / external-capital requirement | $1.30 bn (26.4%) |
| Local-content / local-funding requirement | $3.60 bn (73.6%) |
| Default foreign-turnkey external-capital comparison | $8.82 bn; OSR saves $7.52 bn (85.3%) |
| 15%–25% planning risk envelope | $5.63 bn–$6.12 bn |
| Annual OPEX | $117 M / yr |
| Low/high project NPV at 8% | $-3148388 k / $-2411474 k |
| Low/high project IRR | -3.2% / 1.1% |
| Low/high steady-state DSCR | 0.20 / 0.50 |

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
| 2-hour screenshot trace | 11,825.84 train-km; 177,101.60 kWh consumed; 170,545.67 kWh charged; 33 depot services completed; minimum SoC 62%; 0 onboard emergencies; 0 invariant violations |
| Full 05:30–02:00 service plus run-out | 179,108.22 train-km; 2,682,292.52 kWh consumed; 2,700,335.25 kWh charged; 1,564 depot services completed (5 active at cutoff); minimum SoC 47%; 0 onboard emergencies; 0 invariant violations; 96.1% of scheduled train-km delivered |

### Mandatory degraded-energy cases

| Case | Minimum SoC | Service delivered / required | Result |
|---|---:|---:|---:|
| 80% end-of-life battery capacity | 34.2% | 96.1% / 90% | pass |
| maximum planning climate/HVAC duty | 20.0% | 96.0% / 90% | pass |
| 50% charging-contact availability | 47.4% | 96.1% / 90% | pass |
| ten-hour all-site grid outage | 20.0% | 72.9% / 60% | pass |
| ten-hour single charging-pad outage | 47.4% | 96.1% / 90% | pass |

**Simulation acceptance:** passed — The full-window run includes 4.5 hours after the 02:00 service close so long ring and charging cycles can finish. Nominal and N-1/degraded screens protect 20% SoC and at least 90% of scheduled train-km. The ten-hour all-site grid outage is an emergency reduced-service case with a 60% floor. Energy-adaptive control may widen off-peak headways; calibrated timetable acceptance remains an operator gate.

Full evidence and provenance: [`engineering/simulation/validation-summary.json`](engineering/simulation/validation-summary.json).

| Simulation dashboard | Network visualizer |
|---|---|
| ![Dar-Es-Salaam energy and battery simulation dashboard](engineering/screenshots/dar-es-salaam-simulation-dashboard.png) | ![Dar-Es-Salaam simulator network visualizer](engineering/screenshots/dar-es-salaam-network-visualizer.png) |

## SUMO, QGIS, and energy screening

These are executed city-specific screening runs. They establish model consistency and expose planning findings; they are not a calibrated operational or construction acceptance.

| Package | Current result |
|---|---|
| SUMO | 36/36 screening services arrived; 0 input findings; status `completed` |
| QGIS/GDAL | GeoPackage generated with 9 corridors, 132 line platforms, 18 interchange complexes, 289 civil segments, and 0 input findings |
| pandapower/pvlib | Solver passed; grid-only max transformer loading 81.1%; coordinated-daylight max 33.0%; 0 open screening findings |

Evidence: [`engineering/sumo/summary.json`](engineering/sumo/summary.json), [`engineering/gis/summary.json`](engineering/gis/summary.json), and [`engineering/energy/summary.json`](engineering/energy/summary.json).

| QGIS engineering-layer review | SUMO executed timetable review |
|---|---|
| ![Dar-Es-Salaam QGIS engineering layers](engineering/screenshots/dar-es-salaam-qgis-engineering-map.png) | ![Dar-Es-Salaam SUMO timetable validation](engineering/screenshots/dar-es-salaam-sumo-validation.png) |

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`dar-es-salaam.toml`](dar-es-salaam.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`dar-es-salaam-network-map.png`](dar-es-salaam-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`dar-es-salaam.stations.json`](dar-es-salaam.stations.json) | Machine-readable station list |
| [`dar-es-salaam.design-quality.yaml`](dar-es-salaam.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |


Run the city regeneration command below to refresh the full engineering and operations bundle in this city folder.

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug dar-es-salaam

# 2. full generated design, scenario, engineering, and operations bundle
scripts/regenerate-city.sh dar-es-salaam
```

The generated design, scenario, engineering, and operations evidence share this canonical city directory.
