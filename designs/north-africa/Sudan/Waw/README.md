# Waw — Urban Rail Network

**Country:** SD · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Waw rail network on OpenStreetMap](waw-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`waw.corridor.geojson`](waw.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 2 |
| Unique stations | 11 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 72.9% |
| Route length (double track) | 17.9 km |
| Revenue fleet | 23 × 2-car trainsets |
| Spare + cold-reserve | 4 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 |  8.1 km | 5 | 13 | NW Mid ↔ S Outer |
| line-2 |  9.7 km | 6 | 14 | N Outer ↔ W Inner |
| **Total** | **17.9 km** | **11 unique** | **27** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 210 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 260 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 210 AW2 passengers (`tram-2car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 210 × 12 = **2,520 pphpd**
- **Network peak throughput (all lines, both directions):** 2 lines × 2 directions × 2,520 = **10,080 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **100,800 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **21,870 – 32,805 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 72.9%
- Catchment population: **≈ 218,700** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 2 | 400 kW | 2500 kWh |
| Standard | 3 | 300 kW | 2000 kWh |
| Terminal | 3 | 500 kW | 3000 kWh |
| **Total installed** | **11** | **9,200 kW** | **66,000 kWh** |

Aggregate station-rail charging power: **7,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 72 kWh | 8.9 km average line length |
| Onboard battery coverage | 3.4× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 11.4 kWh/stop | 682 kW average charger across stops |
| Stops to refill one trainset pack | 21 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 46 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 66 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (16.6 km @ €3.5 M/km) | €58 M |
| Elevated (1.1 km @ €18 M/km) | €20 M |
| Elevated-interchange premium (1 sites @ €20 M) | €20 M |
| **Civil subtotal** | **€98 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 3 | €1.5 M | €4.5 M |
| `major` | 2 | €3.0 M | €6.0 M |
| `terminal` | 3 | €2.5 M | €7.5 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| **Stations subtotal** | | | **€30 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 3 | €3.0 M | €9.0 M |
| **Depots subtotal** | | | **€34 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 27 | €2.0 M | €54 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 17.9 km × €0.015 M/km | €0.3 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €4.7 M |
| EPC integration + project management (7%) | on subtotal | €15 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €98 M |
| Stations | €30 M |
| Depots | €34 M |
| Rolling stock | €54 M |
| Residual train-control wayside + charging microgrids | €5.0 M |
| EPC overhead (7%) | €15 M |
| **CAPEX total** | **€237 M** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €789 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh waw`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€17 M / yr** | €56 |
| Steady-state, low-ridership (year 11+) | **€21 M / yr** | €70 |
| Steady-state, high-ridership (year 11+) | **€20 M / yr** | €67 |
| Lifecycle envelope (yr 1–40, low scenario) | **€795 M cumulative** | €2,651 |
| Lifecycle envelope (yr 1–40, high scenario) | **€768 M cumulative** | €2,559 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero and only the OPEX shortfall remains — ~€4.7 M / yr (low) → €3.8 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €142 M | 3.0% | 40 y, 10 y grace | €7.2 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €59 M | 15.0% | 40 y, 10 y grace | €9.0 M / yr |
| Government equity (no debt service) | 15% | €35 M | — | — | — |
| **Total** | **100%** | **€237 M** | | | **€16 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €4.3 M / yr + bonds €8.9 M / yr = **€13 M / yr** total — plus the equity tranche amortised across construction (€3.5 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €2.2 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €3.2 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €13 k |
| Traction energy (22.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (119 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €202 k |
| **OPEX subtotal** | | **€5.6 M / yr** |

_Annual fleet utilisation: 23 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 2.8 M train-km / yr (~123 k km / trainset / yr)._

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
| Annual paid trips | 5.5 M | 10.9 M |
| Farebox revenue | €923 k / yr | €1.8 M / yr |
| Farebox / OPEX recovery | 16% | 33% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €4.7 M / yr | €3.8 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€21 M / yr** | **€20 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`waw.toml`](waw.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`waw-network-map.png`](waw-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`waw.corridor.geojson`](waw.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`waw.stations.json`](waw.stations.json) | Machine-readable station list |
| [`waw.design-quality.yaml`](waw.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug waw

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug waw \
    --sidecar .cache/osr-pipeline/rasters/waw.grid.json \
    --out-dir designs/.../Waw

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../waw.toml \
    --out designs/.../README.md
```

`scripts/regenerate-waw.sh` chains steps 3 + drift tests into a single command.
