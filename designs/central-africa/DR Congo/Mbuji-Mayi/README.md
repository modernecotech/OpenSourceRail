# Mbuji-Mayi — Urban Rail Network

**Country:** CD · **Population:** 2,500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Mbuji-Mayi rail network on OpenStreetMap](mbuji-mayi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`mbuji-mayi.corridor.geojson`](mbuji-mayi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 55 |
| Interchange stations | 11 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 70.2% |
| Route length (double track) | 118.3 km |
| Revenue fleet | 89 × 4-car trainsets |
| Spare + cold-reserve | 12 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 29.3 km | 15 | 25 | E Outer ↔ W Outer |
| line-2 | 27.8 km | 12 | 24 | NE Outer ↔ SW Mid |
| line-3 | 17.4 km | 8 | 16 | SE Mid ↔ SW Mid |
| line-4 | 43.8 km | 20 | 36 | W Mid ↔ W Outer |
| **Total** | **118.3 km** | **55 unique** | **101** | |

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
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 5,280 = **42,240 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **422,400 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **175,500 – 263,250 trips/day**

## Catchment

- City population: **2,500,000**
- Anchor-weighted coverage: 70.2%
- Catchment population: **≈ 1,755,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 11 | 500 kW | 3000 kWh |
| Major | 15 | 400 kW | 2500 kWh |
| Standard | 20 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **52** | **25,000 kW** | **165,500 kWh** |

Aggregate station-rail charging power: **29,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 473 kWh | 29.6 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.0 kWh/stop | 541 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 125 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 166 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (112.7 km @ €3.5 M/km) | €394 M |
| Elevated (5.3 km @ €18 M/km) | €96 M |
| Elevated-interchange premium (4 sites @ €20 M) | €80 M |
| **Civil subtotal** | **€570 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 20 | €1.5 M | €30 M |
| `major` | 15 | €3.0 M | €45 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| `interchange-elevated` | 9 | €4.5 M | €40 M |
| **Stations subtotal** | | | **€141 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 101 | €4.0 M | €404 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 118.3 km × €0.015 M/km | €1.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €21 M |
| EPC integration + project management (7%) | on subtotal | €82 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €570 M |
| Stations | €141 M |
| Depots | €40 M |
| Rolling stock | €404 M |
| Residual train-control wayside + charging microgrids | €22 M |
| EPC overhead (7%) | €82 M |
| **CAPEX total** | **€1.26 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €504 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh mbuji-mayi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€83 M / yr** | €33 |
| Steady-state, low-ridership (year 11+) | **€105 M / yr** | €42 |
| Steady-state, high-ridership (year 11+) | **€98 M / yr** | €39 |
| Lifecycle envelope (yr 1–40, low scenario) | **€3.99 bn cumulative** | €1,596 |
| Lifecycle envelope (yr 1–40, high scenario) | **€3.76 bn cumulative** | €1,503 |

_Population basis: 2,500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero and only the OPEX shortfall remains — ~€25 M / yr (low) → €17 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €756 M | 3.0% | 40 y, 10 y grace | €39 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €315 M | 13.0% | 40 y, 10 y grace | €42 M / yr |
| Government equity (no debt service) | 15% | €189 M | — | — | — |
| **Total** | **100%** | **€1.26 bn** | | | **€81 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €23 M / yr + bonds €41 M / yr = **€64 M / yr** total — plus the equity tranche amortised across construction (€19 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €16 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €15 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €89 k |
| Traction energy (279.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (722 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.2 M |
| **OPEX subtotal** | | **€33 M / yr** |

_Annual fleet utilisation: 89 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 17.5 M train-km / yr (~196 k km / trainset / yr)._

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
| Annual paid trips | 45.6 M | 91.2 M |
| Farebox revenue | €7.7 M / yr | €15 M / yr |
| Farebox / OPEX recovery | 24% | 47% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €25 M / yr | €17 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€105 M / yr** | **€98 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`mbuji-mayi.toml`](mbuji-mayi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`mbuji-mayi-network-map.png`](mbuji-mayi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`mbuji-mayi.corridor.geojson`](mbuji-mayi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`mbuji-mayi.stations.json`](mbuji-mayi.stations.json) | Machine-readable station list |
| [`mbuji-mayi.design-quality.yaml`](mbuji-mayi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug mbuji-mayi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug mbuji-mayi \
    --sidecar .cache/osr-pipeline/rasters/mbuji-mayi.grid.json \
    --out-dir designs/.../Mbuji-Mayi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../mbuji-mayi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-mbuji-mayi.sh` chains steps 3 + drift tests into a single command.
