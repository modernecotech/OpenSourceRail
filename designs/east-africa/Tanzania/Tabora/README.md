# Tabora — Urban Rail Network

**Country:** TZ · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Tabora rail network on OpenStreetMap](tabora-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`tabora.corridor.geojson`](tabora.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 2 |
| Unique stations | 13 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 53.8% |
| Route length (double track) | 17.6 km |
| Revenue fleet | 22 × 2-car trainsets |
| Spare + cold-reserve | 4 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 12.3 km | 8 | 17 | W Mid ↔ S Outer |
| line-2 |  5.2 km | 5 | 9 | NE Mid ↔ NW Mid |
| **Total** | **17.6 km** | **13 unique** | **26** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 160 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 210 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 160 AW2 passengers (`tram-2car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 160 × 12 = **1,920 pphpd**
- **Network peak throughput (all lines, both directions):** 2 lines × 2 directions × 1,920 = **7,680 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **76,800 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **49,920 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **29,052 – 48,420 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 53.8%
- Catchment population: **≈ 161,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 5 | 400 kW | 2500 kWh |
| Standard | 1 | 300 kW | 2000 kWh |
| Terminal | 3 | 500 kW | 3000 kWh |
| **Total installed** | **12** | **9,800 kW** | **69,500 kWh** |

Aggregate station-rail charging power: **8,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 70 kWh | 8.8 km average line length |
| Onboard battery coverage | 3.4× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.6 kWh/stop | 635 kW average charger across stops |
| Stops to refill one trainset pack | 23 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 49 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 70 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD marketplace / direct-supplier pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **marketplace-BOM rolling stock at about $267 k per self-contained car** (derived from the 800,334 USD 3-car BOM floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. This is a listed-price floor, not a certified rail supplier quote; freight, duty, qualification, warranty, and acceptance testing sit outside the city CAPEX floor. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (15.3 km @ $2.0 M/km) | $31 M |
| Elevated (2.2 km @ $9.0 M/km) | $19 M |
| Elevated-interchange premium (2 sites @ $4.50 M) | $9.0 M |
| **Civil subtotal** | **$59 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $300 k | $300 k |
| `standard` | 1 | $800 k | $800 k |
| `major` | 5 | $1.60 M | $8.0 M |
| `terminal` | 3 | $1.40 M | $4.2 M |
| `depot-terminal` | 1 | $2.0 M | $2.0 M |
| `interchange-elevated` | 2 | $3.50 M | $7.0 M |
| **Stations subtotal** | | | **$22 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 26 | $534 k | $14 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 17.6 km × $0.015 M/km | $870 k |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $6.8 M |
| EPC integration + project management (7%) | on subtotal | $8.5 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $59 M |
| Stations | $22 M |
| Depots | $18 M |
| Rolling stock | $14 M |
| Residual train-control wayside + charging microgrids | $7.7 M |
| EPC overhead (7%) | $8.5 M |
| **CAPEX total** | **$129 M** |
| Per-route-km | $7.3 M / km |
| Per-capita (city pop) | $431 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh tabora`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$8.8 M / yr** | $29 |
| Steady-state, low-ridership (year 8+) | **$8.6 M / yr** | $29 |
| Steady-state, high-ridership (year 8+) | **$8.6 M / yr** | $29 |
| Steady-state, operating-neutral revenue case | **$8.6 M / yr** | $29 |
| Lifecycle envelope (yr 1–30, low scenario) | **$260 M cumulative** | $865 |
| Lifecycle envelope (yr 1–30, high scenario) | **$260 M cumulative** | $865 |
| Lifecycle envelope (yr 1–30, operating-neutral after opening) | **$260 M cumulative** | $865 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $78 M | 3.8% | 30 y, 7 y grace | $5.1 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $32 M | 9.5% | 30 y, 7 y grace | $3.5 M / yr |
| Government equity (no debt service) | 15% | $19 M | — | — | — |
| **Total** | **100%** | **$129 M** | | | **$8.6 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $2.9 M / yr + bonds $3.1 M / yr = **$6.0 M / yr** total — plus the equity tranche amortised across construction ($2.8 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $555 k |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $2.0 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $44 k |
| Traction energy (21.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (118 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $327 k |
| **OPEX subtotal** | | **$2.9 M / yr** |

_Annual fleet utilisation: 22 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 2.7 M train-km / yr (~123 k km / trainset / yr)._

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

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (49,920 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 29,052 | 48,420 | 16,549 |
| Daily paid trips / catchment | 18% | 30% | 10% |
| Daily paid trips / city population | 10% | 16% | 6% |
| Annual paid trips | 10.6 M | 17.7 M | 6.0 M |
| Farebox revenue | $3.5 M / yr | $5.8 M / yr | $2.0 M / yr |
| Station shop leases | $355 k / yr | $355 k / yr | $355 k / yr |
| Advertising boards | $561 k / yr | $561 k / yr | $561 k / yr |
| **Total revenue** | **$4.4 M / yr** | **$6.7 M / yr** | **$2.9 M / yr** |
| Revenue / OPEX recovery | 152% | 232% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov commitment | $8.6 M / yr | $8.6 M / yr | **$8.6 M / yr** |
| Operating surplus after OPEX | $1.5 M / yr | $3.8 M / yr | $0 / yr |

_Commercial-revenue assumptions: 2,544 m² of station shop/kiosk leases at $13/m²/month and 476 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`tabora.toml`](tabora.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`tabora-network-map.png`](tabora-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`tabora.corridor.geojson`](tabora.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`tabora.stations.json`](tabora.stations.json) | Machine-readable station list |
| [`tabora.design-quality.yaml`](tabora.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug tabora

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug tabora \
    --sidecar .cache/osr-pipeline/rasters/tabora.grid.json \
    --out-dir designs/.../Tabora

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../tabora.toml \
    --out designs/.../README.md
```

`scripts/regenerate-tabora.sh` chains steps 3 + drift tests into a single command.
