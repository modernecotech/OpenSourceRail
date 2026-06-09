# Jeddah — Urban Rail Network

**Country:** SA · **Population:** 4,700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Jeddah rail network on OpenStreetMap](jeddah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`jeddah.corridor.geojson`](jeddah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 201 |
| Interchange stations | 35 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 45.2% |
| Route length (double track) | 406.0 km |
| Revenue fleet | 483 × 6-car trainsets |
| Revenue fleet passenger capacity | 347,760 AW2 pax (463,680 AW3 crush) |
| Spare + cold-reserve | 54 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 53.1 km | 27 | 70 | NW Outer ↔ S Outer |
| line-2 | 48.3 km | 25 | 64 | SE Mid ↔ N Outer |
| line-3 | 50.1 km | 26 | 67 | NW Mid ↔ SE Outer |
| line-4 | 42.7 km | 25 | 57 | NW Mid ↔ SE Outer |
| line-5 | 54.0 km | 21 | 71 | N Outer ↔ S Outer |
| line-6 | 41.7 km | 18 | 56 | SW Outer ↔ E Mid |
| line-7 | 29.7 km | 16 | 40 | NE Outer ↔ SW Inner |
| line-8 | 86.5 km | 44 | 112 | NW Mid ↔ NW Mid |
| **Total** | **406.0 km** | **201 unique** | **537** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 347,760 AW2 pax (463,680 AW3 crush) |
| Total fleet capacity | 386,640 AW2 pax (515,520 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 483 × 720 = **347,760 AW2 passengers** (463,680 AW3 crush)
- **Total fleet passenger capacity:** 537 × 720 = **386,640 AW2 passengers** (515,520 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 14,400 = **230,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,304,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,843,200 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **336.4 – 538.2 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **4,700,000**
- Anchor-weighted coverage: 45.2%
- Catchment population: **≈ 2,124,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 35 | 500 kW | 3000 kWh |
| Major | 92 | 400 kW | 2500 kWh |
| Standard | 56 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **197** | **82,600 kW** | **526,000 kWh** |

Aggregate station-rail charging power: **106,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,127.3 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,218 kWh | 50.8 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 531 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 413 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 5,314 MWh/day | 205,030 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 4,901 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,127.3 MW / 5,637 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 526 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (385.6 km @ $3.0 M/km) | $1.16 bn |
| Elevated (19.4 km @ $12.0 M/km) | $233 M |
| Elevated-interchange premium (16 sites @ $4.50 M) | $72 M |
| **Civil subtotal** | **$1.46 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | $600 k | $3.0 M |
| `standard` | 56 | $2.50 M | $140 M |
| `major` | 92 | $4.50 M | $414 M |
| `terminal` | 13 | $4.50 M | $58 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 35 | $12.0 M | $420 M |
| **Stations subtotal** | | | **$1.04 bn** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 13 | $2.0 M | $26 M |
| **Depots subtotal** | | | **$38 M** |

### Rolling stock

Rolling stock is costed at the **delivered production planning unit: $1.4 M per self-contained car**. The raw 3-car light-metro BOM floor remains 592,840 USD direct material plus 35 % assembly allowance = 800,334 USD per consist, but city CAPEX now adds production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. Motors, sensors, train-control computers, onboard batteries, roof PV, and charge hardware appear here ONLY — never re-billed elsewhere in the city cost stack.

| Per-car cost bucket | Basis | Cost |
|---|---|---|
| Direct material BOM floor | Welded frame, panels, glazing, doors, bogies, traction, batteries, HVAC, electronics, interiors | $267 k |
| Production labour + shop overhead | Cut/bend/weld, fit-out, harnessing, paint, factory supervision, utilities, rework reserve | $420 k |
| Fixtures, tooling, QA, certification evidence | Jigs/fixtures, dimensional QA, EN 15085/45545 evidence, supplier audits, homologation dossier amortisation | $310 k |
| Logistics, warranty, spares, commissioning | Freight, duty, insurance, initial spares/tools, manuals/training, site testing, acceptance runs | $403 k |
| **Total per car** | Delivered production planning unit | **$1.4 M** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 537 | $8.40 M | $4.51 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 3222 | $100 k | $322 M |
| High sensitivity check | 3222 | $200 k | $644 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,127,317 kW @ $700/kW | $789 M |
| Grid interconnection / PPA tie-in | 1,127,317 kW @ $100/kW | $113 M |
| Annual generation proxy | 1,127.3 MW × 5.0 peak-sun-h/day × 365 d/yr | 2,057.4 GWh/yr |
| **Dedicated solar plant subtotal** | | **$902 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 406.0 km × $0.050 M/km | $20 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $93 M |
| EPC integration + project management (7%) | on subtotal | $524 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.46 bn |
| Stations | $1.04 bn |
| Depots | $38 M |
| Rolling stock | $4.51 bn |
| Railway production plant | $322 M |
| Dedicated solar power plant | $902 M |
| Residual train-control wayside + charging microgrids | $114 M |
| EPC overhead (7%) | $524 M |
| **CAPEX total** | **$8.91 bn** |
| Per-route-km | $22 M / km |
| Per-capita (city pop) | $1,896 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh jeddah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$499 M / yr** | $106 |
| Steady-state, low capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$285 M / yr** | $61 |
| Lifecycle envelope (yr 1–40, low scenario) | **$2.50 bn cumulative** | $531 |
| Lifecycle envelope (yr 1–40, high scenario) | **$2.50 bn cumulative** | $531 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$12.48 bn cumulative** | $2,655 |

_Population basis: 4,700,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $285 M / yr → $285 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $7.13 bn | 2.0% | 40 y, 5 y grace | $285 M / yr |
| Government equity (no debt service) | 20% | $1.78 bn | — | — | — |
| **Total** | **100%** | **$8.91 bn** | | | **$285 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $143 M / yr = **$143 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($357 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $180 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $51 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.0 M |
| Traction energy (1939.7 GWh / yr) | 205,030 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 150.7 GWh/yr + dedicated solar plant 1127.3 MW / 2057.4 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $14 M |
| Labour (2,205 FTE) | driverless roster: OCC/remote 288, station/platform 834, passenger service 191, fleet maintenance 431, infrastructure/energy 391, admin/training 70; no train drivers × country median × 12 × engineer-premium 1.4 | $63 M |
| **OPEX subtotal** | | **$309 M / yr** |

_Annual service work: 205,030 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 80.8 M train-km / yr (484.9 M car-km / yr). On-site PV covers 150.7 GWh/yr and the dedicated solar plant adds 2057.4 GWh/yr against 1939.7 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $4.53 |
| Day pass (3 trips) | $11.56 (15 % bulk discount) |
| Monthly unlimited pass | $136.00 (~8 % of median monthly income) |
| Annual pass | $1496.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (1,843,200 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 6% |
| Annual paid trips | 336.4 M | 538.2 M | 41.2 M |
| Annual paid trips / city resident | 72 | 115 | 9 |
| Farebox revenue | $1.52 bn / yr | $2.44 bn / yr | $187 M / yr |
| Station shop leases | $37 M / yr | $37 M / yr | $37 M / yr |
| Advertising boards | $85 M / yr | $85 M / yr | $85 M / yr |
| **Total revenue** | **$1.65 bn / yr** | **$2.56 bn / yr** | **$309 M / yr** |
| Revenue / OPEX recovery | 533% | 830% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Gross repayable-debt service + residual OPEX subsidy | $285 M / yr | $285 M / yr | **$285 M / yr** |
| Operating surplus applied to debt support | -$285 M / yr | -$285 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$285 M / yr** |
| Operating surplus after OPEX (before debt support) | $1.34 bn / yr | $2.25 bn / yr | $0 / yr |

_Commercial-revenue assumptions: 38,528 m² of station shop/kiosk leases at $90/m²/month and 7,016 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $440 M / yr | $704 M / yr | 16 min/trip × $4.90/h value-of-time proxy |
| Avoided road congestion | $97 M / yr | $155 M / yr | 1,211 M - 1,938 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $17 M / yr | $28 M / yr | 218.0–348.8 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $48 M / yr | $78 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $668 M / yr | $1.07 bn / yr | 23% of paid trips × $8.50 local spend proxy |
| Entertainment / community activity supported | $303 M / yr | $485 M / yr | 11% of paid trips × $8.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$1.57 bn / yr** | **$2.52 bn / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 5 education anchors | 45,299 trips/school day; 10.0 M access-events/yr | 72,478 trips/school day; 15.9 M access-events/yr |
| Healthcare | 17 healthcare anchors | 77,602 trips/day; 28.3 M access-events/yr | 124,163 trips/day; 45.3 M access-events/yr |
| Commerce | 141 major/terminal/interchange nodes | 215,338 trips/trading day; 71.1 M access-events/yr | 344,541 trips/trading day; 113.7 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 97,690 trips/activity day; 29.3 M access-events/yr | 156,303 trips/activity day; 46.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $4.47 bn | 50% of $8.91 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $7.16 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $1.43 bn / yr | spread across 5 construction / grace years |
| Construction employment supported | 54,826 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 336.4 M - 538.2 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`jeddah.toml`](jeddah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`jeddah-network-map.png`](jeddah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`jeddah.corridor.geojson`](jeddah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`jeddah.stations.json`](jeddah.stations.json) | Machine-readable station list |
| [`jeddah.design-quality.yaml`](jeddah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug jeddah

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug jeddah \
    --sidecar .cache/osr-pipeline/rasters/jeddah.grid.json \
    --out-dir designs/.../Jeddah

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../jeddah.toml \
    --out designs/.../README.md
```

`scripts/regenerate-jeddah.sh` chains steps 3 + drift tests into a single command.
