# Davao — Urban Rail Network

**Country:** PH · **Population:** 1,827,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Davao rail network on OpenStreetMap](davao-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`davao.corridor.geojson`](davao.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 107 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 71.5% |
| Route length (double track) | 228.9 km |
| Revenue fleet | 167 × 4-car trainsets |
| Spare + cold-reserve | 19 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 39.7 km | 16 | 32 | SW Outer ↔ NE Mid |
| line-2 | 24.5 km | 14 | 20 | E Mid ↔ SW Mid |
| line-3 | 35.2 km | 16 | 29 | NE Outer ↔ SE Inner |
| line-4 | 32.1 km | 14 | 27 | S Inner ↔ NW Outer |
| line-5 | 27.7 km | 13 | 24 | W Mid ↔ E Inner |
| line-6 | 69.7 km | 35 | 54 | NW Mid ↔ NW Mid |
| **Total** | **228.9 km** | **107 unique** | **186** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Nominal capacity | 540 pax (seated + standing, `metro-4car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 540 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 540 × 12 = **6,480 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 6,480 = **77,760 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **777,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **130,630 – 195,945 trips/day**

## Catchment

- City population: **1,827,000**
- Anchor-weighted coverage: 71.5%
- Catchment population: **≈ 1,306,305** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 31 | 400 kW | 2500 kWh |
| Standard | 36 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **101** | **44,700 kW** | **288,500 kWh** |

Aggregate station-rail charging power: **57,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (216.4 km @ €3.5 M/km) | €758 M |
| Elevated (11.0 km @ €18 M/km) | €197 M |
| Elevated-interchange premium (8 sites @ €20 M) | €160 M |
| **Civil subtotal** | **€1.11 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 7 | €0.4 M | €2.8 M |
| `standard` | 36 | €1.5 M | €54 M |
| `major` | 31 | €3.0 M | €93 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 24 | €4.5 M | €108 M |
| **Stations subtotal** | | | **€283 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 9 | €3.0 M | €27 M |
| **Depots subtotal** | | | **€52 M** |

### Rolling stock

Rolling stock is costed at **€1.0 M per self-contained car (wagon)**. Each car carries one powered bogie, one trailer bogie, under-seat Na-ion battery, traction inverter, onboard sensor/control stack, doors, HVAC, interior, and aluminium body. Motors, sensors, train-control computers, and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Per-car cost bucket | Basis | Cost |
|---|---|---|
| Body shell + interior + doors | Aluminium extrusion body, glazing, seats, PRM zone, plug doors | €300 k |
| Bogies + brakes | One powered bogie + one trailer bogie, wheelsets, suspension, discs | €220 k |
| Traction package | PMSM motors, gearbox, SiC inverter, cooling, HV contactors | €180 k |
| Battery + BMS | 120 kWh usable under-seat Na-ion pack, BMS, fire containment | €120 k |
| Driverless onboard stack | T-ECU/S, T-ECU/A, T-OBS sensors, radios, cameras, event recorder | €90 k |
| HVAC, auxiliaries, fit-out margin | HVAC, lighting, PIS, wiring, assembly QA | €90 k |
| **Total per car** | | **€1.0 M** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-4car` (revenue + spare + cold reserve) | 186 | €4.0 M | €744 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 228.9 km × €0.015 M/km | €3.4 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 228.9 km × €0.8 M/km | €182 M |
| EPC integration + project management (7%) | on subtotal | €167 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.11 bn |
| Stations | €283 M |
| Depots | €52 M |
| Rolling stock | €744 M |
| Residual train-control wayside + power | €185 M |
| EPC overhead (7%) | €167 M |
| **CAPEX total** | **€2.55 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €1,394 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh davao`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€177 M / yr** | €97 |
| Steady-state, low-ridership (year 6+) | **€217 M / yr** | €119 |
| Steady-state, high-ridership (year 6+) | **€199 M / yr** | €109 |
| Lifecycle envelope (yr 1–25, low scenario) | **€5.23 bn cumulative** | €2,860 |
| Lifecycle envelope (yr 1–25, high scenario) | **€4.86 bn cumulative** | €2,659 |

_Population basis: 1,827,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€48 M / yr (low) → €30 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.53 bn | 4.0% | 25 y, 5 y grace | €112 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €636 M | 6.2% | 25 y, 5 y grace | €56 M / yr |
| Government equity (no debt service) | 15% | €382 M | — | — | — |
| **Total** | **100%** | **€2.55 bn** | | | **€169 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €61 M / yr + bonds €39 M / yr = **€101 M / yr** total — plus the equity tranche amortised across construction (€76 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €30 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €29 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €171 k |
| Traction energy (524.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,385 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €7.7 M |
| **OPEX subtotal** | | **€67 M / yr** |

_Annual fleet utilisation: 167 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 32.8 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$360 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.55 (~$0.60 USD) |
| Day pass (3 trips) | €1.41 (15 % bulk discount) |
| Monthly unlimited pass | €16.56 (~5 % of median monthly income) |
| Annual pass | €182.16 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 33.3 M | 66.7 M |
| Farebox revenue | €18 M / yr | €37 M / yr |
| Farebox / OPEX recovery | 28% | 55% |
| Country policy-target recovery (diagnostic) | 55% | 55% |
| Operating shortfall (gov subsidy required) | €48 M / yr | €30 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€217 M / yr** | **€199 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`davao.toml`](davao.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`davao-network-map.png`](davao-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`davao.corridor.geojson`](davao.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`davao.stations.json`](davao.stations.json) | Machine-readable station list |
| [`davao.design-quality.yaml`](davao.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug davao

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug davao \
    --sidecar .cache/osr-pipeline/rasters/davao.grid.json \
    --out-dir designs/.../Davao

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../davao.toml \
    --out designs/.../README.md
```

`scripts/regenerate-davao.sh` chains steps 3 + drift tests into a single command.
