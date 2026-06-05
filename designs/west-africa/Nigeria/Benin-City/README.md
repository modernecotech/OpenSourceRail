# Benin-City — Urban Rail Network

**Country:** NG · **Population:** 1,800,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Benin-City rail network on OpenStreetMap](benin-city-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`benin-city.corridor.geojson`](benin-city.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 76 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 44.3% |
| Route length (double track) | 132.3 km |
| Revenue fleet | 98 × 4-car trainsets |
| Spare + cold-reserve | 13 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 30.5 km | 16 | 26 | N Outer ↔ S Outer |
| line-2 | 30.0 km | 17 | 25 | NE Outer ↔ SW Outer |
| line-3 | 26.1 km | 14 | 23 | NW Mid ↔ SE Outer |
| line-4 | 45.7 km | 30 | 37 | W Inner ↔ W Inner |
| **Total** | **132.3 km** | **76 unique** | **111** | |

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
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 5,760 = **46,080 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **460,800 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **299,520 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **143,532 – 239,220 trips/day**

## Catchment

- City population: **1,800,000**
- Anchor-weighted coverage: 44.3%
- Catchment population: **≈ 797,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 20 | 400 kW | 2500 kWh |
| Standard | 27 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **77** | **35,600 kW** | **231,000 kWh** |

Aggregate station-rail charging power: **41,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 529 kWh | 33.1 km average line length |
| Onboard battery coverage | 0.9× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 546 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 178 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 231 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (114.6 km @ $3.0 M/km) | $344 M |
| Elevated (16.8 km @ $9.0 M/km) | $151 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$540 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 27 | $800 k | $22 M |
| `major` | 20 | $1.60 M | $32 M |
| `terminal` | 5 | $1.40 M | $7.0 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 24 | $3.50 M | $84 M |
| **Stations subtotal** | | | **$147 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 111 | $1.07 M | $118 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 132.3 km × $0.015 M/km | $6.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $40 M |
| EPC integration + project management (7%) | on subtotal | $61 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $540 M |
| Stations | $147 M |
| Depots | $22 M |
| Rolling stock | $118 M |
| Residual train-control wayside + charging microgrids | $46 M |
| EPC overhead (7%) | $61 M |
| **CAPEX total** | **$934 M** |
| Per-route-km | $7.1 M / km |
| Per-capita (city pop) | $519 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh benin-city`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$77 M / yr** | $43 |
| Steady-state, low-ridership (year 8+) | **$73 M / yr** | $41 |
| Steady-state, high-ridership (year 8+) | **$73 M / yr** | $41 |
| Steady-state, operating-neutral revenue case | **$73 M / yr** | $41 |
| Lifecycle envelope (yr 1–30, low scenario) | **$2.22 bn cumulative** | $1,231 |
| Lifecycle envelope (yr 1–30, high scenario) | **$2.22 bn cumulative** | $1,231 |
| Lifecycle envelope (yr 1–30, operating-neutral after opening) | **$2.22 bn cumulative** | $1,231 |

_Population basis: 1,800,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $561 M | 4.5% | 30 y, 7 y grace | $40 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $234 M | 13.5% | 30 y, 7 y grace | $33 M / yr |
| Government equity (no debt service) | 15% | $140 M | — | — | — |
| **Total** | **100%** | **$934 M** | | | **$73 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $25 M / yr + bonds $32 M / yr = **$57 M / yr** total — plus the equity tranche amortised across construction ($20 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $4.7 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $14 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $328 k |
| Traction energy (308.0 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (806 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $2.4 M |
| **OPEX subtotal** | | **$22 M / yr** |

_Annual fleet utilisation: 98 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 19.2 M train-km / yr (~196 k km / trainset / yr)._

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

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (299,520 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 143,532 | 239,220 | 121,808 |
| Daily paid trips / catchment | 18% | 30% | 15% |
| Daily paid trips / city population | 8% | 13% | 7% |
| Annual paid trips | 52.4 M | 87.3 M | 44.5 M |
| Farebox revenue | $18 M / yr | $31 M / yr | $16 M / yr |
| Station shop leases | $2.4 M / yr | $2.4 M / yr | $2.4 M / yr |
| Advertising boards | $3.6 M / yr | $3.6 M / yr | $3.6 M / yr |
| **Total revenue** | **$24 M / yr** | **$37 M / yr** | **$22 M / yr** |
| Revenue / OPEX recovery | 113% | 169% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov commitment | $73 M / yr | $73 M / yr | **$73 M / yr** |
| Operating surplus after OPEX | $2.8 M / yr | $15 M / yr | $0 / yr |

_Commercial-revenue assumptions: 16,240 m² of station shop/kiosk leases at $14/m²/month and 2,916 advertising boards at $122/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`benin-city.toml`](benin-city.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`benin-city-network-map.png`](benin-city-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`benin-city.corridor.geojson`](benin-city.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`benin-city.stations.json`](benin-city.stations.json) | Machine-readable station list |
| [`benin-city.design-quality.yaml`](benin-city.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug benin-city

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug benin-city \
    --sidecar .cache/osr-pipeline/rasters/benin-city.grid.json \
    --out-dir designs/.../Benin-City

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../benin-city.toml \
    --out designs/.../README.md
```

`scripts/regenerate-benin-city.sh` chains steps 3 + drift tests into a single command.
