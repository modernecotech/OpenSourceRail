# Kisangani — Urban Rail Network

**Country:** CD · **Population:** 1,300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kisangani rail network on OpenStreetMap](kisangani-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kisangani.corridor.geojson`](kisangani.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 2 |
| Unique stations | 26 |
| Interchange stations | 4 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 63.7% |
| Route length (double track) | 47.3 km |
| Revenue fleet | 36 × 4-car trainsets |
| Spare + cold-reserve | 4 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 24.9 km | 12 | 21 | SE Outer ↔ NW Outer |
| line-2 | 22.4 km | 15 | 19 | W Inner ↔ W Inner |
| **Total** | **47.3 km** | **26 unique** | **40** | |

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
- **Network peak throughput (all lines, both directions):** 2 lines × 2 directions × 5,280 = **21,120 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **211,200 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **82,810 – 124,215 trips/day**

## Catchment

- City population: **1,300,000**
- Anchor-weighted coverage: 63.7%
- Catchment population: **≈ 828,100** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 4 | 500 kW | 3000 kWh |
| Major | 14 | 400 kW | 2500 kWh |
| Standard | 6 | 300 kW | 2000 kWh |
| Terminal | 1 | 500 kW | 3000 kWh |
| **Total installed** | **26** | **14,900 kW** | **102,000 kWh** |

Aggregate station-rail charging power: **14,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 378 kWh | 23.6 km average line length |
| Onboard battery coverage | 1.3× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 548 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 74 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 102 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (44.2 km @ €3.5 M/km) | €155 M |
| Elevated (2.8 km @ €18 M/km) | €50 M |
| Elevated-interchange premium (2 sites @ €20 M) | €40 M |
| **Civil subtotal** | **€245 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | €0.4 M | €0.4 M |
| `standard` | 6 | €1.5 M | €9.0 M |
| `major` | 14 | €3.0 M | €42 M |
| `terminal` | 1 | €2.5 M | €2.5 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 4 | €4.5 M | €18 M |
| **Stations subtotal** | | | **€75 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 1 | €3.0 M | €3.0 M |
| **Depots subtotal** | | | **€28 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 40 | €4.0 M | €160 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 47.3 km × €0.015 M/km | €0.7 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €11 M |
| EPC integration + project management (7%) | on subtotal | €36 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €245 M |
| Stations | €75 M |
| Depots | €28 M |
| Rolling stock | €160 M |
| Residual train-control wayside + charging microgrids | €11 M |
| EPC overhead (7%) | €36 M |
| **CAPEX total** | **€556 M** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €427 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kisangani`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€36 M / yr** | €28 |
| Steady-state, low-ridership (year 11+) | **€45 M / yr** | €35 |
| Steady-state, high-ridership (year 11+) | **€41 M / yr** | €32 |
| Lifecycle envelope (yr 1–40, low scenario) | **€1.73 bn cumulative** | €1,328 |
| Lifecycle envelope (yr 1–40, high scenario) | **€1.61 bn cumulative** | €1,236 |

_Population basis: 1,300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero and only the OPEX shortfall remains — ~€9.9 M / yr (low) → €5.9 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €333 M | 3.0% | 40 y, 10 y grace | €17 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €139 M | 13.0% | 40 y, 10 y grace | €19 M / yr |
| Government equity (no debt service) | 15% | €83 M | — | — | — |
| **Total** | **100%** | **€556 M** | | | **€36 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €10.0 M / yr + bonds €18 M / yr = **€28 M / yr** total — plus the equity tranche amortised across construction (€8.3 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €6.4 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €7.0 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €35 k |
| Traction energy (113.1 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (296 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €503 k |
| **OPEX subtotal** | | **€14 M / yr** |

_Annual fleet utilisation: 36 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 7.1 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$110 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.17 (~$0.18 USD) |
| Day pass (3 trips) | €0.43 (15 % bulk discount) |
| Monthly unlimited pass | €5.06 (~5 % of median monthly income) |
| Annual pass | €55.66 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 23.7 M | 47.5 M |
| Farebox revenue | €4.0 M / yr | €8.0 M / yr |
| Farebox / OPEX recovery | 29% | 58% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €9.9 M / yr | €5.9 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€45 M / yr** | **€41 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kisangani.toml`](kisangani.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kisangani-network-map.png`](kisangani-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kisangani.corridor.geojson`](kisangani.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kisangani.stations.json`](kisangani.stations.json) | Machine-readable station list |
| [`kisangani.design-quality.yaml`](kisangani.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kisangani

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kisangani \
    --sidecar .cache/osr-pipeline/rasters/kisangani.grid.json \
    --out-dir designs/.../Kisangani

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kisangani.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kisangani.sh` chains steps 3 + drift tests into a single command.
