# Thika — Urban Rail Network

**Country:** KE · **Population:** 350,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Thika rail network on OpenStreetMap](thika-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`thika.corridor.geojson`](thika.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 38 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 62.6% |
| Route length (double track) | 75.5 km |
| Revenue fleet | 66 × 3-car trainsets |
| Spare + cold-reserve | 8 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 29.0 km | 15 | 28 | NE Outer ↔ SW Mid |
| line-2 | 21.3 km | 11 | 21 | W Mid ↔ E Mid |
| line-3 | 25.2 km | 12 | 25 | SW Outer ↔ NE Outer |
| **Total** | **75.5 km** | **38 unique** | **74** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 57 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 330 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 420 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 330 AW2 passengers (`light-metro-3car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 330 × 12 = **3,960 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 3,960 = **23,760 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **237,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **21,910 – 32,865 trips/day**

## Catchment

- City population: **350,000**
- Anchor-weighted coverage: 62.6%
- Catchment population: **≈ 219,100** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 2 | 400 kW | 2500 kWh |
| Standard | 24 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **35** | **17,000 kW** | **117,000 kWh** |

Aggregate station-rail charging power: **21,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 302 kWh | 25.2 km average line length |
| Onboard battery coverage | 1.2× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.3 kWh/stop | 559 kW average charger across stops |
| Stops to refill one trainset pack | 39 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 85 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 117 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (69.3 km @ €3.5 M/km) | €243 M |
| Elevated (5.9 km @ €18 M/km) | €105 M |
| Elevated-interchange premium (1 sites @ €20 M) | €20 M |
| **Civil subtotal** | **€368 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 24 | €1.5 M | €36 M |
| `major` | 2 | €3.0 M | €6.0 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 3 | €4.5 M | €14 M |
| **Stations subtotal** | | | **€72 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 74 | €3.0 M | €222 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 75.5 km × €0.015 M/km | €1.1 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €12 M |
| EPC integration + project management (7%) | on subtotal | €50 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €368 M |
| Stations | €72 M |
| Depots | €40 M |
| Rolling stock | €222 M |
| Residual train-control wayside + charging microgrids | €13 M |
| EPC overhead (7%) | €50 M |
| **CAPEX total** | **€765 M** |
| Per-route-km | €10 M / km |
| Per-capita (city pop) | €2,186 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh thika`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€59 M / yr** | €169 |
| Steady-state, low-ridership (year 8+) | **€74 M / yr** | €212 |
| Steady-state, high-ridership (year 8+) | **€72 M / yr** | €206 |
| Lifecycle envelope (yr 1–30, low scenario) | **€2.12 bn cumulative** | €6,067 |
| Lifecycle envelope (yr 1–30, high scenario) | **€2.07 bn cumulative** | €5,919 |

_Population basis: 350,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€18 M / yr (low) → €16 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €459 M | 4.5% | 30 y, 7 y grace | €32 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €191 M | 11.5% | 30 y, 7 y grace | €24 M / yr |
| Government equity (no debt service) | 15% | €115 M | — | — | — |
| **Total** | **100%** | **€765 M** | | | **€56 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €21 M / yr + bonds €22 M / yr = **€43 M / yr** total — plus the equity tranche amortised across construction (€16 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €8.9 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €9.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €56 k |
| Traction energy (133.3 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (465 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.7 M |
| **OPEX subtotal** | | **€20 M / yr** |

_Annual fleet utilisation: 66 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 11.1 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.35 (~$0.38 USD) |
| Day pass (3 trips) | €0.90 (15 % bulk discount) |
| Monthly unlimited pass | €10.58 (~5 % of median monthly income) |
| Annual pass | €116.38 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 6.4 M | 12.8 M |
| Farebox revenue | €2.3 M / yr | €4.5 M / yr |
| Farebox / OPEX recovery | 11% | 22% |
| Country policy-target recovery (diagnostic) | 50% | 50% |
| Operating shortfall (gov subsidy required) | €18 M / yr | €16 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€74 M / yr** | **€72 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`thika.toml`](thika.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`thika-network-map.png`](thika-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`thika.corridor.geojson`](thika.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`thika.stations.json`](thika.stations.json) | Machine-readable station list |
| [`thika.design-quality.yaml`](thika.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug thika

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug thika \
    --sidecar .cache/osr-pipeline/rasters/thika.grid.json \
    --out-dir designs/.../Thika

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../thika.toml \
    --out designs/.../README.md
```

`scripts/regenerate-thika.sh` chains steps 3 + drift tests into a single command.
