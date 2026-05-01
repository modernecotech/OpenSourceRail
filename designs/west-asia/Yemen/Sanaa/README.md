# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`sanaa.corridor.geojson`](sanaa.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 126 |
| Interchange stations | 32 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 78.0% |
| Route length (double track) | 260.8 km |
| Revenue fleet | 193 × 6-car trainsets |
| Spare + cold-reserve | 25 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.2 km | 17 | 34 | SE Outer ↔ NW Outer |
| line-2 | 28.8 km | 15 | 24 | S Mid ↔ N Outer |
| line-3 | 22.1 km | 10 | 19 | N Mid ↔ SW Mid |
| line-4 | 27.1 km | 13 | 23 | N Mid ↔ S Mid |
| line-5 | 27.1 km | 10 | 23 | SE Outer ↔ SW Inner |
| line-6 | 24.5 km | 12 | 20 | E Inner ↔ W Outer |
| line-7 | 20.6 km | 9 | 18 | NW Mid ↔ E Mid |
| line-8 | 17.2 km | 11 | 15 | SW Mid ↔ NE Inner |
| line-9 | 52.3 km | 29 | 42 | NW Mid ↔ W Inner |
| **Total** | **260.8 km** | **126 unique** | **218** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **307,125 – 460,687 trips/day**

## Catchment

- City population: **3,937,500**
- Anchor-weighted coverage: 78.0%
- Catchment population: **≈ 3,071,250** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 32 | 500 kW | 3000 kWh |
| Major | 34 | 400 kW | 2500 kWh |
| Standard | 36 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **118** | **52,900 kW** | **338,000 kWh** |

Aggregate station-rail charging power: **69,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 695 kWh | 29.0 km average line length |
| Onboard battery coverage | 1.0× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 548 kW average charger across stops |
| Stops to refill one trainset pack | 79 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 264 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 338 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (239.4 km @ €3.5 M/km) | €838 M |
| Elevated (20.6 km @ €18 M/km) | €370 M |
| Elevated-interchange premium (19 sites @ €20 M) | €380 M |
| **Civil subtotal** | **€1.59 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 8 | €0.4 M | €3.2 M |
| `standard` | 36 | €1.5 M | €54 M |
| `major` | 34 | €3.0 M | €102 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 32 | €4.5 M | €144 M |
| **Stations subtotal** | | | **€344 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 218 | €6.0 M | €1.31 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 260.8 km × €0.015 M/km | €3.9 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €50 M |
| EPC integration + project management (7%) | on subtotal | €235 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.59 bn |
| Stations | €344 M |
| Depots | €70 M |
| Rolling stock | €1.31 bn |
| Residual train-control wayside + charging microgrids | €53 M |
| EPC overhead (7%) | €235 M |
| **CAPEX total** | **€3.60 bn** |
| Per-route-km | €14 M / km |
| Per-capita (city pop) | €914 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh sanaa`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€281 M / yr** | €71 |
| Steady-state, low-ridership (year 11+) | **€359 M / yr** | €91 |
| Steady-state, high-ridership (year 11+) | **€350 M / yr** | €89 |
| Lifecycle envelope (yr 1–40, low scenario) | **€13.58 bn cumulative** | €3,448 |
| Lifecycle envelope (yr 1–40, high scenario) | **€13.31 bn cumulative** | €3,381 |

_Population basis: 3,937,500 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero and only the OPEX shortfall remains — ~€86 M / yr (low) → €77 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.16 bn | 3.0% | 40 y, 10 y grace | €110 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €900 M | 18.0% | 40 y, 10 y grace | €163 M / yr |
| Government equity (no debt service) | 15% | €540 M | — | — | — |
| **Total** | **100%** | **€3.60 bn** | | | **€273 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €65 M / yr + bonds €162 M / yr = **€227 M / yr** total — plus the equity tranche amortised across construction (€54 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €52 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €40 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €195 k |
| Traction energy (909.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,577 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.9 M |
| **OPEX subtotal** | | **€95 M / yr** |

_Annual fleet utilisation: 193 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 37.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$80 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.12 (~$0.13 USD) |
| Day pass (3 trips) | €0.31 (15 % bulk discount) |
| Monthly unlimited pass | €3.68 (~5 % of median monthly income) |
| Annual pass | €40.48 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 71.9 M | 143.7 M |
| Farebox revenue | €8.8 M / yr | €18 M / yr |
| Farebox / OPEX recovery | 9% | 19% |
| Country policy-target recovery (diagnostic) | 25% | 25% |
| Operating shortfall (gov subsidy required) | €86 M / yr | €77 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€359 M / yr** | **€350 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`sanaa-network-map.png`](sanaa-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`sanaa.stations.json`](sanaa.stations.json) | Machine-readable station list |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug sanaa

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug sanaa \
    --sidecar .cache/osr-pipeline/rasters/sanaa.grid.json \
    --out-dir designs/.../Sanaa

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../sanaa.toml \
    --out designs/.../README.md
```

`scripts/regenerate-sanaa.sh` chains steps 3 + drift tests into a single command.
