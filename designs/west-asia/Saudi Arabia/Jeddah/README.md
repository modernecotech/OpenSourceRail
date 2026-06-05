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
| Revenue fleet | 292 × 6-car trainsets |
| Spare + cold-reserve | 34 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 53.1 km | 27 | 42 | NW Outer ↔ S Outer |
| line-2 | 48.3 km | 25 | 39 | SE Mid ↔ N Outer |
| line-3 | 50.1 km | 26 | 40 | NW Mid ↔ SE Outer |
| line-4 | 42.7 km | 25 | 35 | NW Mid ↔ SE Outer |
| line-5 | 54.0 km | 21 | 43 | N Outer ↔ S Outer |
| line-6 | 41.7 km | 18 | 34 | SW Outer ↔ E Mid |
| line-7 | 29.7 km | 16 | 25 | NE Outer ↔ SW Inner |
| line-8 | 86.5 km | 44 | 68 | NW Mid ↔ NW Mid |
| **Total** | **406.0 km** | **201 unique** | **326** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 660 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 840 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 660 AW2 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 660 × 12 = **7,920 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 7,920 = **126,720 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,267,200 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **212,440 – 318,660 trips/day**

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

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (385.6 km @ $1.2 M/km) | $463 M |
| Elevated (19.4 km @ $5.5 M/km) | $107 M |
| Elevated-interchange premium (16 sites @ $2.5 M) | $40 M |
| **Civil subtotal** | **$610 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | $180 k | $900 k |
| `standard` | 56 | $450 k | $25 M |
| `major` | 92 | $900 k | $83 M |
| `terminal` | 13 | $800 k | $10 M |
| `depot-terminal` | 1 | $1.00 M | $1.0 M |
| `interchange-elevated` | 35 | $1.80 M | $63 M |
| **Stations subtotal** | | | **$183 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $7.50 M | $7.5 M |
| `layup-minimal` | 13 | $900 k | $12 M |
| **Depots subtotal** | | | **$19 M** |

### Rolling stock

Rolling stock is costed at the **marketplace-BOM floor: $267 k per self-contained car**. The value comes from the 3-car light-metro BOM base of 592,840 USD direct material plus 35 % assembly allowance = 800,334 USD per consist and is divided across three cars. Motors, sensors, train-control computers, onboard batteries, roof PV, and charge hardware appear here ONLY — never re-billed elsewhere in the city cost stack.

| Per-car cost bucket | Basis | Cost |
|---|---|---|
| Body shell + interior + doors | Welded frame, composite panels, glass, doors, seats, PRM fixtures | $106 k |
| Bogies + brakes | Two 2-axle bogies per car, wheelsets, suspension, discs, pads, sensors | $51 k |
| Traction, battery, HVAC, solar + charging | PMSM/gear/inverter package, 120 kWh pack share, BMS, HVAC, roof PV, charger | $93 k |
| Electronics + train-control | T-ECU/S, T-ECU/A, T-OBS sensors, radios, cameras, PIS, event recorder | $16 k |
| Accessibility + safety kit | Passenger call buttons, signs, emergency lighting, first-aid/fire kit | $1 k |
| **Total per car** | | **$267 k** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 326 | $1.60 M | $522 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 406.0 km × $0.015 M/km | $6.1 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $48 M |
| EPC integration + project management (7%) | on subtotal | $97 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $610 M |
| Stations | $183 M |
| Depots | $19 M |
| Rolling stock | $522 M |
| Residual train-control wayside + charging microgrids | $54 M |
| EPC overhead (7%) | $97 M |
| **CAPEX total** | **$1.48 bn** |
| Per-route-km | $3.7 M / km |
| Per-capita (city pop) | $316 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh jeddah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$95 M / yr** | $20 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, cost-neutral revenue case | **$0 / yr** | $0 |
| Lifecycle envelope (yr 1–25, low scenario) | **$476 M cumulative** | $101 |
| Lifecycle envelope (yr 1–25, high scenario) | **$476 M cumulative** | $101 |
| Lifecycle envelope (yr 1–25, cost-neutral after opening) | **$476 M cumulative** | $101 |

_Population basis: 4,700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the cost-neutral case already covers steady-state OPEX + debt service from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $891 M | 3.8% | 25 y, 5 y grace | $64 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $371 M | 4.5% | 25 y, 5 y grace | $29 M / yr |
| Government equity (no debt service) | 15% | $223 M | — | — | — |
| **Total** | **100%** | **$1.48 bn** | | | **$93 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $34 M / yr + bonds $17 M / yr = **$51 M / yr** total — plus the equity tranche amortised across construction ($45 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $21 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $16 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $305 k |
| Traction energy (1376.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,448 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $70 M |
| **OPEX subtotal** | | **$107 M / yr** |

_Annual fleet utilisation: 292 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 57.4 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The cost-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $2.83 |
| Cost-neutral single-trip fare (6 % pass) | $3.40 |
| Day pass (3 trips) | $8.67 (15 % bulk discount) |
| Monthly unlimited pass | $102.00 (~6 % of median monthly income) |
| Annual pass | $1122.00 (11 × monthly = ~1 free month) |

### Revenue & cost-neutrality

Planning ridership bracket = 8–15 % of urban population × 365 service-days at the cost-neutral fare. The cost-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = OPEX + post-grace debt service**.

| | Low scenario | High scenario | Cost-neutral target |
|---|---|---|---|
| Daily paid trips | 376,000 | 705,000 | 63,255 |
| Daily paid trips / population | 8% | 15% | 1% |
| Annual paid trips | 137.2 M | 257.3 M | 23.1 M |
| Farebox revenue | $467 M / yr | $875 M / yr | $79 M / yr |
| Station shop leases | $37 M / yr | $37 M / yr | $37 M / yr |
| Advertising boards | $85 M / yr | $85 M / yr | $85 M / yr |
| **Total revenue** | **$588 M / yr** | **$997 M / yr** | **$200 M / yr** |
| Revenue / OPEX + debt-service recovery | 294% | 498% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Remaining steady-state gov gap | $0 k / yr | $0 k / yr | **$0 / yr** |
| Operating surplus after OPEX + debt | $388 M / yr | $796 M / yr | $0 / yr |

_Commercial-revenue assumptions: 38,528 m² of station shop/kiosk leases at $90/m²/month and 7,016 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % cost-neutral fare target, the 8–15 % daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

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
