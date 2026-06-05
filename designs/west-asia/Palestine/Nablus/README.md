# Nablus — Urban Rail Network

**Country:** PS · **Population:** 450,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Nablus rail network on OpenStreetMap](nablus-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`nablus.corridor.geojson`](nablus.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 34 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 84.1% |
| Route length (double track) | 64.6 km |
| Revenue fleet | 57 × 3-car trainsets |
| Spare + cold-reserve | 8 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 19.1 km | 12 | 19 | NW Mid ↔ SE Mid |
| line-2 | 22.9 km | 12 | 23 | W Mid ↔ E Mid |
| line-3 | 22.7 km | 10 | 23 | NE Outer ↔ SW Inner |
| **Total** | **64.6 km** | **34 unique** | **65** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **37,845 – 56,767 trips/day**

## Catchment

- City population: **450,000**
- Anchor-weighted coverage: 84.1%
- Catchment population: **≈ 378,450** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 7 | 400 kW | 2500 kWh |
| Standard | 14 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **30** | **16,000 kW** | **109,500 kWh** |

Aggregate station-rail charging power: **19,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 258 kWh | 21.5 km average line length |
| Onboard battery coverage | 1.4× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.3 kWh/stop | 559 kW average charger across stops |
| Stops to refill one trainset pack | 39 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 80 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 110 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (63.3 km @ $1.2 M/km) | $76 M |
| Elevated (1.2 km @ $5.5 M/km) | $6.8 M |
| Elevated-interchange premium (1 sites @ $2.5 M) | $2.5 M |
| **Civil subtotal** | **$85 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | $180 k | $720 k |
| `standard` | 14 | $450 k | $6.3 M |
| `major` | 7 | $900 k | $6.3 M |
| `terminal` | 5 | $800 k | $4.0 M |
| `depot-terminal` | 1 | $1.00 M | $1.0 M |
| `interchange-elevated` | 3 | $1.80 M | $5.4 M |
| **Stations subtotal** | | | **$24 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 65 | $800 k | $52 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 64.6 km × $0.015 M/km | $970 k |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $6.9 M |
| EPC integration + project management (7%) | on subtotal | $13 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $85 M |
| Stations | $24 M |
| Depots | $12 M |
| Rolling stock | $52 M |
| Residual train-control wayside + charging microgrids | $7.9 M |
| EPC overhead (7%) | $13 M |
| **CAPEX total** | **$194 M** |
| Per-route-km | $3.0 M / km |
| Per-capita (city pop) | $430 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh nablus`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$12 M / yr** | $26 |
| Steady-state, low-ridership (year 8+) | **$5.7 M / yr** | $13 |
| Steady-state, high-ridership (year 8+) | **$0 k / yr** | $0 |
| Steady-state, cost-neutral revenue case | **$0 / yr** | $0 |
| Lifecycle envelope (yr 1–30, low scenario) | **$212 M cumulative** | $472 |
| Lifecycle envelope (yr 1–30, high scenario) | **$82 M cumulative** | $183 |
| Lifecycle envelope (yr 1–30, cost-neutral after opening) | **$82 M cumulative** | $183 |

_Population basis: 450,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the cost-neutral case already covers steady-state OPEX + debt service from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $116 M | 3.0% | 30 y, 7 y grace | $7.1 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $48 M | 8.5% | 30 y, 7 y grace | $4.9 M / yr |
| Government equity (no debt service) | 15% | $29 M | — | — | — |
| **Total** | **100%** | **$194 M** | | | **$12 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $3.5 M / yr + bonds $4.1 M / yr = **$7.6 M / yr** total — plus the equity tranche amortised across construction ($4.1 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $2.1 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $2.4 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $48 k |
| Traction energy (115.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (400 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $2.4 M |
| **OPEX subtotal** | | **$7.0 M / yr** |

_Annual fleet utilisation: 57 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 9.6 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$360 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The cost-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.60 |
| Cost-neutral single-trip fare (6 % pass) | $0.72 |
| Day pass (3 trips) | $1.84 (15 % bulk discount) |
| Monthly unlimited pass | $21.60 (~6 % of median monthly income) |
| Annual pass | $237.60 (11 × monthly = ~1 free month) |

### Revenue & cost-neutrality

Planning ridership bracket = 8–15 % of urban population × 365 service-days at the cost-neutral fare. The cost-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = OPEX + post-grace debt service**.

| | Low scenario | High scenario | Cost-neutral target |
|---|---|---|---|
| Daily paid trips | 36,000 | 67,500 | 57,544 |
| Daily paid trips / population | 8% | 15% | 13% |
| Annual paid trips | 13.1 M | 24.6 M | 21.0 M |
| Farebox revenue | $9.5 M / yr | $18 M / yr | $15 M / yr |
| Station shop leases | $1.4 M / yr | $1.4 M / yr | $1.4 M / yr |
| Advertising boards | $2.3 M / yr | $2.3 M / yr | $2.3 M / yr |
| **Total revenue** | **$13 M / yr** | **$22 M / yr** | **$19 M / yr** |
| Revenue / OPEX + debt-service recovery | 70% | 114% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov gap | $5.7 M / yr | $0 k / yr | **$0 / yr** |
| Operating surplus after OPEX + debt | $0 k / yr | $2.6 M / yr | $0 / yr |

_Commercial-revenue assumptions: 4,672 m² of station shop/kiosk leases at $29/m²/month and 912 advertising boards at $252/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % cost-neutral fare target, the 8–15 % daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`nablus.toml`](nablus.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`nablus-network-map.png`](nablus-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`nablus.corridor.geojson`](nablus.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`nablus.stations.json`](nablus.stations.json) | Machine-readable station list |
| [`nablus.design-quality.yaml`](nablus.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug nablus

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug nablus \
    --sidecar .cache/osr-pipeline/rasters/nablus.grid.json \
    --out-dir designs/.../Nablus

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../nablus.toml \
    --out designs/.../README.md
```

`scripts/regenerate-nablus.sh` chains steps 3 + drift tests into a single command.
