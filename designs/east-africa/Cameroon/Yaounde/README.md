# Yaounde — Urban Rail Network

**Country:** CM · **Population:** 4,100,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Yaounde rail network on OpenStreetMap](yaounde-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`yaounde.corridor.geojson`](yaounde.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 135 |
| Interchange stations | 28 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 43.4% |
| Route length (double track) | 266.7 km |
| Revenue fleet | 196 × 6-car trainsets |
| Spare + cold-reserve | 23 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 39.9 km | 21 | 32 | SW Mid ↔ NE Outer |
| line-2 | 36.9 km | 14 | 30 | SW Mid ↔ NE Outer |
| line-3 | 22.6 km | 12 | 19 | S Mid ↔ NE Mid |
| line-4 | 28.2 km | 16 | 24 | SE Outer ↔ NW Inner |
| line-5 | 28.5 km | 15 | 24 | SE Mid ↔ W Mid |
| line-6 | 24.7 km | 11 | 21 | E Mid ↔ N Mid |
| line-7 | 35.6 km | 16 | 29 | NW Outer ↔ S Inner |
| line-8 | 50.2 km | 31 | 40 | W Inner ↔ W Inner |
| **Total** | **266.7 km** | **135 unique** | **219** | |

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
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 10,800 = **172,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,728,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **177,940 – 266,910 trips/day**

## Catchment

- City population: **4,100,000**
- Anchor-weighted coverage: 43.4%
- Catchment population: **≈ 1,779,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 28 | 500 kW | 3000 kWh |
| Major | 46 | 400 kW | 2500 kWh |
| Standard | 44 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **132** | **57,100 kW** | **366,000 kWh** |

Aggregate station-rail charging power: **74,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (240.6 km @ €3.5 M/km) | €842 M |
| Elevated (20.8 km @ €18 M/km) | €375 M |
| Elevated-interchange premium (15 sites @ €20 M) | €300 M |
| **Civil subtotal** | **€1.52 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | €0.4 M | €1.6 M |
| `standard` | 44 | €1.5 M | €66 M |
| `major` | 46 | €3.0 M | €138 M |
| `terminal` | 13 | €2.5 M | €32 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 28 | €4.5 M | €126 M |
| **Stations subtotal** | | | **€367 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 13 | €3.0 M | €39 M |
| **Depots subtotal** | | | **€64 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 219 | €6.0 M | €1.31 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 266.7 km × €0.015 M/km | €3.9 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no route traction power) | per-stop allowance by station archetype | €53 M |
| EPC integration + project management (7%) | on subtotal | €232 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.52 bn |
| Stations | €367 M |
| Depots | €64 M |
| Rolling stock | €1.31 bn |
| Residual train-control wayside + charging microgrids | €57 M |
| EPC overhead (7%) | €232 M |
| **CAPEX total** | **€3.55 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €866 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh yaounde`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€233 M / yr** | €57 |
| Steady-state, low-ridership (year 8+) | **€305 M / yr** | €74 |
| Steady-state, high-ridership (year 8+) | **€285 M / yr** | €69 |
| Lifecycle envelope (yr 1–30, low scenario) | **€8.65 bn cumulative** | €2,109 |
| Lifecycle envelope (yr 1–30, high scenario) | **€8.17 bn cumulative** | €1,994 |

_Population basis: 4,100,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€76 M / yr (low) → €55 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.13 bn | 3.8% | 30 y, 7 y grace | €141 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €888 M | 8.5% | 30 y, 7 y grace | €89 M / yr |
| Government equity (no debt service) | 15% | €533 M | — | — | — |
| **Total** | **100%** | **€3.55 bn** | | | **€230 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €81 M / yr + bonds €75 M / yr = **€156 M / yr** total — plus the equity tranche amortised across construction (€76 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €53 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €39 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €196 k |
| Traction energy (923.9 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,612 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €4.5 M |
| **OPEX subtotal** | | **€96 M / yr** |

_Annual fleet utilisation: 196 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 38.5 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$180 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.28 (~$0.30 USD) |
| Day pass (3 trips) | €0.70 (15 % bulk discount) |
| Monthly unlimited pass | €8.28 (~5 % of median monthly income) |
| Annual pass | €91.08 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 74.8 M | 149.7 M |
| Farebox revenue | €21 M / yr | €41 M / yr |
| Farebox / OPEX recovery | 21% | 43% |
| Country policy-target recovery (diagnostic) | 40% | 40% |
| Operating shortfall (gov subsidy required) | €76 M / yr | €55 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€305 M / yr** | **€285 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`yaounde.toml`](yaounde.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`yaounde-network-map.png`](yaounde-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`yaounde.corridor.geojson`](yaounde.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`yaounde.stations.json`](yaounde.stations.json) | Machine-readable station list |
| [`yaounde.design-quality.yaml`](yaounde.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug yaounde

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug yaounde \
    --sidecar .cache/osr-pipeline/rasters/yaounde.grid.json \
    --out-dir designs/.../Yaounde

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../yaounde.toml \
    --out designs/.../README.md
```

`scripts/regenerate-yaounde.sh` chains steps 3 + drift tests into a single command.
