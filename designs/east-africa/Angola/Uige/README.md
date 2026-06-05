# Uige — Urban Rail Network

**Country:** AO · **Population:** 400,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Uige rail network on OpenStreetMap](uige-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`uige.corridor.geojson`](uige.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 1 |
| Unique stations | 8 |
| Interchange stations | 0 |
| Multi-line transfer reachability | 100% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 67.2% |
| Route length (double track) | 13.0 km |
| Revenue fleet | 12 × 3-car trainsets |
| Spare + cold-reserve | 2 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 13.0 km | 8 | 14 | W Outer ↔ SE Outer |
| **Total** | **13.0 km** | **8 unique** | **14** | |

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
- **Network peak throughput (all lines, both directions):** 1 lines × 2 directions × 3,960 = **7,920 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **79,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **51,480 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment (capped by practical service capacity)): ≈ **48,384 – 51,480 trips/day**

## Catchment

- City population: **400,000**
- Anchor-weighted coverage: 67.2%
- Catchment population: **≈ 268,800** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Major | 3 | 400 kW | 2500 kWh |
| Standard | 3 | 300 kW | 2000 kWh |
| Terminal | 1 | 500 kW | 3000 kWh |
| **Total installed** | **8** | **7,600 kW** | **56,500 kWh** |

Aggregate station-rail charging power: **5,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 156 kWh | 13.0 km average line length |
| Onboard battery coverage | 2.3× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 10.4 kWh/stop | 625 kW average charger across stops |
| Stops to refill one trainset pack | 35 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 38 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 56 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (12.8 km @ $2.0 M/km) | $26 M |
| **Civil subtotal** | **$26 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 3 | $800 k | $2.4 M |
| `major` | 3 | $1.60 M | $4.8 M |
| `terminal` | 1 | $1.40 M | $1.4 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| **Stations subtotal** | | | **$11 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 1 | $2.0 M | $2.0 M |
| **Depots subtotal** | | | **$14 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 14 | $800 k | $11 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 13.0 km × $0.015 M/km | $642 k |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $3.6 M |
| EPC integration + project management (7%) | on subtotal | $4.6 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $26 M |
| Stations | $11 M |
| Depots | $14 M |
| Rolling stock | $11 M |
| Residual train-control wayside + charging microgrids | $4.2 M |
| EPC overhead (7%) | $4.6 M |
| **CAPEX total** | **$70 M** |
| Per-route-km | $5.4 M / km |
| Per-capita (city pop) | $176 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh uige`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$6.0 M / yr** | $15 |
| Steady-state, low-ridership (year 6+) | **$5.5 M / yr** | $14 |
| Steady-state, high-ridership (year 6+) | **$5.5 M / yr** | $14 |
| Steady-state, operating-neutral revenue case | **$5.5 M / yr** | $14 |
| Lifecycle envelope (yr 1–25, low scenario) | **$141 M cumulative** | $352 |
| Lifecycle envelope (yr 1–25, high scenario) | **$141 M cumulative** | $352 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$141 M cumulative** | $352 |

_Population basis: 400,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $42 M | 4.5% | 25 y, 5 y grace | $3.2 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $18 M | 11.5% | 25 y, 5 y grace | $2.3 M / yr |
| Government equity (no debt service) | 15% | $11 M | — | — | — |
| **Total** | **100%** | **$70 M** | | | **$5.5 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $1.9 M / yr + bonds $2.0 M / yr = **$3.9 M / yr** total — plus the equity tranche amortised across construction ($2.1 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $448 k |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $1.0 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $32 k |
| Traction energy (24.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (90 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $363 k |
| **OPEX subtotal** | | **$1.8 M / yr** |

_Annual fleet utilisation: 12 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 2.0 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$240 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.40 |
| Operating-neutral single-trip fare (6 % pass) | $0.48 |
| Day pass (3 trips) | $1.22 (15 % bulk discount) |
| Monthly unlimited pass | $14.40 (~6 % of median monthly income) |
| Annual pass | $158.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (51,480 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 48,384 | 51,480 | 7,057 |
| Daily paid trips / catchment | 18% | 19% | 3% |
| Daily paid trips / city population | 12% | 13% | 2% |
| Annual paid trips | 17.7 M | 18.8 M | 2.6 M |
| Farebox revenue | $8.5 M / yr | $9.0 M / yr | $1.2 M / yr |
| Station shop leases | $229 k / yr | $229 k / yr | $229 k / yr |
| Advertising boards | $384 k / yr | $384 k / yr | $384 k / yr |
| **Total revenue** | **$9.1 M / yr** | **$9.6 M / yr** | **$1.8 M / yr** |
| Revenue / OPEX recovery | 492% | 521% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov commitment | $5.5 M / yr | $5.5 M / yr | **$5.5 M / yr** |
| Operating surplus after OPEX | $7.2 M / yr | $7.8 M / yr | $0 / yr |

_Commercial-revenue assumptions: 1,128 m² of station shop/kiosk leases at $19/m²/month and 224 advertising boards at $168/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`uige.toml`](uige.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`uige-network-map.png`](uige-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`uige.corridor.geojson`](uige.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`uige.stations.json`](uige.stations.json) | Machine-readable station list |
| [`uige.design-quality.yaml`](uige.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug uige

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug uige \
    --sidecar .cache/osr-pipeline/rasters/uige.grid.json \
    --out-dir designs/.../Uige

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../uige.toml \
    --out designs/.../README.md
```

`scripts/regenerate-uige.sh` chains steps 3 + drift tests into a single command.
