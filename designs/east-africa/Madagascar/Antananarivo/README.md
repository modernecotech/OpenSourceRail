# Antananarivo — Urban Rail Network

**Country:** MG · **Population:** 3,058,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Antananarivo rail network on OpenStreetMap](antananarivo-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`antananarivo.corridor.geojson`](antananarivo.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 7 |
| Unique stations | 154 |
| Interchange stations | 26 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 42.0% |
| Route length (double track) | 338.9 km |
| Revenue fleet | 244 × 6-car trainsets |
| Spare + cold-reserve | 28 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 52.2 km | 24 | 41 | NE Outer ↔ S Outer |
| line-2 | 42.2 km | 17 | 35 | S Outer ↔ NW Outer |
| line-3 | 39.0 km | 20 | 31 | N Outer ↔ SW Outer |
| line-4 | 33.0 km | 18 | 27 | NW Outer ↔ SE Mid |
| line-5 | 41.2 km | 19 | 34 | NE Outer ↔ SW Mid |
| line-6 | 38.1 km | 17 | 31 | E Outer ↔ W Outer |
| line-7 | 93.1 km | 40 | 73 | NW Mid ↔ NW Mid |
| **Total** | **338.9 km** | **154 unique** | **272** | |

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
- **Network peak throughput (all lines, both directions):** 7 lines × 2 directions × 8,640 = **120,960 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,209,600 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **786,240 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **231,184 – 385,308 trips/day**

## Catchment

- City population: **3,058,000**
- Anchor-weighted coverage: 42.0%
- Catchment population: **≈ 1,284,360** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 26 | 500 kW | 3000 kWh |
| Major | 40 | 400 kW | 2500 kWh |
| Standard | 73 | 300 kW | 2000 kWh |
| Terminal | 11 | 500 kW | 3000 kWh |
| **Total installed** | **151** | **61,400 kW** | **397,000 kWh** |

Aggregate station-rail charging power: **82,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,162 kWh | 48.4 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 536 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 307 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 397 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (302.5 km @ $3.0 M/km) | $908 M |
| Elevated (34.0 km @ $12.0 M/km) | $408 M |
| Elevated-interchange premium (14 sites @ $4.50 M) | $63 M |
| **Civil subtotal** | **$1.38 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | $300 k | $1.2 M |
| `standard` | 73 | $800 k | $58 M |
| `major` | 40 | $1.60 M | $64 M |
| `terminal` | 11 | $1.40 M | $15 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange` | 3 | $2.50 M | $7.5 M |
| `interchange-elevated` | 23 | $3.50 M | $80 M |
| **Stations subtotal** | | | **$229 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 11 | $2.0 M | $22 M |
| **Depots subtotal** | | | **$34 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 272 | $1.60 M | $435 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 338.9 km × $0.050 M/km | $17 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $65 M |
| EPC integration + project management (7%) | on subtotal | $151 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.38 bn |
| Stations | $229 M |
| Depots | $34 M |
| Rolling stock | $435 M |
| Residual train-control wayside + charging microgrids | $82 M |
| EPC overhead (7%) | $151 M |
| **CAPEX total** | **$2.31 bn** |
| Per-route-km | $6.8 M / km |
| Per-capita (city pop) | $755 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh antananarivo`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$140 M / yr** | $46 |
| Steady-state, low-ridership (year 11+) | **$181 M / yr** | $59 |
| Steady-state, high-ridership (year 11+) | **$171 M / yr** | $56 |
| Steady-state, operating-neutral revenue case | **$148 M / yr** | $48 |
| Lifecycle envelope (yr 1–35, low scenario) | **$5.92 bn cumulative** | $1,935 |
| Lifecycle envelope (yr 1–35, high scenario) | **$5.66 bn cumulative** | $1,852 |
| Lifecycle envelope (yr 1–35, operating-neutral after opening) | **$5.10 bn cumulative** | $1,668 |

_Population basis: 3,058,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $33 M / yr → $23 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $1.39 bn | 3.0% | 35 y, 10 y grace | $80 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $577 M | 11.0% | 35 y, 10 y grace | $69 M / yr |
| Government equity (no debt service) | 15% | $346 M | — | — | — |
| **Total** | **100%** | **$2.31 bn** | | | **$148 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $42 M / yr + bonds $64 M / yr = **$105 M / yr** total — plus the equity tranche amortised across construction ($35 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $17 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $33 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $841 k |
| Traction energy (1150.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,045 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $3.1 M |
| **OPEX subtotal** | | **$54 M / yr** |

_Annual fleet utilisation: 244 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 47.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$90 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.15 |
| Operating-neutral single-trip fare (6 % pass) | $0.18 |
| Day pass (3 trips) | $0.46 (15 % bulk discount) |
| Monthly unlimited pass | $5.40 (~6 % of median monthly income) |
| Annual pass | $59.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (786,240 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 231,184 | 385,308 | 728,744 |
| Daily paid trips / catchment | 18% | 30% | 57% |
| Daily paid trips / city population | 8% | 13% | 24% |
| Annual paid trips | 84.4 M | 140.6 M | 266.0 M |
| Farebox revenue | $15 M / yr | $25 M / yr | $48 M / yr |
| Station shop leases | $2.7 M / yr | $2.7 M / yr | $2.7 M / yr |
| Advertising boards | $3.6 M / yr | $3.6 M / yr | $3.6 M / yr |
| **Total revenue** | **$21 M / yr** | **$32 M / yr** | **$54 M / yr** |
| Revenue / OPEX recovery | 40% | 58% | 100% |
| Country farebox-only policy target (diagnostic) | 30% | 30% | 30% |
| Remaining steady-state gov commitment | $181 M / yr | $171 M / yr | **$148 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 25,360 m² of station shop/kiosk leases at $10/m²/month and 4,732 advertising boards at $75/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`antananarivo.toml`](antananarivo.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`antananarivo-network-map.png`](antananarivo-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`antananarivo.corridor.geojson`](antananarivo.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`antananarivo.stations.json`](antananarivo.stations.json) | Machine-readable station list |
| [`antananarivo.design-quality.yaml`](antananarivo.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug antananarivo

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug antananarivo \
    --sidecar .cache/osr-pipeline/rasters/antananarivo.grid.json \
    --out-dir designs/.../Antananarivo

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../antananarivo.toml \
    --out designs/.../README.md
```

`scripts/regenerate-antananarivo.sh` chains steps 3 + drift tests into a single command.
