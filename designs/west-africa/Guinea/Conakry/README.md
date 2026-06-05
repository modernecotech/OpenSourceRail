# Conakry — Urban Rail Network

**Country:** GN · **Population:** 2,010,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Conakry rail network on OpenStreetMap](conakry-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`conakry.corridor.geojson`](conakry.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 54 |
| Interchange stations | 6 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 40.2% |
| Route length (double track) | 93.2 km |
| Revenue fleet | 69 × 4-car trainsets |
| Spare + cold-reserve | 9 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 30.1 km | 20 | 25 | NE Outer ↔ SW Outer |
| line-2 | 16.1 km | 12 | 15 | SW Inner ↔ NE Mid |
| line-3 | 46.9 km | 23 | 38 | NE Mid ↔ NE Mid |
| **Total** | **93.2 km** | **54 unique** | **78** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 480 × 12 = **5,760 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 5,760 = **34,560 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **345,600 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **224,640 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment (capped by practical service capacity)): ≈ **145,443 – 224,640 trips/day**

## Catchment

- City population: **2,010,000**
- Anchor-weighted coverage: 40.2%
- Catchment population: **≈ 808,020** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 6 | 500 kW | 3000 kWh |
| Major | 33 | 400 kW | 2500 kWh |
| Standard | 12 | 300 kW | 2000 kWh |
| Terminal | 3 | 500 kW | 3000 kWh |
| **Total installed** | **55** | **26,300 kW** | **173,500 kWh** |

Aggregate station-rail charging power: **29,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 497 kWh | 31.1 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 546 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 132 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 174 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (88.1 km @ $3.0 M/km) | $264 M |
| Elevated (3.5 km @ $12.0 M/km) | $42 M |
| Elevated-interchange premium (3 sites @ $4.50 M) | $14 M |
| **Civil subtotal** | **$320 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 12 | $800 k | $9.6 M |
| `major` | 33 | $1.60 M | $53 M |
| `terminal` | 3 | $1.40 M | $4.2 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 6 | $3.50 M | $21 M |
| **Stations subtotal** | | | **$90 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 3 | $2.0 M | $6.0 M |
| **Depots subtotal** | | | **$18 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 78 | $1.07 M | $83 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 93.2 km × $0.050 M/km | $4.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $25 M |
| EPC integration + project management (7%) | on subtotal | $38 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $320 M |
| Stations | $90 M |
| Depots | $18 M |
| Rolling stock | $83 M |
| Residual train-control wayside + charging microgrids | $30 M |
| EPC overhead (7%) | $38 M |
| **CAPEX total** | **$579 M** |
| Per-route-km | $6.2 M / km |
| Per-capita (city pop) | $288 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh conakry`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$34 M / yr** | $17 |
| Steady-state, low-ridership (year 11+) | **$36 M / yr** | $18 |
| Steady-state, high-ridership (year 11+) | **$36 M / yr** | $18 |
| Steady-state, operating-neutral revenue case | **$36 M / yr** | $18 |
| Lifecycle envelope (yr 1–35, low scenario) | **$1.23 bn cumulative** | $613 |
| Lifecycle envelope (yr 1–35, high scenario) | **$1.23 bn cumulative** | $613 |
| Lifecycle envelope (yr 1–35, operating-neutral after opening) | **$1.23 bn cumulative** | $613 |

_Population basis: 2,010,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $347 M | 3.0% | 35 y, 10 y grace | $20 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $145 M | 10.0% | 35 y, 10 y grace | $16 M / yr |
| Government equity (no debt service) | 15% | $87 M | — | — | — |
| **Total** | **100%** | **$579 M** | | | **$36 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $10 M / yr + bonds $14 M / yr = **$25 M / yr** total — plus the equity tranche amortised across construction ($8.7 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $3.3 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $8.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $229 k |
| Traction energy (216.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (571 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $1.2 M |
| **OPEX subtotal** | | **$13 M / yr** |

_Annual fleet utilisation: 69 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 13.6 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$130 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.22 |
| Operating-neutral single-trip fare (6 % pass) | $0.26 |
| Day pass (3 trips) | $0.66 (15 % bulk discount) |
| Monthly unlimited pass | $7.80 (~6 % of median monthly income) |
| Annual pass | $85.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (224,640 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 145,443 | 224,640 | 109,924 |
| Daily paid trips / catchment | 18% | 28% | 14% |
| Daily paid trips / city population | 7% | 11% | 5% |
| Annual paid trips | 53.1 M | 82.0 M | 40.1 M |
| Farebox revenue | $14 M / yr | $21 M / yr | $10 M / yr |
| Station shop leases | $1.1 M / yr | $1.1 M / yr | $1.1 M / yr |
| Advertising boards | $1.8 M / yr | $1.8 M / yr | $1.8 M / yr |
| **Total revenue** | **$17 M / yr** | **$24 M / yr** | **$13 M / yr** |
| Revenue / OPEX recovery | 125% | 182% | 100% |
| Country farebox-only policy target (diagnostic) | 35% | 35% | 35% |
| Remaining steady-state gov commitment | $36 M / yr | $36 M / yr | **$36 M / yr** |
| Operating surplus after OPEX | $3.4 M / yr | $11 M / yr | $0 / yr |

_Commercial-revenue assumptions: 10,464 m² of station shop/kiosk leases at $10/m²/month and 1,912 advertising boards at $91/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`conakry.toml`](conakry.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`conakry-network-map.png`](conakry-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`conakry.corridor.geojson`](conakry.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`conakry.stations.json`](conakry.stations.json) | Machine-readable station list |
| [`conakry.design-quality.yaml`](conakry.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug conakry

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug conakry \
    --sidecar .cache/osr-pipeline/rasters/conakry.grid.json \
    --out-dir designs/.../Conakry

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../conakry.toml \
    --out designs/.../README.md
```

`scripts/regenerate-conakry.sh` chains steps 3 + drift tests into a single command.
