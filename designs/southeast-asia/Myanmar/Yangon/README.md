# Yangon — Urban Rail Network

**Country:** MM · **Population:** 5,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Yangon rail network on OpenStreetMap](yangon-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`yangon.corridor.geojson`](yangon.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 213 |
| Interchange stations | 43 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.4% |
| Route length (double track) | 417.5 km |
| Revenue fleet | 301 × 6-car trainsets |
| Spare + cold-reserve | 34 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 53.5 km | 27 | 42 | NW Outer ↔ SE Outer |
| line-2 | 51.9 km | 23 | 41 | SE Outer ↔ NW Outer |
| line-3 | 42.3 km | 20 | 35 | NE Mid ↔ W Outer |
| line-4 | 32.1 km | 18 | 27 | SE Mid ↔ N Mid |
| line-5 | 39.0 km | 21 | 31 | S Outer ↔ N Mid |
| line-6 | 38.8 km | 19 | 31 | N Mid ↔ S Outer |
| line-7 | 43.8 km | 21 | 36 | E Mid ↔ SW Outer |
| line-8 | 38.6 km | 20 | 31 | SW Mid ↔ NE Outer |
| line-9 | 77.4 km | 45 | 61 | NW Mid ↔ NW Mid |
| **Total** | **417.5 km** | **213 unique** | **335** | |

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
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 7,920 = **142,560 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,425,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **293,279 – 439,919 trips/day**

## Catchment

- City population: **5,200,000**
- Anchor-weighted coverage: 56.4%
- Catchment population: **≈ 2,932,799** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 43 | 500 kW | 3000 kWh |
| Major | 97 | 400 kW | 2500 kWh |
| Standard | 51 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **207** | **88,100 kW** | **558,500 kWh** |

Aggregate station-rail charging power: **113,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,113 kWh | 46.4 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 532 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 440 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 558 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (375.2 km @ €3.5 M/km) | €1.31 bn |
| Elevated (39.3 km @ €18 M/km) | €708 M |
| Elevated-interchange premium (18 sites @ €20 M) | €360 M |
| **Civil subtotal** | **€2.38 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 7 | €0.4 M | €2.8 M |
| `standard` | 51 | €1.5 M | €76 M |
| `major` | 97 | €3.0 M | €291 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 4 | €4.5 M | €18 M |
| `interchange-elevated` | 39 | €4.5 M | €176 M |
| **Stations subtotal** | | | **€604 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 335 | €6.0 M | €2.01 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 417.5 km × €0.015 M/km | €6.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €85 M |
| EPC integration + project management (7%) | on subtotal | €361 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.38 bn |
| Stations | €604 M |
| Depots | €70 M |
| Rolling stock | €2.01 bn |
| Residual train-control wayside + charging microgrids | €91 M |
| EPC overhead (7%) | €361 M |
| **CAPEX total** | **€5.52 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,061 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh yangon`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€411 M / yr** | €79 |
| Steady-state, low-ridership (year 11+) | **€579 M / yr** | €111 |
| Steady-state, high-ridership (year 11+) | **€560 M / yr** | €108 |
| Lifecycle envelope (yr 1–30, low scenario) | **€15.69 bn cumulative** | €3,017 |
| Lifecycle envelope (yr 1–30, high scenario) | **€15.31 bn cumulative** | €2,944 |

_Population basis: 5,200,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€128 M / yr (low) → €109 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €3.31 bn | 4.5% | 30 y, 10 y grace | €254 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.38 bn | 13.0% | 30 y, 10 y grace | €196 M / yr |
| Government equity (no debt service) | 15% | €828 M | — | — | — |
| **Total** | **100%** | **€5.52 bn** | | | **€451 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €149 M / yr + bonds €179 M / yr = **€328 M / yr** total — plus the equity tranche amortised across construction (€83 M / yr × 10 yr). Principal repayment begins in year 11 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €80 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €61 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €311 k |
| Traction energy (1418.9 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,517 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.1 M |
| **OPEX subtotal** | | **€147 M / yr** |

_Annual fleet utilisation: 301 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 59.1 M train-km / yr (~196 k km / trainset / yr)._

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
| Annual paid trips | 94.9 M | 189.8 M |
| Farebox revenue | €19 M / yr | €38 M / yr |
| Farebox / OPEX recovery | 13% | 26% |
| Country policy-target recovery (diagnostic) | 40% | 40% |
| Operating shortfall (gov subsidy required) | €128 M / yr | €109 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€579 M / yr** | **€560 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`yangon.toml`](yangon.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`yangon-network-map.png`](yangon-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`yangon.corridor.geojson`](yangon.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`yangon.stations.json`](yangon.stations.json) | Machine-readable station list |
| [`yangon.design-quality.yaml`](yangon.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug yangon

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug yangon \
    --sidecar .cache/osr-pipeline/rasters/yangon.grid.json \
    --out-dir designs/.../Yangon

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../yangon.toml \
    --out designs/.../README.md
```

`scripts/regenerate-yangon.sh` chains steps 3 + drift tests into a single command.
