# Mandalay — Urban Rail Network

**Country:** MM · **Population:** 1,726,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Mandalay rail network on OpenStreetMap](mandalay-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`mandalay.corridor.geojson`](mandalay.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 87 |
| Interchange stations | 23 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 60.1% |
| Route length (double track) | 187.0 km |
| Revenue fleet | 139 × 4-car trainsets |
| Spare + cold-reserve | 17 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 42.7 km | 18 | 35 | N Outer ↔ S Mid |
| line-2 | 33.6 km | 14 | 28 | NE Mid ↔ SW Outer |
| line-3 | 25.4 km | 11 | 21 | N Mid ↔ SE Mid |
| line-4 | 27.9 km | 13 | 24 | E Mid ↔ SW Mid |
| line-5 | 19.0 km | 11 | 17 | SE Mid ↔ W Inner |
| line-6 | 38.4 km | 21 | 31 | NE Inner ↔ NE Inner |
| **Total** | **187.0 km** | **87 unique** | **156** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 440 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 560 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 440 AW2 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 440 × 12 = **5,280 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 5,280 = **63,360 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **633,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **103,732 – 155,598 trips/day**

## Catchment

- City population: **1,726,000**
- Anchor-weighted coverage: 60.1%
- Catchment population: **≈ 1,037,326** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 23 | 500 kW | 3000 kWh |
| Major | 18 | 400 kW | 2500 kWh |
| Standard | 31 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **82** | **37,500 kW** | **243,000 kWh** |

Aggregate station-rail charging power: **47,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 499 kWh | 31.2 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 546 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 188 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 243 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (170.8 km @ €3.5 M/km) | €598 M |
| Elevated (14.7 km @ €18 M/km) | €264 M |
| Elevated-interchange premium (10 sites @ €20 M) | €200 M |
| **Civil subtotal** | **€1.06 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 6 | €0.4 M | €2.4 M |
| `standard` | 31 | €1.5 M | €46 M |
| `major` | 18 | €3.0 M | €54 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 23 | €4.5 M | €104 M |
| **Stations subtotal** | | | **€232 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 156 | €4.0 M | €624 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 187.0 km × €0.015 M/km | €2.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €34 M |
| EPC integration + project management (7%) | on subtotal | €140 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.06 bn |
| Stations | €232 M |
| Depots | €52 M |
| Rolling stock | €624 M |
| Residual train-control wayside + charging microgrids | €37 M |
| EPC overhead (7%) | €140 M |
| **CAPEX total** | **€2.15 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €1,244 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh mandalay`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€160 M / yr** | €93 |
| Steady-state, low-ridership (year 11+) | **€223 M / yr** | €129 |
| Steady-state, high-ridership (year 11+) | **€217 M / yr** | €126 |
| Lifecycle envelope (yr 1–30, low scenario) | **€6.07 bn cumulative** | €3,516 |
| Lifecycle envelope (yr 1–30, high scenario) | **€5.94 bn cumulative** | €3,443 |

_Population basis: 1,726,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€48 M / yr (low) → €42 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.29 bn | 4.5% | 30 y, 10 y grace | €99 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €537 M | 13.0% | 30 y, 10 y grace | €76 M / yr |
| Government equity (no debt service) | 15% | €322 M | — | — | — |
| **Total** | **100%** | **€2.15 bn** | | | **€175 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €58 M / yr + bonds €70 M / yr = **€128 M / yr** total — plus the equity tranche amortised across construction (€32 M / yr × 10 yr). Principal repayment begins in year 11 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €25 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €27 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €139 k |
| Traction energy (436.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,134 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €2.3 M |
| **OPEX subtotal** | | **€54 M / yr** |

_Annual fleet utilisation: 139 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 27.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$130 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.20 (~$0.22 USD) |
| Day pass (3 trips) | €0.51 (15 % bulk discount) |
| Monthly unlimited pass | €5.98 (~5 % of median monthly income) |
| Annual pass | €65.78 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 31.5 M | 63.0 M |
| Farebox revenue | €6.3 M / yr | €13 M / yr |
| Farebox / OPEX recovery | 12% | 23% |
| Country policy-target recovery (diagnostic) | 40% | 40% |
| Operating shortfall (gov subsidy required) | €48 M / yr | €42 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€223 M / yr** | **€217 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`mandalay.toml`](mandalay.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`mandalay-network-map.png`](mandalay-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`mandalay.corridor.geojson`](mandalay.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`mandalay.stations.json`](mandalay.stations.json) | Machine-readable station list |
| [`mandalay.design-quality.yaml`](mandalay.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug mandalay

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug mandalay \
    --sidecar .cache/osr-pipeline/rasters/mandalay.grid.json \
    --out-dir designs/.../Mandalay

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../mandalay.toml \
    --out designs/.../README.md
```

`scripts/regenerate-mandalay.sh` chains steps 3 + drift tests into a single command.
