# Xai-Xai — Urban Rail Network

**Country:** MZ · **Population:** 250,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Xai-Xai rail network on OpenStreetMap](xai-xai-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`xai-xai.corridor.geojson`](xai-xai.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 2 |
| Unique stations | 12 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 43.4% |
| Route length (double track) | 17.9 km |
| Revenue fleet | 23 × 2-car trainsets |
| Spare + cold-reserve | 4 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 |  9.4 km | 6 | 14 | S Outer ↔ NE Outer |
| line-2 |  8.5 km | 6 | 13 | NW Outer ↔ E Outer |
| **Total** | **17.9 km** | **12 unique** | **27** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 210 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 260 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 210 AW2 passengers (`tram-2car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 210 × 12 = **2,520 pphpd**
- **Network peak throughput (all lines, both directions):** 2 lines × 2 directions × 2,520 = **10,080 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **100,800 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **10,850 – 16,275 trips/day**

## Catchment

- City population: **250,000**
- Anchor-weighted coverage: 43.4%
- Catchment population: **≈ 108,500** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 1 | 400 kW | 2500 kWh |
| Standard | 5 | 300 kW | 2000 kWh |
| Terminal | 3 | 500 kW | 3000 kWh |
| **Total installed** | **12** | **9,400 kW** | **67,500 kWh** |

Aggregate station-rail charging power: **8,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 72 kWh | 8.9 km average line length |
| Onboard battery coverage | 3.4× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 11.1 kWh/stop | 667 kW average charger across stops |
| Stops to refill one trainset pack | 22 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 47 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 68 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (16.5 km @ $1.2 M/km) | $20 M |
| Elevated (1.2 km @ $5.5 M/km) | $6.5 M |
| Elevated-interchange premium (1 sites @ $2.5 M) | $2.5 M |
| **Civil subtotal** | **$29 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 5 | $450 k | $2.2 M |
| `major` | 1 | $900 k | $900 k |
| `terminal` | 3 | $800 k | $2.4 M |
| `depot-terminal` | 1 | $1.00 M | $1.0 M |
| `interchange` | 2 | $1.35 M | $2.7 M |
| **Stations subtotal** | | | **$9.2 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $7.50 M | $7.5 M |
| `layup-minimal` | 3 | $900 k | $2.7 M |
| **Depots subtotal** | | | **$10 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 27 | $534 k | $14 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 17.9 km × $0.015 M/km | $269 k |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $2.9 M |
| EPC integration + project management (7%) | on subtotal | $4.6 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $29 M |
| Stations | $9.2 M |
| Depots | $10 M |
| Rolling stock | $14 M |
| Residual train-control wayside + charging microgrids | $3.2 M |
| EPC overhead (7%) | $4.6 M |
| **CAPEX total** | **$71 M** |
| Per-route-km | $3.9 M / km |
| Per-capita (city pop) | $282 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh xai-xai`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$4.7 M / yr** | $19 |
| Steady-state, low-ridership (year 11+) | **$4.3 M / yr** | $17 |
| Steady-state, high-ridership (year 11+) | **$2.6 M / yr** | $10 |
| Steady-state, cost-neutral revenue case | **$0 / yr** | $0 |
| Lifecycle envelope (yr 1–35, low scenario) | **$154 M cumulative** | $616 |
| Lifecycle envelope (yr 1–35, high scenario) | **$112 M cumulative** | $450 |
| Lifecycle envelope (yr 1–35, cost-neutral after opening) | **$47 M cumulative** | $188 |

_Population basis: 250,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero; the cost-neutral case already covers steady-state OPEX + debt service from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $42 M | 3.0% | 35 y, 10 y grace | $2.4 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $18 M | 13.5% | 35 y, 10 y grace | $2.5 M / yr |
| Government equity (no debt service) | 15% | $11 M | — | — | — |
| **Total** | **100%** | **$71 M** | | | **$4.9 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $1.3 M / yr + bonds $2.4 M / yr = **$3.6 M / yr** total — plus the equity tranche amortised across construction ($1.1 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $576 k |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $967 k |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $13 k |
| Traction energy (22.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (119 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $260 k |
| **OPEX subtotal** | | **$1.8 M / yr** |

_Annual fleet utilisation: 23 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 2.8 M train-km / yr (~123 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$130 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The cost-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.22 |
| Cost-neutral single-trip fare (6 % pass) | $0.26 |
| Day pass (3 trips) | $0.66 (15 % bulk discount) |
| Monthly unlimited pass | $7.80 (~6 % of median monthly income) |
| Annual pass | $85.80 (11 × monthly = ~1 free month) |

### Revenue & cost-neutrality

Planning ridership bracket = 8–15 % of urban population × 365 service-days at the cost-neutral fare. The cost-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = OPEX + post-grace debt service**.

| | Low scenario | High scenario | Cost-neutral target |
|---|---|---|---|
| Daily paid trips | 20,000 | 37,500 | 65,024 |
| Daily paid trips / population | 8% | 15% | 26% |
| Annual paid trips | 7.3 M | 13.7 M | 23.7 M |
| Farebox revenue | $1.9 M / yr | $3.6 M / yr | $6.2 M / yr |
| Station shop leases | $212 k / yr | $212 k / yr | $212 k / yr |
| Advertising boards | $349 k / yr | $349 k / yr | $349 k / yr |
| **Total revenue** | **$2.5 M / yr** | **$4.1 M / yr** | **$6.7 M / yr** |
| Revenue / OPEX + debt-service recovery | 37% | 61% | 100% |
| Country farebox-only policy target (diagnostic) | 30% | 30% | 30% |
| Remaining steady-state gov gap | $4.3 M / yr | $2.6 M / yr | **$0 / yr** |
| Operating surplus after OPEX + debt | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 1,928 m² of station shop/kiosk leases at $10/m²/month and 376 advertising boards at $91/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % cost-neutral fare target, the 8–15 % daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`xai-xai.toml`](xai-xai.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`xai-xai-network-map.png`](xai-xai-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`xai-xai.corridor.geojson`](xai-xai.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`xai-xai.stations.json`](xai-xai.stations.json) | Machine-readable station list |
| [`xai-xai.design-quality.yaml`](xai-xai.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug xai-xai

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug xai-xai \
    --sidecar .cache/osr-pipeline/rasters/xai-xai.grid.json \
    --out-dir designs/.../Xai-Xai

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../xai-xai.toml \
    --out designs/.../README.md
```

`scripts/regenerate-xai-xai.sh` chains steps 3 + drift tests into a single command.
