# Lusaka — Urban Rail Network

**Country:** ZM · **Population:** 3,037,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Lusaka rail network on OpenStreetMap](lusaka-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`lusaka.corridor.geojson`](lusaka.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 167 |
| Interchange-class stations | 15 |
| Multi-line transfer reachability | 57% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 58.4% |
| Route length (double track) | 279.5 km |
| Revenue fleet | 514 × 6-car trainsets |
| Revenue fleet passenger capacity | 370,080 AW2 pax (493,440 AW3 crush) |
| Dedicated depot-service rotation fleet | 0 (off-peak service uses peak-fleet surplus) |
| Spare + cold-reserve | 56 × 6-car trainsets |
| Peak headway | 3 min |
| Station spacing policy | 1.2 km central / 2 km urban / 3 km suburban / up to 5 km in the lowest-demand outer fringe |
| City-centre consolidation | Cross-line platforms within the 600 m station-complex envelope are emitted as one interchange |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Turnaround inspection and recharge

During the 07:00–09:00 and 15:00–17:00 peaks, trains make the normal quick terminal turnback: no depot-service hold is inserted, allowing more battery depletion while the 20% dispatch-reserve gate remains mandatory. In the 6- and 12-minute lower-frequency windows, each line's deterministic energy controller may widen the published headway when actual charging delivery leaves a departing set below the 40% normal-service SoC target (up to 3× the published headway). This automatically matches offered off-peak service to available traction energy without buying a separate service-rotation fleet. In those lower-frequency windows, each train receives a **12-minute service slot** at its designated powered service point. This may be a staffed terminal platform or the main depot; only defects and maintenance require a depot move. Interior cleaning, exterior and running-gear walk-around, door/coupler/emergency-equipment checks, fault-log download, and a 150 kW low-C recharge run concurrently. A red defect holds the set for maintenance; a clear inspection returns it to the revenue rotation.

The fleet is sized for the 3-minute peaks; when service relaxes to 6 or 12 minutes, the same peak fleet provides enough idle cover for service-point work. Therefore **0 additional trainsets** are required for depot service; only the existing 48 planned-maintenance spares and 8 cold-reserve sets are included in the rolling-stock, production-plant, maintenance, labour, and total CAPEX/OPEX figures below.

## Distributed overnight stabling

At service close, telemetry-healthy trainsets remain at selected powered passenger stations near their first morning departures. Every occupied station must provide at least 150 kW low-C charging, CCTV, remote traction isolation, protected emergency access, and an OCC-assigned train/track slot. Sets with red defects, overdue heavy maintenance, failed isolation, or failed security return to the main-heavy depot. OCC verifies charge completion and remote self-test before releasing all station-stabled sets together at service start. The generated default therefore builds one maintenance-focused main depot, not a parking depot at every terminus.

Circumferential lines use the same demand-based stop-spacing policy as radials (1.0× the equivalent radial spacing), while every forced radial-transfer platform is retained. Charging-platform dwell is 120 seconds, calculated from one circuit's climate-adjusted energy and the line's aggregate charging power; non-charging halts keep their ordinary dwell.

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 38.5 km | 23 | 96 | NE Outer ↔ W Mid |
| line-2 | 26.2 km | 15 | 68 | E Mid ↔ SW Mid |
| line-3 | 27.5 km | 18 | 73 | SE Outer ↔ W Mid |
| line-4 | 23.8 km | 14 | 62 | E Mid ↔ NW Mid |
| line-5 | 28.4 km | 17 | 73 | N Inner ↔ S Outer |
| line-6 | 32.4 km | 18 | 81 | NE Outer ↔ W Mid |
| line-7 | 28.7 km | 16 | 71 | N Mid ↔ SW Outer |
| line-8 | 73.9 km | 46 | 46 | N Outer ↔ N Mid |
| **Total** | **279.5 km** | **167 unique** | **570** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 1,080 kWh usable / 1,350 kWh nameplate per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 370,080 AW2 pax (493,440 AW3 crush) |
| Total fleet capacity | 410,400 AW2 pax (547,200 AW3 crush, incl. service rotation + spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 514 × 720 = **370,080 AW2 passengers** (493,440 AW3 crush)
- **Total fleet passenger capacity:** 570 × 720 = **410,400 AW2 passengers** (547,200 AW3 crush, incl. service rotation + spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 14,400 = **230,400 passengers/hour**
- **Scheduled one-way train journeys:** **3,488/day**
- **Daily theoretical capacity from timetable:** 3,488 scheduled one-way train journeys/day × 720 AW2 pax = **2,511,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **2,008,800 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **366.6 – 586.6 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **3,037,000**
- Anchor-weighted coverage: 58.4%
- Catchment population: **≈ 1,773,608** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 55 | 300 kW | 2000 kWh |
| Major | 5 | 300 kW | 2000 kWh |
| Standard | 78 | 300 kW | 2000 kWh |
| Terminal | 13 | 300 kW | 2000 kWh |
| **Total installed** | **152** | **50,300 kW** | **342,000 kWh** |

Aggregate station-rail charging power: **304,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 1,080 kWh usable (1,350 kWh nameplate) battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **642.6 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Onboard battery adequacy | 7.2× worst inter-charge run | OK: 1,350 kWh nameplate, 270 kWh protected reserve, and 929 kWh usable margin across the worst powered-stop gap (line-1) |
| Lowest traversal charging margin | 508 kWh | line-7 after climate load, 98% conversion, and the required 10% operating margin |
| PV daily yield proxy | 241 MWh/day | 4.8 peak-sun-hour planning proxy before local derates |
| Scheduled one-way train journeys | 3,488 / day | Train departures across both directions and all lines |
| Scheduled train journey-km | 112,792 train-km/day | One-way train journeys × route length |
| Annual service work | 44.5 M train-km/yr | Includes 108% depot/deadhead factor |
| Scheduled traction demand | 2,924 MWh/day | 266.8 M car-km/yr × 4.0 kWh/car-km |
| On-site PV shortfall before solar plant | 2,682 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 642.6 MW / 3,084 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 342 MWh | Distributed LFP buffer for charging peaks and grid outages |

Opportunity charging is checked line by line; ring trains remain in service while receiving the longer planned dwell at every powered platform.

| Line | Powered stops | Climate-adjusted traversal | Delivered per traversal | Required-margin surplus | Worst powered-stop gap |
|---|---:|---:|---:|---:|---:|
| line-1 | 20 | 577 kWh | 1,405 kWh | 770 kWh | 10.1 km / 151 kWh |
| line-2 | 15 | 393 kWh | 1,045 kWh | 613 kWh | 2.4 km / 36 kWh |
| line-3 | 18 | 412 kWh | 1,241 kWh | 788 kWh | 2.7 km / 41 kWh |
| line-4 | 14 | 357 kWh | 980 kWh | 587 kWh | 2.0 km / 30 kWh |
| line-5 | 16 | 425 kWh | 1,111 kWh | 643 kWh | 4.1 km / 61 kWh |
| line-6 | 16 | 486 kWh | 1,111 kWh | 576 kWh | 9.2 km / 138 kWh |
| line-7 | 14 | 429 kWh | 980 kWh | 508 kWh | 8.5 km / 128 kWh |
| line-8 | 39 | 1,107 kWh | 2,548 kWh | 1,330 kWh | 8.0 km / 120 kWh |

## CAPEX (planning grade)

Base figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Full generated bundles add the scenario-dependent dedicated solar plant and finance reconciliation under `build/`. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields are explicit converted reporting views at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), distributed overnight stabling that reduces depot parking and local commissioning-bay scope, at-grade depots without overhead bridge cranes, **trainset-family rolling-stock units** (for example $900 k per 3-car light-metro trainset, with the raw marketplace BOM retained only as an audit floor), commodity LFP packs + heavy-vehicle PMSM motors + matched commercial traction controllers, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line includes direct material, local assembly/labour, nominal per-train QA/acceptance, and modest local handover logistics. Fixtures, tooling, and production-readiness live in the separate railway production-plant setup line at $60 k per vehicle/car module, with $120 k retained as the high sensitivity check; warranty, spares, and routine commissioning support are OPEX rather than repeated train CAPEX. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (260.9 km @ $3.0 M/km) | $783 M |
| Elevated (18.7 km @ $12.0 M/km) | $224 M |
| Elevated-interchange premium (15 sites @ $4.50 M) | $68 M |
| **Civil subtotal** | **$1.07 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 15 | $600 k | $9.0 M |
| `standard` | 78 | $2.50 M | $195 M |
| `major` | 5 | $4.50 M | $22 M |
| `terminal` | 13 | $4.50 M | $58 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 55 | $12.0 M | $660 M |
| **Stations subtotal** | | | **$950 M** |

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
| `metro-6car` (revenue + service rotation + spare + cold reserve) | 570 | $1.68 M | $958 M |

#### 800 V procurement basis

The following RFC 0021 commodity-component reconciliation is already included in the delivered rolling-stock and charging-site planning units; it is shown for auditability and is not additive.

| Component | Current design basis |
|---|---:|
| Onboard architecture | 800 V-class; 650-700 V nominal traction DC bus |
| Gross traction battery | 225 kWh/car; 24,167 USD/car |
| PMSM motor + controller sets | 2/car @ 10,000 USD/set |
| Core electrical subtotal | 51,000 USD/car; 306,000 USD/trainset |
| Normal 500 kWh / 500 kW station equipment | 65,000 USD; 100,000 USD integrated allowance |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, fixtures, plant services, production-readiness, and commissioning bay setup. Standard 1 m fiberglass body moulds, dry clips, and compact gauges replace a full-length body mould and adhesive cure hall. It is costed per vehicle/car module, not per trainset, and stays separate from the rolling-stock procurement line. Distributed overnight stabling reduces this allowance because fewer depot-centred commissioning and stabling bays are required.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 3420 | $60 k | $205 M |
| High sensitivity check | 3420 | $120 k | $410 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 642,596 kW @ $700/kW | $450 M |
| Grid interconnection / PPA tie-in | 642,596 kW @ $100/kW | $64 M |
| Annual generation proxy | 642.6 MW × 4.8 peak-sun-h/day × 365 d/yr | 1,125.8 GWh/yr |
| **Dedicated solar plant subtotal** | | **$514 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 279.5 km × $0.050 M/km | $14 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $67 M |
| EPC integration + project management (7%) | on subtotal | $229 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.07 bn |
| Stations | $950 M |
| Depots | $8.0 M |
| Rolling stock | $958 M |
| Railway production plant | $205 M |
| Dedicated solar power plant | $514 M |
| Residual train-control wayside + charging microgrids | $81 M |
| EPC overhead (7%) | $229 M |
| **CAPEX total** | **$4.02 bn** |
| Per-route-km | $14 M / km |
| Per-capita (city pop) | $1,323 / person |

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

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh lusaka`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$260 M / yr** | $85 |
| Steady-state, low capacity-use (year 8+) | **$99 M / yr** | $33 |
| Steady-state, high capacity-use (year 8+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$189 M / yr** | $62 |
| Lifecycle envelope (yr 1–40, low scenario) | **$5.08 bn cumulative** | $1,674 |
| Lifecycle envelope (yr 1–40, high scenario) | **$1.82 bn cumulative** | $598 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$8.05 bn cumulative** | $2,650 |

_Population basis: 3,037,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $90 M / yr → $189 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Candidate climate/MDB concessional debt (unconfirmed) | 80% | $3.22 bn | 4.5% | 40 y, 7 y grace | $189 M / yr |
| Government equity (no debt service) | 20% | $804 M | — | — | — |
| **Total** | **100%** | **$4.02 bn** | | | **$189 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — candidate climate/MDB debt $145 M / yr = **$145 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($115 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

_Loan availability note: this is a finance placeholder, not a committed lender offer. Plausible providers would be a national government borrowing through an MDB or a climate fund accredited entity, such as the World Bank/IBRD, Islamic Development Bank, Climate Investment Funds, or Green Climate Fund channels. Official GCF policy allows grants and concessional loans, and World Bank/CIF material documents below-market climate finance, but this project still needs a lender mandate, eligibility screen, and signed term sheet before the 4.5% / 40-year assumption can be treated as real. Evidence anchors: [GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), [GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), [World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), [CIF funding instruments](https://www.cif.org/cif-funding), and [IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $38 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $41 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $699 k |
| Traction energy (1067.1 GWh / yr) | 112,792 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 88.1 GWh/yr + dedicated solar plant 642.6 MW / 1125.8 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $7.7 M |
| Labour (1,802 FTE) | driverless roster: OCC/remote 304, station/platform 698, passenger service 204, fleet maintenance 320, infrastructure/energy 245, admin/training 31; no train drivers × country median × 12 × engineer-premium 1.4 | $5.3 M |
| **OPEX subtotal** | | **$93 M / yr** |

_Annual service work: 112,792 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 44.5 M train-km / yr (266.8 M car-km / yr). On-site PV covers 88.1 GWh/yr and the dedicated solar plant adds 1125.8 GWh/yr against 1067.1 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

## Maintenance schedule system

Baseline scheduled work covers 570 trainsets, 167 stations, 279.5 route-km, 8 lines, and 112,792 scheduled train-km/day. Intervals are defined in [`lib/templates/maintenance-schedule.toml`](../../../../lib/templates/maintenance-schedule.toml) and governed by [RFC 0029](../../../../docs/rfcs/0029-maintenance-schedule-system.md).

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

Country median monthly income: **$175 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.47 |
| Day pass (3 trips) | $1.19 (15 % bulk discount) |
| Monthly unlimited pass | $14.00 (~8 % of median monthly income) |
| Annual pass | $154.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (2,008,800 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 24% |
| Annual paid trips | 366.6 M | 586.6 M | 174.0 M |
| Annual paid trips / city resident | 121 | 193 | 57 |
| Farebox revenue | $171 M / yr | $274 M / yr | $81 M / yr |
| Station shop leases | $4.5 M / yr | $4.5 M / yr | $4.5 M / yr |
| Advertising boards | $6.9 M / yr | $6.9 M / yr | $6.9 M / yr |
| **Total revenue** | **$183 M / yr** | **$285 M / yr** | **$93 M / yr** |
| Revenue / OPEX recovery | 197% | 308% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $189 M / yr | $189 M / yr | **$189 M / yr** |
| Operating surplus applied to debt support | -$90 M / yr | -$189 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $99 M / yr | $0 k / yr | **$189 M / yr** |
| Operating surplus after OPEX (before debt support) | $90 M / yr | $193 M / yr | $0 / yr |

_Commercial-revenue assumptions: 30,472 m² of station shop/kiosk leases at $14/m²/month and 5,556 advertising boards at $122/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $49 M / yr | $79 M / yr | 16 min/trip × $0.50/h value-of-time proxy |
| Avoided road congestion | $106 M / yr | $169 M / yr | 1,320 M - 2,112 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $19 M / yr | $30 M / yr | 237.6–380.1 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $53 M / yr | $84 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $114 M / yr | $182 M / yr | 21% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $58 M / yr | $93 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$399 M / yr** | **$638 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 12 education anchors | 61,171 trips/school day; 13.5 M access-events/yr | 97,874 trips/school day; 21.5 M access-events/yr |
| Healthcare | 7 healthcare anchors | 69,790 trips/day; 25.5 M access-events/yr | 111,663 trips/day; 40.8 M access-events/yr |
| Commerce | 74 major/terminal/interchange nodes | 207,436 trips/trading day; 68.5 M access-events/yr | 331,897 trips/trading day; 109.5 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 106,466 trips/activity day; 31.9 M access-events/yr | 170,346 trips/activity day; 51.1 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $2.17 bn | 54% of $4.02 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $3.47 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $496 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 258,440 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 366.6 M - 586.6 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Financial validation

The machine-readable finance check reconciles the design-base CAPEX with the scenario-dependent solar plant and records deterministic cash-flow sensitivities. It is a planning screen, not financial close.

| Check | Result |
|---|---:|
| Authoritative design-base CAPEX | $3.50 bn |
| Timetable-sized dedicated solar CAPEX | $514 M |
| **Reconciled project CAPEX** | **$4.02 bn** |
| 15%–25% planning risk envelope | $4.62 bn–$5.02 bn |
| Annual OPEX | $93 M / yr |
| Low/high project NPV at 8% | $-2385332 k / $-1695707 k |
| Low/high project IRR | -1.5% / 2.4% |
| Low/high steady-state DSCR | 0.48 / 1.02 |

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
| 2-hour screenshot trace | 7,609.48 train-km; 113,958.30 kWh consumed; 125,067.48 kWh charged; 50 depot services completed; minimum SoC 84%; 0 onboard emergencies; 0 invariant violations |
| Full 05:30–02:00 service plus run-out | 115,263.81 train-km; 1,726,171.69 kWh consumed; 1,760,676.28 kWh charged; 1,347 depot services completed (9 active at cutoff); minimum SoC 80%; 0 onboard emergencies; 0 invariant violations; 100.0% of scheduled train-km delivered |

### Mandatory degraded-energy cases

| Case | Minimum SoC | Service delivered / required | Result |
|---|---:|---:|---:|
| 80% end-of-life battery capacity | 74.9% | 100.0% / 90% | pass |
| maximum planning climate/HVAC duty | 76.2% | 100.0% / 90% | pass |
| 50% charging-contact availability | 79.9% | 100.0% / 90% | pass |
| ten-hour all-site grid outage | 20.0% | 88.0% / 60% | pass |
| ten-hour single charging-pad outage | 77.8% | 100.0% / 90% | pass |

**Simulation acceptance:** passed — The full-window run includes 4.5 hours after the 02:00 service close so long ring and charging cycles can finish. Nominal and N-1/degraded screens protect 20% SoC and at least 90% of scheduled train-km. The ten-hour all-site grid outage is an emergency reduced-service case with a 60% floor. Energy-adaptive control may widen off-peak headways; calibrated timetable acceptance remains an operator gate.

Full evidence and provenance: [`engineering/simulation/validation-summary.json`](engineering/simulation/validation-summary.json).

| Simulation dashboard | Network visualizer |
|---|---|
| ![Lusaka energy and battery simulation dashboard](engineering/screenshots/lusaka-simulation-dashboard.png) | ![Lusaka simulator network visualizer](engineering/screenshots/lusaka-network-visualizer.png) |

## SUMO, QGIS, and energy screening

These are executed city-specific screening runs. They establish model consistency and expose planning findings; they are not a calibrated operational or construction acceptance.

| Package | Current result |
|---|---|
| SUMO | 32/32 screening services arrived; 0 input findings; status `completed` |
| QGIS/GDAL | GeoPackage generated with 8 corridors, 167 line platforms, 15 interchange complexes, 107 civil segments, and 0 input findings |
| pandapower/pvlib | Solver passed; grid-only max transformer loading 81.1%; coordinated-daylight max 33.0%; 0 open screening findings |

Evidence: [`engineering/sumo/summary.json`](engineering/sumo/summary.json), [`engineering/gis/summary.json`](engineering/gis/summary.json), and [`engineering/energy/summary.json`](engineering/energy/summary.json).

| QGIS engineering-layer review | SUMO executed timetable review |
|---|---|
| ![Lusaka QGIS engineering layers](engineering/screenshots/lusaka-qgis-engineering-map.png) | ![Lusaka SUMO timetable validation](engineering/screenshots/lusaka-sumo-validation.png) |

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`lusaka.toml`](lusaka.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`lusaka-network-map.png`](lusaka-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`lusaka.corridor.geojson`](lusaka.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`lusaka.stations.json`](lusaka.stations.json) | Machine-readable station list |
| [`lusaka.design-quality.yaml`](lusaka.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |


Run the city regeneration command below to refresh the full engineering and operations bundle in this city folder.

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug lusaka

# 2. full generated design, scenario, engineering, and operations bundle
scripts/regenerate-city.sh lusaka
```

The generated design, scenario, engineering, and operations evidence share this canonical city directory.
