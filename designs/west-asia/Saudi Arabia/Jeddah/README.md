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
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **531,100 – 955,980 trips/day**

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

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,218 kWh | 50.8 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 531 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 413 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 526 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

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
| Residual train-control wayside + charging microgrids | $114 M |
| EPC overhead (7%) | $524 M |
| **CAPEX total** | **$8.01 bn** |
| Per-route-km | $20 M / km |
| Per-capita (city pop) | $1,705 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh jeddah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$240 M / yr** | $51 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$160 M / yr** | $34 |
| Lifecycle envelope (yr 1–40, low scenario) | **$1.20 bn cumulative** | $256 |
| Lifecycle envelope (yr 1–40, high scenario) | **$1.20 bn cumulative** | $256 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$6.81 bn cumulative** | $1,449 |

_Population basis: 4,700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $160 M / yr → $160 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $3.20 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $4.01 bn | 2.0% | 40 y, 5 y grace | $160 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 4.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $801 M | — | — | — |
| **Total** | **100%** | **$8.01 bn** | | | **$160 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $80 M / yr + fallback bonds $0 k / yr = **$80 M / yr** total. The $3.20 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($160 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $180 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $51 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.0 M |
| Traction energy (2276.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,448 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $70 M |
| **OPEX subtotal** | | **$302 M / yr** |

_Annual fleet utilisation: 483 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 94.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $4.53 |
| Day pass (3 trips) | $11.56 (15 % bulk discount) |
| Monthly unlimited pass | $136.00 (~8 % of median monthly income) |
| Annual pass | $1496.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (1,843,200 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 531,100 | 955,980 | 109,022 |
| Daily paid trips / catchment | 25% | 45% | 5% |
| Daily paid trips / city population | 11% | 20% | 2% |
| Annual paid trips | 193.9 M | 348.9 M | 39.8 M |
| Farebox revenue | $879 M / yr | $1.58 bn / yr | $180 M / yr |
| Station shop leases | $37 M / yr | $37 M / yr | $37 M / yr |
| Advertising boards | $85 M / yr | $85 M / yr | $85 M / yr |
| **Total revenue** | **$1.00 bn / yr** | **$1.70 bn / yr** | **$302 M / yr** |
| Revenue / OPEX recovery | 331% | 564% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Gross repayable-debt service + residual OPEX subsidy | $160 M / yr | $160 M / yr | **$160 M / yr** |
| Operating surplus applied to debt support | -$160 M / yr | -$160 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$160 M / yr** |
| Operating surplus after OPEX (before debt support) | $698 M / yr | $1.40 bn / yr | $0 / yr |

_Commercial-revenue assumptions: 38,528 m² of station shop/kiosk leases at $90/m²/month and 7,016 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

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
