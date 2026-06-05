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
| Lines | 6 |
| Unique stations | 122 |
| Interchange stations | 13 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 33.8% |
| Route length (double track) | 235.6 km |
| Revenue fleet | 172 × 6-car trainsets |
| Spare + cold-reserve | 20 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 35.8 km | 20 | 29 | S Outer ↔ N Outer |
| line-2 | 39.5 km | 20 | 32 | NE Outer ↔ SW Outer |
| line-3 | 31.1 km | 17 | 26 | SW Outer ↔ N Outer |
| line-4 | 36.5 km | 17 | 30 | NE Outer ↔ S Mid |
| line-5 | 33.0 km | 20 | 27 | E Outer ↔ NW Mid |
| line-6 | 59.7 km | 29 | 48 | NE Mid ↔ NE Mid |
| **Total** | **235.6 km** | **122 unique** | **192** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 480 × 12 = **5,760 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 5,760 = **69,120 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **691,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **449,280 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **184,771 – 307,951 trips/day**

## Catchment

- City population: **3,037,000**
- Anchor-weighted coverage: 33.8%
- Catchment population: **≈ 1,026,506** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 13 | 500 kW | 3000 kWh |
| Major | 57 | 400 kW | 2500 kWh |
| Standard | 42 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **122** | **51,400 kW** | **332,500 kWh** |

Aggregate station-rail charging power: **66,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 942 kWh | 39.3 km average line length |
| Onboard battery coverage | 0.8× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 543 kW average charger across stops |
| Stops to refill one trainset pack | 80 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 257 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 332 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (223.5 km @ $2.0 M/km) | $447 M |
| Elevated (10.4 km @ $9.0 M/km) | $94 M |
| Elevated-interchange premium (9 sites @ $4.50 M) | $40 M |
| **Civil subtotal** | **$581 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $300 k | $300 k |
| `standard` | 42 | $800 k | $34 M |
| `major` | 57 | $1.60 M | $91 M |
| `terminal` | 9 | $1.40 M | $13 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 13 | $3.50 M | $46 M |
| **Stations subtotal** | | | **$185 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 9 | $2.0 M | $18 M |
| **Depots subtotal** | | | **$30 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 192 | $1.60 M | $307 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 235.6 km × $0.015 M/km | $12 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $53 M |
| EPC integration + project management (7%) | on subtotal | $82 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $581 M |
| Stations | $185 M |
| Depots | $30 M |
| Rolling stock | $307 M |
| Residual train-control wayside + charging microgrids | $65 M |
| EPC overhead (7%) | $82 M |
| **CAPEX total** | **$1.25 bn** |
| Per-route-km | $5.3 M / km |
| Per-capita (city pop) | $412 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh lusaka`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$107 M / yr** | $35 |
| Steady-state, low-ridership (year 8+) | **$104 M / yr** | $34 |
| Steady-state, high-ridership (year 8+) | **$103 M / yr** | $34 |
| Steady-state, operating-neutral revenue case | **$103 M / yr** | $34 |
| Lifecycle envelope (yr 1–30, low scenario) | **$3.14 bn cumulative** | $1,033 |
| Lifecycle envelope (yr 1–30, high scenario) | **$3.11 bn cumulative** | $1,023 |
| Lifecycle envelope (yr 1–30, operating-neutral after opening) | **$3.11 bn cumulative** | $1,023 |

_Population basis: 3,037,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $1.3 M / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $750 M | 3.8% | 30 y, 7 y grace | $49 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $312 M | 16.5% | 30 y, 7 y grace | $53 M / yr |
| Government equity (no debt service) | 15% | $187 M | — | — | — |
| **Total** | **100%** | **$1.25 bn** | | | **$103 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $28 M / yr + bonds $52 M / yr = **$80 M / yr** total — plus the equity tranche amortised across construction ($27 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $12 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $16 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $585 k |
| Traction energy (810.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,426 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $4.2 M |
| **OPEX subtotal** | | **$33 M / yr** |

_Annual fleet utilisation: 172 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 33.8 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$175 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.29 |
| Operating-neutral single-trip fare (6 % pass) | $0.35 |
| Day pass (3 trips) | $0.89 (15 % bulk discount) |
| Monthly unlimited pass | $10.50 (~6 % of median monthly income) |
| Annual pass | $115.50 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (449,280 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 184,771 | 307,951 | 195,038 |
| Daily paid trips / catchment | 18% | 30% | 19% |
| Daily paid trips / city population | 6% | 10% | 6% |
| Annual paid trips | 67.4 M | 112.4 M | 71.2 M |
| Farebox revenue | $24 M / yr | $39 M / yr | $25 M / yr |
| Station shop leases | $3.1 M / yr | $3.1 M / yr | $3.1 M / yr |
| Advertising boards | $4.9 M / yr | $4.9 M / yr | $4.9 M / yr |
| **Total revenue** | **$32 M / yr** | **$47 M / yr** | **$33 M / yr** |
| Revenue / OPEX recovery | 96% | 144% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Remaining steady-state gov commitment | $104 M / yr | $103 M / yr | **$103 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $14 M / yr | $0 / yr |

_Commercial-revenue assumptions: 21,272 m² of station shop/kiosk leases at $14/m²/month and 3,948 advertising boards at $122/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`lusaka.toml`](lusaka.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`lusaka-network-map.png`](lusaka-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`lusaka.corridor.geojson`](lusaka.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`lusaka.stations.json`](lusaka.stations.json) | Machine-readable station list |
| [`lusaka.design-quality.yaml`](lusaka.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug lusaka

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug lusaka \
    --sidecar .cache/osr-pipeline/rasters/lusaka.grid.json \
    --out-dir designs/.../Lusaka

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../lusaka.toml \
    --out designs/.../README.md
```

`scripts/regenerate-lusaka.sh` chains steps 3 + drift tests into a single command.
