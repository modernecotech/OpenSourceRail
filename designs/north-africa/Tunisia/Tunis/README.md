# Tunis — Urban Rail Network

**Country:** TN · **Population:** 2,900,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Tunis rail network on OpenStreetMap](tunis-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`tunis.corridor.geojson`](tunis.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 117 |
| Interchange stations | 20 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 47.8% |
| Route length (double track) | 240.3 km |
| Revenue fleet | 174 × 4-car trainsets |
| Spare + cold-reserve | 20 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 45.4 km | 22 | 37 | SE Outer ↔ W Mid |
| line-2 | 38.2 km | 20 | 31 | NE Outer ↔ W Outer |
| line-3 | 32.8 km | 18 | 27 | S Mid ↔ N Mid |
| line-4 | 40.6 km | 19 | 34 | NW Outer ↔ SE Outer |
| line-5 | 83.3 km | 39 | 65 | W Mid ↔ W Mid |
| **Total** | **240.3 km** | **117 unique** | **194** | |

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
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 6,480 = **64,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **648,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **138,620 – 207,930 trips/day**

## Catchment

- City population: **2,900,000**
- Anchor-weighted coverage: 47.8%
- Catchment population: **≈ 1,386,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 20 | 500 kW | 3000 kWh |
| Major | 43 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **117** | **49,500 kW** | **320,500 kWh** |

Aggregate station-rail charging power: **62,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 769 kWh | 48.1 km average line length |
| Onboard battery coverage | 0.6× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 536 kW average charger across stops |
| Stops to refill one trainset pack | 54 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 248 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 320 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (226.3 km @ €3.5 M/km) | €792 M |
| Elevated (13.1 km @ €18 M/km) | €236 M |
| Elevated-interchange premium (11 sites @ €20 M) | €220 M |
| **Civil subtotal** | **€1.25 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | €0.4 M | €0.4 M |
| `standard` | 46 | €1.5 M | €69 M |
| `major` | 43 | €3.0 M | €129 M |
| `terminal` | 7 | €2.5 M | €18 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 20 | €4.5 M | €90 M |
| **Stations subtotal** | | | **€309 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 7 | €3.0 M | €21 M |
| **Depots subtotal** | | | **€46 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 194 | €4.0 M | €776 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 240.3 km × €0.015 M/km | €3.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €44 M |
| EPC integration + project management (7%) | on subtotal | €170 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.25 bn |
| Stations | €309 M |
| Depots | €46 M |
| Rolling stock | €776 M |
| Residual train-control wayside + charging microgrids | €48 M |
| EPC overhead (7%) | €170 M |
| **CAPEX total** | **€2.60 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €896 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh tunis`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€206 M / yr** | €71 |
| Steady-state, low-ridership (year 6+) | **€234 M / yr** | €81 |
| Steady-state, high-ridership (year 6+) | **€205 M / yr** | €71 |
| Lifecycle envelope (yr 1–25, low scenario) | **€5.71 bn cumulative** | €1,968 |
| Lifecycle envelope (yr 1–25, high scenario) | **€5.14 bn cumulative** | €1,772 |

_Population basis: 2,900,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€43 M / yr (low) → €14 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.56 bn | 4.5% | 25 y, 5 y grace | €120 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €649 M | 9.0% | 25 y, 5 y grace | €71 M / yr |
| Government equity (no debt service) | 15% | €390 M | — | — | — |
| **Total** | **100%** | **€2.60 bn** | | | **€191 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €70 M / yr + bonds €58 M / yr = **€129 M / yr** total — plus the equity tranche amortised across construction (€78 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €31 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €32 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €180 k |
| Traction energy (546.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,454 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €7.9 M |
| **OPEX subtotal** | | **€71 M / yr** |

_Annual fleet utilisation: 174 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 34.2 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$350 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.54 (~$0.58 USD) |
| Day pass (3 trips) | €1.37 (15 % bulk discount) |
| Monthly unlimited pass | €16.10 (~5 % of median monthly income) |
| Annual pass | €177.10 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 52.9 M | 105.8 M |
| Farebox revenue | €28 M / yr | €57 M / yr |
| Farebox / OPEX recovery | 40% | 80% |
| Country policy-target recovery (diagnostic) | 50% | 50% |
| Operating shortfall (gov subsidy required) | €43 M / yr | €14 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€234 M / yr** | **€205 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`tunis.toml`](tunis.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`tunis-network-map.png`](tunis-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`tunis.corridor.geojson`](tunis.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`tunis.stations.json`](tunis.stations.json) | Machine-readable station list |
| [`tunis.design-quality.yaml`](tunis.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug tunis

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug tunis \
    --sidecar .cache/osr-pipeline/rasters/tunis.grid.json \
    --out-dir designs/.../Tunis

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../tunis.toml \
    --out designs/.../README.md
```

`scripts/regenerate-tunis.sh` chains steps 3 + drift tests into a single command.
