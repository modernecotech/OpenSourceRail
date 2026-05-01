# Mosul — Urban Rail Network

**Country:** IQ · **Population:** 1,940,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Mosul rail network on OpenStreetMap](mosul-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`mosul.corridor.geojson`](mosul.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 60 |
| Interchange stations | 4 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 38.2% |
| Route length (double track) | 144.6 km |
| Revenue fleet | 108 × 4-car trainsets |
| Spare + cold-reserve | 14 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 29.0 km | 14 | 25 | SW Mid ↔ E Outer |
| line-2 | 31.5 km | 12 | 26 | SE Outer ↔ NW Outer |
| line-3 | 32.3 km | 11 | 27 | NW Outer ↔ E Mid |
| line-4 | 27.6 km | 12 | 24 | N Mid ↔ S Outer |
| line-5 | 24.2 km | 11 | 20 | NE Outer ↔ W Mid |
| **Total** | **144.6 km** | **60 unique** | **122** | |

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
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 5,280 = **52,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **528,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **74,108 – 111,162 trips/day**

## Catchment

- City population: **1,940,000**
- Anchor-weighted coverage: 38.2%
- Catchment population: **≈ 741,080** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 4 | 500 kW | 3000 kWh |
| Major | 18 | 400 kW | 2500 kWh |
| Standard | 24 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **56** | **25,900 kW** | **172,000 kWh** |

Aggregate station-rail charging power: **34,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 463 kWh | 28.9 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.4 kWh/stop | 567 kW average charger across stops |
| Stops to refill one trainset pack | 51 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 130 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 172 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (117.3 km @ €3.5 M/km) | €411 M |
| Elevated (26.5 km @ €18 M/km) | €477 M |
| Elevated-interchange premium (5 sites @ €20 M) | €100 M |
| **Civil subtotal** | **€988 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | €0.4 M | €1.6 M |
| `standard` | 24 | €1.5 M | €36 M |
| `major` | 18 | €3.0 M | €54 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 4 | €4.5 M | €18 M |
| **Stations subtotal** | | | **€135 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 122 | €4.0 M | €488 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 144.6 km × €0.015 M/km | €2.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €20 M |
| EPC integration + project management (7%) | on subtotal | €118 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €988 M |
| Stations | €135 M |
| Depots | €52 M |
| Rolling stock | €488 M |
| Residual train-control wayside + charging microgrids | €23 M |
| EPC overhead (7%) | €118 M |
| **CAPEX total** | **€1.80 bn** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €930 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh mosul`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€136 M / yr** | €70 |
| Steady-state, low-ridership (year 6+) | **€155 M / yr** | €80 |
| Steady-state, high-ridership (year 6+) | **€134 M / yr** | €69 |
| Lifecycle envelope (yr 1–25, low scenario) | **€3.78 bn cumulative** | €1,947 |
| Lifecycle envelope (yr 1–25, high scenario) | **€3.36 bn cumulative** | €1,734 |

_Population basis: 1,940,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€28 M / yr (low) → €7.0 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.08 bn | 4.0% | 25 y, 5 y grace | €80 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €451 M | 8.5% | 25 y, 5 y grace | €48 M / yr |
| Government equity (no debt service) | 15% | €271 M | — | — | — |
| **Total** | **100%** | **€1.80 bn** | | | **€127 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €43 M / yr + bonds €38 M / yr = **€82 M / yr** total — plus the equity tranche amortised across construction (€54 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €20 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €23 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €108 k |
| Traction energy (339.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (880 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.2 M |
| **OPEX subtotal** | | **€48 M / yr** |

_Annual fleet utilisation: 108 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 21.2 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.58 (~$0.63 USD) |
| Day pass (3 trips) | €1.49 (15 % bulk discount) |
| Monthly unlimited pass | €17.48 (~5 % of median monthly income) |
| Annual pass | €192.28 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 35.4 M | 70.8 M |
| Farebox revenue | €21 M / yr | €41 M / yr |
| Farebox / OPEX recovery | 43% | 85% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €28 M / yr | €7.0 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€155 M / yr** | **€134 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`mosul.toml`](mosul.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`mosul-network-map.png`](mosul-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`mosul.corridor.geojson`](mosul.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`mosul.stations.json`](mosul.stations.json) | Machine-readable station list |
| [`mosul.design-quality.yaml`](mosul.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug mosul

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug mosul \
    --sidecar .cache/osr-pipeline/rasters/mosul.grid.json \
    --out-dir designs/.../Mosul

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../mosul.toml \
    --out designs/.../README.md
```

`scripts/regenerate-mosul.sh` chains steps 3 + drift tests into a single command.
