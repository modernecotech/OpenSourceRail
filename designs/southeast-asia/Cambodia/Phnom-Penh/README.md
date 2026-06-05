# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 106 |
| Interchange stations | 23 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 48.3% |
| Route length (double track) | 227.7 km |
| Revenue fleet | 166 × 4-car trainsets |
| Spare + cold-reserve | 20 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 38.6 km | 18 | 31 | SE Outer ↔ N Outer |
| line-2 | 31.4 km | 16 | 26 | E Outer ↔ W Mid |
| line-3 | 28.1 km | 11 | 24 | N Mid ↔ SW Mid |
| line-4 | 25.9 km | 15 | 21 | SW Mid ↔ NE Mid |
| line-5 | 41.2 km | 18 | 34 | NW Outer ↔ SE Outer |
| line-6 | 62.4 km | 29 | 50 | W Mid ↔ W Mid |
| **Total** | **227.7 km** | **106 unique** | **186** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 440 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 560 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 440 AW2 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 440 × 12 = **5,280 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 5,280 = **63,360 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **633,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **110,172 – 165,258 trips/day**

## Catchment

- City population: **2,281,000**
- Anchor-weighted coverage: 48.3%
- Catchment population: **≈ 1,101,723** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 23 | 500 kW | 3000 kWh |
| Major | 25 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **104** | **44,800 kW** | **290,500 kWh** |

Aggregate station-rail charging power: **57,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 607 kWh | 37.9 km average line length |
| Onboard battery coverage | 0.8× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 545 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 224 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 290 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (186.2 km @ $1.2 M/km) | $223 M |
| Elevated (40.2 km @ $5.5 M/km) | $221 M |
| Elevated-interchange premium (8 sites @ $2.5 M) | $20 M |
| **Civil subtotal** | **$465 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $180 k | $540 k |
| `standard` | 46 | $450 k | $21 M |
| `major` | 25 | $900 k | $22 M |
| `terminal` | 9 | $800 k | $7.2 M |
| `depot-terminal` | 1 | $1.00 M | $1.0 M |
| `interchange` | 10 | $1.35 M | $14 M |
| `interchange-elevated` | 13 | $1.80 M | $23 M |
| **Stations subtotal** | | | **$89 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $7.50 M | $7.5 M |
| `layup-minimal` | 9 | $900 k | $8.1 M |
| **Depots subtotal** | | | **$16 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 186 | $1.07 M | $198 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 227.7 km × $0.015 M/km | $3.4 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $24 M |
| EPC integration + project management (7%) | on subtotal | $56 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $465 M |
| Stations | $89 M |
| Depots | $16 M |
| Rolling stock | $198 M |
| Residual train-control wayside + charging microgrids | $28 M |
| EPC overhead (7%) | $56 M |
| **CAPEX total** | **$851 M** |
| Per-route-km | $3.7 M / km |
| Per-capita (city pop) | $373 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh phnom-penh`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$56 M / yr** | $24 |
| Steady-state, low-ridership (year 8+) | **$42 M / yr** | $18 |
| Steady-state, high-ridership (year 8+) | **$17 M / yr** | $7 |
| Steady-state, cost-neutral revenue case | **$0 / yr** | $0 |
| Lifecycle envelope (yr 1–30, low scenario) | **$1.36 bn cumulative** | $595 |
| Lifecycle envelope (yr 1–30, high scenario) | **$781 M cumulative** | $342 |
| Lifecycle envelope (yr 1–30, cost-neutral after opening) | **$390 M cumulative** | $171 |

_Population basis: 2,281,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the cost-neutral case already covers steady-state OPEX + debt service from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $510 M | 4.0% | 30 y, 7 y grace | $34 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $213 M | 8.0% | 30 y, 7 y grace | $21 M / yr |
| Government equity (no debt service) | 15% | $128 M | — | — | — |
| **Total** | **100%** | **$851 M** | | | **$55 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $20 M / yr + bonds $17 M / yr = **$37 M / yr** total — plus the equity tranche amortised across construction ($18 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $7.9 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $11 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $171 k |
| Traction energy (521.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,378 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $5.0 M |
| **OPEX subtotal** | | **$24 M / yr** |

_Annual fleet utilisation: 166 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 32.6 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$215 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The cost-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.36 |
| Cost-neutral single-trip fare (6 % pass) | $0.43 |
| Day pass (3 trips) | $1.10 (15 % bulk discount) |
| Monthly unlimited pass | $12.90 (~6 % of median monthly income) |
| Annual pass | $141.90 (11 × monthly = ~1 free month) |

### Revenue & cost-neutrality

Planning ridership bracket = 8–15 % of urban population × 365 service-days at the cost-neutral fare. The cost-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = OPEX + post-grace debt service**.

| | Low scenario | High scenario | Cost-neutral target |
|---|---|---|---|
| Daily paid trips | 182,480 | 342,150 | 450,514 |
| Daily paid trips / population | 8% | 15% | 20% |
| Annual paid trips | 66.6 M | 124.9 M | 164.4 M |
| Farebox revenue | $29 M / yr | $54 M / yr | $71 M / yr |
| Station shop leases | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| Advertising boards | $5.3 M / yr | $5.3 M / yr | $5.3 M / yr |
| **Total revenue** | **$37 M / yr** | **$62 M / yr** | **$79 M / yr** |
| Revenue / OPEX + debt-service recovery | 47% | 79% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov gap | $42 M / yr | $17 M / yr | **$0 / yr** |
| Operating surplus after OPEX + debt | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 18,536 m² of station shop/kiosk leases at $17/m²/month and 3,428 advertising boards at $150/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % cost-neutral fare target, the 8–15 % daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`phnom-penh-network-map.png`](phnom-penh-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`phnom-penh.stations.json`](phnom-penh.stations.json) | Machine-readable station list |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug phnom-penh

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug phnom-penh \
    --sidecar .cache/osr-pipeline/rasters/phnom-penh.grid.json \
    --out-dir designs/.../Phnom-Penh

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../phnom-penh.toml \
    --out designs/.../README.md
```

`scripts/regenerate-phnom-penh.sh` chains steps 3 + drift tests into a single command.
