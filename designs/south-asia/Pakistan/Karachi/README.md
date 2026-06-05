# Karachi — Urban Rail Network

**Country:** PK · **Population:** 20,300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Karachi rail network on OpenStreetMap](karachi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`karachi.corridor.geojson`](karachi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 231 |
| Interchange stations | 33 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 48.4% |
| Route length (double track) | 472.3 km |
| Revenue fleet | 337 × 6-car trainsets |
| Spare + cold-reserve | 40 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 57.8 km | 27 | 46 | NW Outer ↔ E Outer |
| line-2 | 47.2 km | 25 | 38 | W Outer ↔ SE Mid |
| line-3 | 45.5 km | 23 | 37 | N Outer ↔ SW Mid |
| line-4 | 46.3 km | 21 | 37 | E Mid ↔ W Outer |
| line-5 | 46.2 km | 25 | 37 | NE Outer ↔ S Mid |
| line-6 | 46.1 km | 24 | 37 | N Outer ↔ S Mid |
| line-7 | 37.4 km | 19 | 30 | W Mid ↔ E Outer |
| line-8 | 41.7 km | 16 | 34 | NE Outer ↔ SE Mid |
| line-9 | 104.1 km | 51 | 81 | NW Mid ↔ NW Mid |
| **Total** | **472.3 km** | **231 unique** | **377** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 720 × 12 = **8,640 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 8,640 = **155,520 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,555,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **1,010,880 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment (capped by practical service capacity)): ≈ **1,010,880 – 1,010,880 trips/day**

## Catchment

- City population: **20,300,000**
- Anchor-weighted coverage: 48.4%
- Catchment population: **≈ 9,825,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 33 | 500 kW | 3000 kWh |
| Major | 94 | 400 kW | 2500 kWh |
| Standard | 83 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **226** | **91,500 kW** | **585,000 kWh** |

Aggregate station-rail charging power: **122,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,259 kWh | 52.5 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 529 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 458 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 585 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (435.6 km @ $3.0 M/km) | $1.31 bn |
| Elevated (34.7 km @ $12.0 M/km) | $416 M |
| Elevated-interchange premium (25 sites @ $4.50 M) | $112 M |
| **Civil subtotal** | **$1.84 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | $300 k | $1.5 M |
| `standard` | 83 | $800 k | $66 M |
| `major` | 94 | $1.60 M | $150 M |
| `terminal` | 15 | $1.40 M | $21 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 33 | $3.50 M | $116 M |
| **Stations subtotal** | | | **$357 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 15 | $2.0 M | $30 M |
| **Depots subtotal** | | | **$42 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 377 | $1.60 M | $603 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 472.3 km × $0.050 M/km | $24 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $100 M |
| EPC integration + project management (7%) | on subtotal | $207 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.84 bn |
| Stations | $357 M |
| Depots | $42 M |
| Rolling stock | $603 M |
| Residual train-control wayside + charging microgrids | $124 M |
| EPC overhead (7%) | $207 M |
| **CAPEX total** | **$3.17 bn** |
| Per-route-km | $6.7 M / km |
| Per-capita (city pop) | $156 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh karachi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$275 M / yr** | $14 |
| Steady-state, low-ridership (year 8+) | **$263 M / yr** | $13 |
| Steady-state, high-ridership (year 8+) | **$263 M / yr** | $13 |
| Steady-state, operating-neutral revenue case | **$263 M / yr** | $13 |
| Lifecycle envelope (yr 1–30, low scenario) | **$7.97 bn cumulative** | $392 |
| Lifecycle envelope (yr 1–30, high scenario) | **$7.97 bn cumulative** | $392 |
| Lifecycle envelope (yr 1–30, operating-neutral after opening) | **$7.97 bn cumulative** | $392 |

_Population basis: 20,300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $1.90 bn | 4.0% | 30 y, 7 y grace | $128 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $792 M | 16.5% | 30 y, 7 y grace | $135 M / yr |
| Government equity (no debt service) | 15% | $475 M | — | — | — |
| **Total** | **100%** | **$3.17 bn** | | | **$263 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $76 M / yr + bonds $131 M / yr = **$207 M / yr** total — plus the equity tranche amortised across construction ($68 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $24 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $45 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.2 M |
| Traction energy (1588.6 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,846 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $7.9 M |
| **OPEX subtotal** | | **$78 M / yr** |

_Annual fleet utilisation: 337 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 66.2 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.28 |
| Operating-neutral single-trip fare (6 % pass) | $0.33 |
| Day pass (3 trips) | $0.84 (15 % bulk discount) |
| Monthly unlimited pass | $9.90 (~6 % of median monthly income) |
| Annual pass | $108.90 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (1,010,880 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 1,010,880 | 1,010,880 | 526,764 |
| Daily paid trips / catchment | 10% | 10% | 5% |
| Daily paid trips / city population | 5% | 5% | 3% |
| Annual paid trips | 369.0 M | 369.0 M | 192.3 M |
| Farebox revenue | $122 M / yr | $122 M / yr | $63 M / yr |
| Station shop leases | $5.6 M / yr | $5.6 M / yr | $5.6 M / yr |
| Advertising boards | $8.8 M / yr | $8.8 M / yr | $8.8 M / yr |
| **Total revenue** | **$136 M / yr** | **$136 M / yr** | **$78 M / yr** |
| Revenue / OPEX recovery | 175% | 175% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov commitment | $263 M / yr | $263 M / yr | **$263 M / yr** |
| Operating surplus after OPEX | $58 M / yr | $58 M / yr | $0 / yr |

_Commercial-revenue assumptions: 40,488 m² of station shop/kiosk leases at $13/m²/month and 7,472 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`karachi.toml`](karachi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`karachi-network-map.png`](karachi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`karachi.corridor.geojson`](karachi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`karachi.stations.json`](karachi.stations.json) | Machine-readable station list |
| [`karachi.design-quality.yaml`](karachi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug karachi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug karachi \
    --sidecar .cache/osr-pipeline/rasters/karachi.grid.json \
    --out-dir designs/.../Karachi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../karachi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-karachi.sh` chains steps 3 + drift tests into a single command.
