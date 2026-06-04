# Nairobi — Urban Rail Network

**Country:** KE · **Population:** 5,700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Nairobi rail network on OpenStreetMap](nairobi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`nairobi.corridor.geojson`](nairobi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 190 |
| Interchange stations | 26 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 42.8% |
| Route length (double track) | 476.2 km |
| Revenue fleet | 340 × 6-car trainsets |
| Spare + cold-reserve | 38 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 57.1 km | 25 | 46 | SW Outer ↔ NE Outer |
| line-2 | 59.9 km | 27 | 48 | W Outer ↔ E Outer |
| line-3 | 55.1 km | 23 | 43 | NW Mid ↔ SE Outer |
| line-4 | 48.0 km | 18 | 39 | SE Mid ↔ W Outer |
| line-5 | 47.7 km | 18 | 38 | NE Mid ↔ SW Outer |
| line-6 | 52.9 km | 22 | 42 | N Mid ↔ SE Outer |
| line-7 | 38.4 km | 14 | 31 | E Mid ↔ NW Outer |
| line-8 | 117.2 km | 44 | 91 | W Mid ↔ W Mid |
| **Total** | **476.2 km** | **190 unique** | **378** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 660 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 840 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 660 AW2 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 660 × 12 = **7,920 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 7,920 = **126,720 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,267,200 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **243,960 – 365,940 trips/day**

## Catchment

- City population: **5,700,000**
- Anchor-weighted coverage: 42.8%
- Catchment population: **≈ 2,439,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 26 | 500 kW | 3000 kWh |
| Major | 35 | 400 kW | 2500 kWh |
| Standard | 105 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **180** | **70,000 kW** | **454,500 kWh** |

Aggregate station-rail charging power: **99,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,429 kWh | 59.5 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 525 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 350 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 454 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (450.2 km @ $0.85 M/km) | $383 M |
| Elevated (23.1 km @ $4.0 M/km) | $92 M |
| Elevated-interchange premium (16 sites @ $2.0 M) | $32 M |
| **Civil subtotal** | **$507 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 11 | $120 k | $1.3 M |
| `standard` | 105 | $300 k | $32 M |
| `major` | 35 | $600 k | $21 M |
| `terminal` | 13 | $500 k | $6.5 M |
| `depot-terminal` | 1 | $650 k | $650 k |
| `interchange-elevated` | 26 | $1.20 M | $31 M |
| **Stations subtotal** | | | **$92 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $7.50 M | $7.5 M |
| `layup-minimal` | 13 | $900 k | $12 M |
| **Depots subtotal** | | | **$19 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 378 | $1.60 M | $605 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 476.2 km × $0.015 M/km | $7.1 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $38 M |
| EPC integration + project management (7%) | on subtotal | $89 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $507 M |
| Stations | $92 M |
| Depots | $19 M |
| Rolling stock | $605 M |
| Residual train-control wayside + charging microgrids | $45 M |
| EPC overhead (7%) | $89 M |
| **CAPEX total** | **$1.36 bn** |
| Per-route-km | $2.9 M / km |
| Per-capita (city pop) | $238 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh nairobi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$105 M / yr** | $18 |
| Steady-state, low-ridership (year 8+) | **$58 M / yr** | $10 |
| Steady-state, high-ridership (year 8+) | **$0 k / yr** | $0 |
| Steady-state, cost-neutral revenue case | **$0 / yr** | $0 |
| Lifecycle envelope (yr 1–30, low scenario) | **$2.06 bn cumulative** | $362 |
| Lifecycle envelope (yr 1–30, high scenario) | **$733 M cumulative** | $129 |
| Lifecycle envelope (yr 1–30, cost-neutral after opening) | **$733 M cumulative** | $129 |

_Population basis: 5,700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the cost-neutral case already covers steady-state OPEX + debt service from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $815 M | 4.5% | 30 y, 7 y grace | $58 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $339 M | 11.5% | 30 y, 7 y grace | $43 M / yr |
| Government equity (no debt service) | 15% | $204 M | — | — | — |
| **Total** | **100%** | **$1.36 bn** | | | **$100 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $37 M / yr + bonds $39 M / yr = **$76 M / yr** total — plus the equity tranche amortised across construction ($29 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $24 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $12 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $357 k |
| Traction energy (1602.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,869 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $11 M |
| **OPEX subtotal** | | **$48 M / yr** |

_Annual fleet utilisation: 340 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 66.8 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The cost-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.38 |
| Cost-neutral single-trip fare (6 % pass) | $0.46 |
| Day pass (3 trips) | $1.17 (15 % bulk discount) |
| Monthly unlimited pass | $13.80 (~6 % of median monthly income) |
| Annual pass | $151.80 (11 × monthly = ~1 free month) |

### Revenue & cost-neutrality

Planning ridership bracket = 8–15 % of urban population × 365 service-days at the cost-neutral fare. The cost-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = OPEX + post-grace debt service**.

| | Low scenario | High scenario | Cost-neutral target |
|---|---|---|---|
| Daily paid trips | 456,000 | 855,000 | 799,710 |
| Daily paid trips / population | 8% | 15% | 14% |
| Annual paid trips | 166.4 M | 312.1 M | 291.9 M |
| Farebox revenue | $77 M / yr | $144 M / yr | $134 M / yr |
| Station shop leases | $5.3 M / yr | $5.3 M / yr | $5.3 M / yr |
| Advertising boards | $8.5 M / yr | $8.5 M / yr | $8.5 M / yr |
| **Total revenue** | **$90 M / yr** | **$157 M / yr** | **$148 M / yr** |
| Revenue / OPEX + debt-service recovery | 61% | 106% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Remaining steady-state gov gap | $58 M / yr | $0 k / yr | **$0 / yr** |
| Operating surplus after OPEX + debt | $0 k / yr | $9.3 M / yr | $0 / yr |

_Commercial-revenue assumptions: 27,248 m² of station shop/kiosk leases at $18/m²/month and 5,196 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % cost-neutral fare target, the 8–15 % daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`nairobi.toml`](nairobi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`nairobi-network-map.png`](nairobi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`nairobi.corridor.geojson`](nairobi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`nairobi.stations.json`](nairobi.stations.json) | Machine-readable station list |
| [`nairobi.design-quality.yaml`](nairobi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug nairobi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug nairobi \
    --sidecar .cache/osr-pipeline/rasters/nairobi.grid.json \
    --out-dir designs/.../Nairobi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../nairobi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-nairobi.sh` chains steps 3 + drift tests into a single command.
