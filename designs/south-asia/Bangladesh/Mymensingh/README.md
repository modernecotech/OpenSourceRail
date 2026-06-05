# Mymensingh — Urban Rail Network

**Country:** BD · **Population:** 700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Mymensingh rail network on OpenStreetMap](mymensingh-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`mymensingh.corridor.geojson`](mymensingh.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 37 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 41.1% |
| Route length (double track) | 67.3 km |
| Revenue fleet | 59 × 3-car trainsets |
| Spare + cold-reserve | 8 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 25.1 km | 15 | 25 | E Outer ↔ W Outer |
| line-2 | 18.3 km | 11 | 18 | N Mid ↔ S Outer |
| line-3 | 23.9 km | 11 | 24 | NE Outer ↔ S Outer |
| **Total** | **67.3 km** | **37 unique** | **67** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 57 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 330 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 420 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 330 AW2 passengers (`light-metro-3car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 330 × 12 = **3,960 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 3,960 = **23,760 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **237,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **28,770 – 43,155 trips/day**

## Catchment

- City population: **700,000**
- Anchor-weighted coverage: 41.1%
- Catchment population: **≈ 287,700** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 5 | 400 kW | 2500 kWh |
| Standard | 22 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **35** | **17,100 kW** | **117,500 kWh** |

Aggregate station-rail charging power: **21,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 269 kWh | 22.4 km average line length |
| Onboard battery coverage | 1.3× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.5 kWh/stop | 568 kW average charger across stops |
| Stops to refill one trainset pack | 38 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 86 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 118 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (35.3 km @ $1.2 M/km) | $42 M |
| Elevated (31.9 km @ $5.5 M/km) | $176 M |
| **Civil subtotal** | **$218 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | $180 k | $360 k |
| `standard` | 22 | $450 k | $9.9 M |
| `major` | 5 | $900 k | $4.5 M |
| `terminal` | 5 | $800 k | $4.0 M |
| `depot-terminal` | 1 | $1.00 M | $1.0 M |
| `interchange` | 2 | $1.35 M | $2.7 M |
| **Stations subtotal** | | | **$22 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $7.50 M | $7.5 M |
| `layup-minimal` | 5 | $900 k | $4.5 M |
| **Depots subtotal** | | | **$12 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 67 | $800 k | $54 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 67.3 km × $0.015 M/km | $1.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $7.1 M |
| EPC integration + project management (7%) | on subtotal | $22 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $218 M |
| Stations | $22 M |
| Depots | $12 M |
| Rolling stock | $54 M |
| Residual train-control wayside + charging microgrids | $8.1 M |
| EPC overhead (7%) | $22 M |
| **CAPEX total** | **$336 M** |
| Per-route-km | $5.0 M / km |
| Per-capita (city pop) | $480 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh mymensingh`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$22 M / yr** | $31 |
| Steady-state, low-ridership (year 8+) | **$20 M / yr** | $29 |
| Steady-state, high-ridership (year 8+) | **$13 M / yr** | $19 |
| Steady-state, cost-neutral revenue case | **$0 / yr** | $0 |
| Lifecycle envelope (yr 1–30, low scenario) | **$624 M cumulative** | $891 |
| Lifecycle envelope (yr 1–30, high scenario) | **$463 M cumulative** | $662 |
| Lifecycle envelope (yr 1–30, cost-neutral after opening) | **$154 M cumulative** | $220 |

_Population basis: 700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the cost-neutral case already covers steady-state OPEX + debt service from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $202 M | 3.8% | 30 y, 7 y grace | $13 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $84 M | 8.5% | 30 y, 7 y grace | $8.4 M / yr |
| Government equity (no debt service) | 15% | $50 M | — | — | — |
| **Total** | **100%** | **$336 M** | | | **$22 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $7.7 M / yr + bonds $7.1 M / yr = **$15 M / yr** total — plus the equity tranche amortised across construction ($7.2 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $2.1 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $5.0 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $50 k |
| Traction energy (119.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (416 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $1.4 M |
| **OPEX subtotal** | | **$8.6 M / yr** |

_Annual fleet utilisation: 59 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 9.9 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$195 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The cost-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.33 |
| Cost-neutral single-trip fare (6 % pass) | $0.39 |
| Day pass (3 trips) | $0.99 (15 % bulk discount) |
| Monthly unlimited pass | $11.70 (~6 % of median monthly income) |
| Annual pass | $128.70 (11 × monthly = ~1 free month) |

### Revenue & cost-neutrality

Planning ridership bracket = 8–15 % of urban population × 365 service-days at the cost-neutral fare. The cost-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = OPEX + post-grace debt service**.

| | Low scenario | High scenario | Cost-neutral target |
|---|---|---|---|
| Daily paid trips | 56,000 | 105,000 | 199,465 |
| Daily paid trips / population | 8% | 15% | 28% |
| Annual paid trips | 20.4 M | 38.3 M | 72.8 M |
| Farebox revenue | $8.0 M / yr | $15 M / yr | $28 M / yr |
| Station shop leases | $717 k / yr | $717 k / yr | $717 k / yr |
| Advertising boards | $1.2 M / yr | $1.2 M / yr | $1.2 M / yr |
| **Total revenue** | **$9.9 M / yr** | **$17 M / yr** | **$30 M / yr** |
| Revenue / OPEX + debt-service recovery | 33% | 56% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Remaining steady-state gov gap | $20 M / yr | $13 M / yr | **$0 / yr** |
| Operating surplus after OPEX + debt | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 4,352 m² of station shop/kiosk leases at $16/m²/month and 880 advertising boards at $136/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % cost-neutral fare target, the 8–15 % daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`mymensingh.toml`](mymensingh.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`mymensingh-network-map.png`](mymensingh-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`mymensingh.corridor.geojson`](mymensingh.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`mymensingh.stations.json`](mymensingh.stations.json) | Machine-readable station list |
| [`mymensingh.design-quality.yaml`](mymensingh.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug mymensingh

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug mymensingh \
    --sidecar .cache/osr-pipeline/rasters/mymensingh.grid.json \
    --out-dir designs/.../Mymensingh

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../mymensingh.toml \
    --out designs/.../README.md
```

`scripts/regenerate-mymensingh.sh` chains steps 3 + drift tests into a single command.
