# Niamey — Urban Rail Network

**Country:** NE · **Population:** 1,407,635

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Niamey rail network on OpenStreetMap](niamey-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`niamey.corridor.geojson`](niamey.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 79 |
| Interchange stations | 11 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 38.4% |
| Route length (double track) | 146.0 km |
| Revenue fleet | 107 × 4-car trainsets |
| Spare + cold-reserve | 13 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 30.9 km | 17 | 26 | SE Outer ↔ NW Outer |
| line-2 | 24.7 km | 15 | 21 | N Outer ↔ SE Outer |
| line-3 | 28.7 km | 17 | 24 | SW Outer ↔ E Mid |
| line-4 | 61.6 km | 31 | 49 | NW Outer ↔ NW Outer |
| **Total** | **146.0 km** | **79 unique** | **120** | |

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
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 6,480 = **51,840 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **518,400 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **54,053 – 81,079 trips/day**

## Catchment

- City population: **1,407,635**
- Anchor-weighted coverage: 38.4%
- Catchment population: **≈ 540,531** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 11 | 500 kW | 3000 kWh |
| Major | 39 | 400 kW | 2500 kWh |
| Standard | 24 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **80** | **35,800 kW** | **233,500 kWh** |

Aggregate station-rail charging power: **43,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (139.0 km @ €3.5 M/km) | €487 M |
| Elevated (6.4 km @ €18 M/km) | €115 M |
| Elevated-interchange premium (5 sites @ €20 M) | €100 M |
| **Civil subtotal** | **€702 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 24 | €1.5 M | €36 M |
| `major` | 39 | €3.0 M | €117 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 11 | €4.5 M | €50 M |
| **Stations subtotal** | | | **€218 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 5 | €3.0 M | €15 M |
| **Depots subtotal** | | | **€40 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 120 | €4.0 M | €480 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 146.0 km × €0.015 M/km | €2.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no route traction power) | per-stop allowance by station archetype | €31 M |
| EPC integration + project management (7%) | on subtotal | €103 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €702 M |
| Stations | €218 M |
| Depots | €40 M |
| Rolling stock | €480 M |
| Residual train-control wayside + charging microgrids | €33 M |
| EPC overhead (7%) | €103 M |
| **CAPEX total** | **€1.58 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €1,120 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh niamey`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€87 M / yr** | €62 |
| Steady-state, low-ridership (year 11+) | **€131 M / yr** | €93 |
| Steady-state, high-ridership (year 11+) | **€127 M / yr** | €90 |
| Lifecycle envelope (yr 1–35, low scenario) | **€4.14 bn cumulative** | €2,939 |
| Lifecycle envelope (yr 1–35, high scenario) | **€4.04 bn cumulative** | €2,873 |

_Population basis: 1,407,635 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero and only the OPEX shortfall remains — ~€36 M / yr (low) → €32 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €946 M | 3.0% | 35 y, 10 y grace | €54 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €394 M | 9.0% | 35 y, 10 y grace | €40 M / yr |
| Government equity (no debt service) | 15% | €236 M | — | — | — |
| **Total** | **100%** | **€1.58 bn** | | | **€94 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €28 M / yr + bonds €35 M / yr = **€64 M / yr** total — plus the equity tranche amortised across construction (€24 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €19 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €19 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €109 k |
| Traction energy (336.3 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (888 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.3 M |
| **OPEX subtotal** | | **€40 M / yr** |

_Annual fleet utilisation: 107 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 21.0 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$95 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.15 (~$0.16 USD) |
| Day pass (3 trips) | €0.37 (15 % bulk discount) |
| Monthly unlimited pass | €4.37 (~5 % of median monthly income) |
| Annual pass | €48.07 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 25.7 M | 51.4 M |
| Farebox revenue | €3.7 M / yr | €7.5 M / yr |
| Farebox / OPEX recovery | 9% | 19% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €36 M / yr | €32 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€131 M / yr** | **€127 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`niamey.toml`](niamey.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`niamey-network-map.png`](niamey-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`niamey.corridor.geojson`](niamey.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`niamey.stations.json`](niamey.stations.json) | Machine-readable station list |
| [`niamey.design-quality.yaml`](niamey.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug niamey

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug niamey \
    --sidecar .cache/osr-pipeline/rasters/niamey.grid.json \
    --out-dir designs/.../Niamey

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../niamey.toml \
    --out designs/.../README.md
```

`scripts/regenerate-niamey.sh` chains steps 3 + drift tests into a single command.
