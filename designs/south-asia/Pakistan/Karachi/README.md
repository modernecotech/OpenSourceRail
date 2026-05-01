# Karachi — Urban Rail Network

**Country:** PK · **Population:** 20,300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Karachi rail network on OpenStreetMap](karachi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`karachi.corridor.geojson`](karachi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 231 |
| Interchange stations | 33 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 48.4% |
| Route length (double track) | 472.3 km |
| Revenue fleet | 337 × 6-car trainsets |
| Spare + cold-reserve | 40 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 57.8 km | 27 | 46 | NW Outer ↔ E Outer |
| line-2 | 47.2 km | 25 | 38 | W Outer ↔ SE Mid |
| line-3 | 45.5 km | 23 | 37 | N Outer ↔ SW Mid |
| line-4 | 46.3 km | 21 | 37 | E Mid ↔ W Outer |
| line-5 | 46.2 km | 25 | 37 | NE Outer ↔ S Mid |
| line-6 | 46.1 km | 24 | 37 | N Outer ↔ S Mid |
| line-7 | 37.4 km | 19 | 30 | W Mid ↔ E Outer |
| line-8 | 41.7 km | 16 | 34 | NE Outer ↔ SE Mid |
| line-9 | 104.1 km | 51 | 81 | NW Mid ↔ NW Mid |
| **Total** | **472.3 km** | **231 unique** | **377** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Nominal capacity | 900 pax (seated + standing, `metro-6car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 900 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 900 × 12 = **10,800 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 10,800 = **194,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,944,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **982,520 – 1,473,780 trips/day**

## Catchment

- City population: **20,300,000**
- Anchor-weighted coverage: 48.4%
- Catchment population: **≈ 9,825,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 33 | 500 kW | 3000 kWh |
| Major | 94 | 400 kW | 2500 kWh |
| Standard | 83 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **226** | **91,500 kW** | **585,000 kWh** |

Aggregate station-rail charging power: **122,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (435.6 km @ €3.5 M/km) | €1.52 bn |
| Elevated (34.7 km @ €18 M/km) | €625 M |
| Elevated-interchange premium (25 sites @ €20 M) | €500 M |
| **Civil subtotal** | **€2.65 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | €0.4 M | €2.0 M |
| `standard` | 83 | €1.5 M | €124 M |
| `major` | 94 | €3.0 M | €282 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 33 | €4.5 M | €148 M |
| **Stations subtotal** | | | **€598 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 15 | €3.0 M | €45 M |
| **Depots subtotal** | | | **€70 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 377 | €6.0 M | €2.26 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 472.3 km × €0.015 M/km | €7.1 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no route traction power) | per-stop allowance by station archetype | €86 M |
| EPC integration + project management (7%) | on subtotal | €397 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.65 bn |
| Stations | €598 M |
| Depots | €70 M |
| Rolling stock | €2.26 bn |
| Residual train-control wayside + charging microgrids | €93 M |
| EPC overhead (7%) | €397 M |
| **CAPEX total** | **€6.07 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €299 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh karachi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€526 M / yr** | €26 |
| Steady-state, low-ridership (year 8+) | **€574 M / yr** | €28 |
| Steady-state, high-ridership (year 8+) | **€503 M / yr** | €25 |
| Lifecycle envelope (yr 1–30, low scenario) | **€16.88 bn cumulative** | €831 |
| Lifecycle envelope (yr 1–30, high scenario) | **€15.25 bn cumulative** | €751 |

_Population basis: 20,300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€71 M / yr (low) → €0 k / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €3.64 bn | 4.0% | 30 y, 7 y grace | €245 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.52 bn | 16.5% | 30 y, 7 y grace | €258 M / yr |
| Government equity (no debt service) | 15% | €910 M | — | — | — |
| **Total** | **100%** | **€6.07 bn** | | | **€503 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €146 M / yr + bonds €250 M / yr = **€396 M / yr** total — plus the equity tranche amortised across construction (€130 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €90 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €66 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €353 k |
| Traction energy (1588.6 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,846 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €7.3 M |
| **OPEX subtotal** | | **€164 M / yr** |

_Annual fleet utilisation: 337 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 66.2 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.25 (~$0.28 USD) |
| Day pass (3 trips) | €0.65 (15 % bulk discount) |
| Monthly unlimited pass | €7.59 (~5 % of median monthly income) |
| Annual pass | €83.49 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 370.5 M | 741.0 M |
| Farebox revenue | €94 M / yr | €187 M / yr |
| Farebox / OPEX recovery | 57% | 114% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €71 M / yr | €0 k / yr |
| Operating surplus (operator retained → capex sinking fund) | €0 k / yr | €23 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€574 M / yr** | **€503 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`karachi.toml`](karachi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`karachi-network-map.png`](karachi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`karachi.corridor.geojson`](karachi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`karachi.stations.json`](karachi.stations.json) | Machine-readable station list |
| [`karachi.design-quality.yaml`](karachi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug karachi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug karachi \
    --sidecar .cache/osr-pipeline/rasters/karachi.grid.json \
    --out-dir designs/.../Karachi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../karachi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-karachi.sh` chains steps 3 + drift tests into a single command.
