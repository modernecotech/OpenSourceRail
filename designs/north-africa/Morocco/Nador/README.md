# Nador — Urban Rail Network

**Country:** MA · **Population:** 250,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Nador rail network on OpenStreetMap](nador-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`nador.corridor.geojson`](nador.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 19 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 69.6% |
| Route length (double track) | 34.3 km |
| Revenue fleet | 42 × 2-car trainsets |
| Spare + cold-reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 10.0 km | 6 | 15 | E Mid ↔ W Outer |
| line-2 | 15.4 km | 7 | 20 | NW Outer ↔ SE Mid |
| line-3 |  9.0 km | 6 | 13 | SE Outer ↔ N Inner |
| **Total** | **34.3 km** | **19 unique** | **48** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 160 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 210 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 160 AW2 passengers (`tram-2car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 160 × 12 = **1,920 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 1,920 = **11,520 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **115,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **74,880 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **31,320 – 52,200 trips/day**

## Catchment

- City population: **250,000**
- Anchor-weighted coverage: 69.6%
- Catchment population: **≈ 174,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 2 | 400 kW | 2500 kWh |
| Standard | 7 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **18** | **11,900 kW** | **83,000 kWh** |

Aggregate station-rail charging power: **12,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 91 kWh | 11.4 km average line length |
| Onboard battery coverage | 2.6× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.7 kWh/stop | 645 kW average charger across stops |
| Stops to refill one trainset pack | 22 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 60 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 83 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (33.0 km @ $2.0 M/km) | $66 M |
| Elevated (1.3 km @ $9.0 M/km) | $11 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$82 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $300 k | $300 k |
| `standard` | 7 | $800 k | $5.6 M |
| `major` | 2 | $1.60 M | $3.2 M |
| `terminal` | 5 | $1.40 M | $7.0 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 3 | $3.50 M | $10 M |
| **Stations subtotal** | | | **$29 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 5 | $2.0 M | $10 M |
| **Depots subtotal** | | | **$22 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 48 | $534 k | $26 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 34.3 km × $0.015 M/km | $1.7 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $8.8 M |
| EPC integration + project management (7%) | on subtotal | $12 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $82 M |
| Stations | $29 M |
| Depots | $22 M |
| Rolling stock | $26 M |
| Residual train-control wayside + charging microgrids | $11 M |
| EPC overhead (7%) | $12 M |
| **CAPEX total** | **$180 M** |
| Per-route-km | $5.3 M / km |
| Per-capita (city pop) | $722 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh nador`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$12 M / yr** | $46 |
| Steady-state, low-ridership (year 6+) | **$11 M / yr** | $45 |
| Steady-state, high-ridership (year 6+) | **$11 M / yr** | $45 |
| Steady-state, operating-neutral revenue case | **$11 M / yr** | $45 |
| Lifecycle envelope (yr 1–25, low scenario) | **$284 M cumulative** | $1,134 |
| Lifecycle envelope (yr 1–25, high scenario) | **$284 M cumulative** | $1,134 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$284 M cumulative** | $1,134 |

_Population basis: 250,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $108 M | 3.8% | 25 y, 5 y grace | $7.8 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $45 M | 4.5% | 25 y, 5 y grace | $3.5 M / yr |
| Government equity (no debt service) | 15% | $27 M | — | — | — |
| **Total** | **100%** | **$180 M** | | | **$11 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $4.1 M / yr + bonds $2.0 M / yr = **$6.1 M / yr** total — plus the equity tranche amortised across construction ($5.4 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $1.0 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $2.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $86 k |
| Traction energy (41.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (218 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $1.5 M |
| **OPEX subtotal** | | **$5.3 M / yr** |

_Annual fleet utilisation: 42 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 5.2 M train-km / yr (~123 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$410 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.68 |
| Operating-neutral single-trip fare (6 % pass) | $0.82 |
| Day pass (3 trips) | $2.09 (15 % bulk discount) |
| Monthly unlimited pass | $24.60 (~6 % of median monthly income) |
| Annual pass | $270.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (74,880 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 31,320 | 52,200 | 7,992 |
| Daily paid trips / catchment | 18% | 30% | 5% |
| Daily paid trips / city population | 13% | 21% | 3% |
| Annual paid trips | 11.4 M | 19.1 M | 2.9 M |
| Farebox revenue | $9.4 M / yr | $16 M / yr | $2.4 M / yr |
| Station shop leases | $1.1 M / yr | $1.1 M / yr | $1.1 M / yr |
| Advertising boards | $1.8 M / yr | $1.8 M / yr | $1.8 M / yr |
| **Total revenue** | **$12 M / yr** | **$18 M / yr** | **$5.3 M / yr** |
| Revenue / OPEX recovery | 233% | 352% | 100% |
| Country farebox-only policy target (diagnostic) | 60% | 60% | 60% |
| Remaining steady-state gov commitment | $11 M / yr | $11 M / yr | **$11 M / yr** |
| Operating surplus after OPEX | $7.0 M / yr | $13 M / yr | $0 / yr |

_Commercial-revenue assumptions: 3,144 m² of station shop/kiosk leases at $33/m²/month and 608 advertising boards at $287/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`nador.toml`](nador.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`nador-network-map.png`](nador-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`nador.corridor.geojson`](nador.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`nador.stations.json`](nador.stations.json) | Machine-readable station list |
| [`nador.design-quality.yaml`](nador.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug nador

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug nador \
    --sidecar .cache/osr-pipeline/rasters/nador.grid.json \
    --out-dir designs/.../Nador

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../nador.toml \
    --out designs/.../README.md
```

`scripts/regenerate-nador.sh` chains steps 3 + drift tests into a single command.
