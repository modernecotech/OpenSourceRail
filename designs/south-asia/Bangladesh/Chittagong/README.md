# Chittagong — Urban Rail Network

**Country:** BD · **Population:** 5,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Chittagong rail network on OpenStreetMap](chittagong-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`chittagong.corridor.geojson`](chittagong.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 160 |
| Interchange stations | 36 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 63.6% |
| Route length (double track) | 374.2 km |
| Revenue fleet | 271 × 6-car trainsets |
| Spare + cold-reserve | 31 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 48.6 km | 23 | 39 | NW Outer ↔ S Mid |
| line-2 | 44.2 km | 19 | 36 | S Mid ↔ N Outer |
| line-3 | 42.8 km | 19 | 35 | NE Outer ↔ S Mid |
| line-4 | 39.9 km | 18 | 32 | SW Mid ↔ N Outer |
| line-5 | 42.1 km | 17 | 35 | SE Outer ↔ NW Mid |
| line-6 | 38.0 km | 17 | 31 | NE Outer ↔ SW Inner |
| line-7 | 39.6 km | 14 | 32 | W Inner ↔ NE Outer |
| line-8 | 78.9 km | 34 | 62 | NW Mid ↔ NW Mid |
| **Total** | **374.2 km** | **160 unique** | **302** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **330,720 – 496,080 trips/day**

## Catchment

- City population: **5,200,000**
- Anchor-weighted coverage: 63.6%
- Catchment population: **≈ 3,307,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 36 | 500 kW | 3000 kWh |
| Major | 33 | 400 kW | 2500 kWh |
| Standard | 67 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **150** | **62,800 kW** | **403,500 kWh** |

Aggregate station-rail charging power: **84,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,123 kWh | 46.8 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 530 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 314 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 404 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (330.5 km @ €3.5 M/km) | €1.16 bn |
| Elevated (37.6 km @ €18 M/km) | €676 M |
| Elevated-interchange premium (18 sites @ €20 M) | €360 M |
| **Civil subtotal** | **€2.19 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 11 | €0.4 M | €4.4 M |
| `standard` | 67 | €1.5 M | €100 M |
| `major` | 33 | €3.0 M | €99 M |
| `terminal` | 13 | €2.5 M | €32 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| `interchange-elevated` | 34 | €4.5 M | €153 M |
| **Stations subtotal** | | | **€401 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 302 | €6.0 M | €1.81 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 374.2 km × €0.015 M/km | €5.5 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €59 M |
| EPC integration + project management (7%) | on subtotal | €317 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.19 bn |
| Stations | €401 M |
| Depots | €64 M |
| Rolling stock | €1.81 bn |
| Residual train-control wayside + charging microgrids | €64 M |
| EPC overhead (7%) | €317 M |
| **CAPEX total** | **€4.85 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €933 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh chittagong`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€318 M / yr** | €61 |
| Steady-state, low-ridership (year 8+) | **€418 M / yr** | €80 |
| Steady-state, high-ridership (year 8+) | **€390 M / yr** | €75 |
| Lifecycle envelope (yr 1–30, low scenario) | **€11.84 bn cumulative** | €2,277 |
| Lifecycle envelope (yr 1–30, high scenario) | **€11.19 bn cumulative** | €2,152 |

_Population basis: 5,200,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€104 M / yr (low) → €76 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.91 bn | 3.8% | 30 y, 7 y grace | €192 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.21 bn | 8.5% | 30 y, 7 y grace | €122 M / yr |
| Government equity (no debt service) | 15% | €728 M | — | — | — |
| **Total** | **100%** | **€4.85 bn** | | | **€314 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €111 M / yr + bonds €103 M / yr = **€214 M / yr** total — plus the equity tranche amortised across construction (€104 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €72 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €53 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €276 k |
| Traction energy (1277.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,257 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €6.8 M |
| **OPEX subtotal** | | **€133 M / yr** |

_Annual fleet utilisation: 271 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 53.2 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$195 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.30 (~$0.33 USD) |
| Day pass (3 trips) | €0.76 (15 % bulk discount) |
| Monthly unlimited pass | €8.97 (~5 % of median monthly income) |
| Annual pass | €98.67 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 94.9 M | 189.8 M |
| Farebox revenue | €28 M / yr | €57 M / yr |
| Farebox / OPEX recovery | 21% | 43% |
| Country policy-target recovery (diagnostic) | 50% | 50% |
| Operating shortfall (gov subsidy required) | €104 M / yr | €76 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€418 M / yr** | **€390 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`chittagong.toml`](chittagong.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`chittagong-network-map.png`](chittagong-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`chittagong.corridor.geojson`](chittagong.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`chittagong.stations.json`](chittagong.stations.json) | Machine-readable station list |
| [`chittagong.design-quality.yaml`](chittagong.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug chittagong

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug chittagong \
    --sidecar .cache/osr-pipeline/rasters/chittagong.grid.json \
    --out-dir designs/.../Chittagong

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../chittagong.toml \
    --out designs/.../README.md
```

`scripts/regenerate-chittagong.sh` chains steps 3 + drift tests into a single command.
