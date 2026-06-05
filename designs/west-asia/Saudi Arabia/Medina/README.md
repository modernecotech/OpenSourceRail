# Medina — Urban Rail Network

**Country:** SA · **Population:** 1,500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Medina rail network on OpenStreetMap](medina-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`medina.corridor.geojson`](medina.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 103 |
| Interchange stations | 14 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 47.0% |
| Route length (double track) | 211.5 km |
| Revenue fleet | 153 × 4-car trainsets |
| Spare + cold-reserve | 18 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 34.4 km | 19 | 28 | NE Outer ↔ SW Outer |
| line-2 | 31.4 km | 18 | 26 | W Outer ↔ E Outer |
| line-3 | 27.7 km | 15 | 24 | N Mid ↔ SE Outer |
| line-4 | 40.1 km | 20 | 32 | E Outer ↔ W Outer |
| line-5 | 77.9 km | 32 | 61 | W Outer ↔ W Outer |
| **Total** | **211.5 km** | **103 unique** | **171** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 320 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 430 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 320 AW2 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 320 × 12 = **3,840 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 3,840 = **38,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **384,000 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **249,600 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **126,900 – 211,500 trips/day**

## Catchment

- City population: **1,500,000**
- Anchor-weighted coverage: 47.0%
- Catchment population: **≈ 705,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 14 | 500 kW | 3000 kWh |
| Major | 42 | 400 kW | 2500 kWh |
| Standard | 33 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **97** | **42,200 kW** | **274,000 kWh** |

Aggregate station-rail charging power: **54,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 677 kWh | 42.3 km average line length |
| Onboard battery coverage | 0.7× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 527 kW average charger across stops |
| Stops to refill one trainset pack | 55 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 211 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 274 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (196.9 km @ $2.0 M/km) | $394 M |
| Elevated (13.8 km @ $9.0 M/km) | $124 M |
| Elevated-interchange premium (11 sites @ $4.50 M) | $50 M |
| **Civil subtotal** | **$567 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 7 | $300 k | $2.1 M |
| `standard` | 33 | $800 k | $26 M |
| `major` | 42 | $1.60 M | $67 M |
| `terminal` | 7 | $1.40 M | $9.8 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 14 | $3.50 M | $49 M |
| **Stations subtotal** | | | **$156 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 7 | $2.0 M | $14 M |
| **Depots subtotal** | | | **$26 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 171 | $1.07 M | $182 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 211.5 km × $0.015 M/km | $11 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $44 M |
| EPC integration + project management (7%) | on subtotal | $69 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $567 M |
| Stations | $156 M |
| Depots | $26 M |
| Rolling stock | $182 M |
| Residual train-control wayside + charging microgrids | $55 M |
| EPC overhead (7%) | $69 M |
| **CAPEX total** | **$1.06 bn** |
| Per-route-km | $5.0 M / km |
| Per-capita (city pop) | $704 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh medina`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$68 M / yr** | $45 |
| Steady-state, low-ridership (year 6+) | **$66 M / yr** | $44 |
| Steady-state, high-ridership (year 6+) | **$66 M / yr** | $44 |
| Steady-state, operating-neutral revenue case | **$66 M / yr** | $44 |
| Lifecycle envelope (yr 1–25, low scenario) | **$1.66 bn cumulative** | $1,107 |
| Lifecycle envelope (yr 1–25, high scenario) | **$1.66 bn cumulative** | $1,107 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$1.66 bn cumulative** | $1,107 |

_Population basis: 1,500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $634 M | 3.8% | 25 y, 5 y grace | $46 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $264 M | 4.5% | 25 y, 5 y grace | $20 M / yr |
| Government equity (no debt service) | 15% | $158 M | — | — | — |
| **Total** | **100%** | **$1.06 bn** | | | **$66 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $24 M / yr + bonds $12 M / yr = **$36 M / yr** total — plus the equity tranche amortised across construction ($32 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $7.3 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $15 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $527 k |
| Traction energy (480.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,281 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $37 M |
| **OPEX subtotal** | | **$59 M / yr** |

_Annual fleet utilisation: 153 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 30.1 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $2.83 |
| Operating-neutral single-trip fare (6 % pass) | $3.40 |
| Day pass (3 trips) | $8.67 (15 % bulk discount) |
| Monthly unlimited pass | $102.00 (~6 % of median monthly income) |
| Annual pass | $1122.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (249,600 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 126,900 | 211,500 | 2,335 |
| Daily paid trips / catchment | 18% | 30% | 0% |
| Daily paid trips / city population | 8% | 14% | 0% |
| Annual paid trips | 46.3 M | 77.2 M | 0.9 M |
| Farebox revenue | $157 M / yr | $262 M / yr | $2.9 M / yr |
| Station shop leases | $17 M / yr | $17 M / yr | $17 M / yr |
| Advertising boards | $40 M / yr | $40 M / yr | $40 M / yr |
| **Total revenue** | **$214 M / yr** | **$319 M / yr** | **$59 M / yr** |
| Revenue / OPEX recovery | 360% | 537% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Remaining steady-state gov commitment | $66 M / yr | $66 M / yr | **$66 M / yr** |
| Operating surplus after OPEX | $155 M / yr | $260 M / yr | $0 / yr |

_Commercial-revenue assumptions: 17,672 m² of station shop/kiosk leases at $90/m²/month and 3,272 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`medina.toml`](medina.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`medina-network-map.png`](medina-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`medina.corridor.geojson`](medina.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`medina.stations.json`](medina.stations.json) | Machine-readable station list |
| [`medina.design-quality.yaml`](medina.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug medina

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug medina \
    --sidecar .cache/osr-pipeline/rasters/medina.grid.json \
    --out-dir designs/.../Medina

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../medina.toml \
    --out designs/.../README.md
```

`scripts/regenerate-medina.sh` chains steps 3 + drift tests into a single command.
