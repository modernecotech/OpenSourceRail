# Durban — Urban Rail Network

**Country:** ZA · **Population:** 3,900,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Durban rail network on OpenStreetMap](durban-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`durban.corridor.geojson`](durban.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 171 |
| Interchange stations | 42 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 79.4% |
| Route length (double track) | 401.3 km |
| Revenue fleet | 290 × 6-car trainsets |
| Spare + cold-reserve | 35 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 57.2 km | 23 | 46 | S Outer ↔ NE Mid |
| line-2 | 44.1 km | 17 | 36 | SW Mid ↔ NE Mid |
| line-3 | 48.9 km | 18 | 39 | S Mid ↔ N Outer |
| line-4 | 26.4 km | 11 | 23 | SW Mid ↔ E Mid |
| line-5 | 38.0 km | 17 | 31 | E Mid ↔ NW Outer |
| line-6 | 33.2 km | 12 | 27 | SE Mid ↔ W Mid |
| line-7 | 28.2 km | 12 | 24 | W Mid ↔ E Inner |
| line-8 | 32.9 km | 16 | 27 | E Inner ↔ NW Mid |
| line-9 | 92.6 km | 46 | 72 | W Mid ↔ W Mid |
| **Total** | **401.3 km** | **171 unique** | **325** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **309,660 – 464,490 trips/day**

## Catchment

- City population: **3,900,000**
- Anchor-weighted coverage: 79.4%
- Catchment population: **≈ 3,096,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 42 | 500 kW | 3000 kWh |
| Major | 13 | 400 kW | 2500 kWh |
| Standard | 95 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **166** | **67,200 kW** | **433,500 kWh** |

Aggregate station-rail charging power: **92,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,070 kWh | 44.6 km average line length |
| Onboard battery coverage | 0.7× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.0 kWh/stop | 541 kW average charger across stops |
| Stops to refill one trainset pack | 80 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 336 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 434 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (367.0 km @ €3.5 M/km) | €1.28 bn |
| Elevated (31.4 km @ €18 M/km) | €565 M |
| Elevated-interchange premium (19 sites @ €20 M) | €380 M |
| **Civil subtotal** | **€2.23 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 6 | €0.4 M | €2.4 M |
| `standard` | 95 | €1.5 M | €142 M |
| `major` | 13 | €3.0 M | €39 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 42 | €4.5 M | €189 M |
| **Stations subtotal** | | | **€413 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 325 | €6.0 M | €1.95 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 401.3 km × €0.015 M/km | €6.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €62 M |
| EPC integration + project management (7%) | on subtotal | €331 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.23 bn |
| Stations | €413 M |
| Depots | €70 M |
| Rolling stock | €1.95 bn |
| Residual train-control wayside + charging microgrids | €68 M |
| EPC overhead (7%) | €331 M |
| **CAPEX total** | **€5.06 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,298 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh durban`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€421 M / yr** | €108 |
| Steady-state, low-ridership (year 6+) | **€485 M / yr** | €124 |
| Steady-state, high-ridership (year 6+) | **€433 M / yr** | €111 |
| Lifecycle envelope (yr 1–25, low scenario) | **€11.81 bn cumulative** | €3,029 |
| Lifecycle envelope (yr 1–25, high scenario) | **€10.77 bn cumulative** | €2,761 |

_Population basis: 3,900,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€98 M / yr (low) → €46 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €3.04 bn | 4.5% | 25 y, 5 y grace | €233 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.27 bn | 10.5% | 25 y, 5 y grace | €154 M / yr |
| Government equity (no debt service) | 15% | €759 M | — | — | — |
| **Total** | **100%** | **€5.06 bn** | | | **€387 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €137 M / yr + bonds €133 M / yr = **€270 M / yr** total — plus the equity tranche amortised across construction (€152 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €78 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €54 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €299 k |
| Traction energy (1367.1 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,420 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €18 M |
| **OPEX subtotal** | | **€151 M / yr** |

_Annual fleet utilisation: 290 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 57.0 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$480 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.74 (~$0.80 USD) |
| Day pass (3 trips) | €1.88 (15 % bulk discount) |
| Monthly unlimited pass | €22.08 (~5 % of median monthly income) |
| Annual pass | €242.88 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 71.2 M | 142.3 M |
| Farebox revenue | €52 M / yr | €105 M / yr |
| Farebox / OPEX recovery | 35% | 70% |
| Country policy-target recovery (diagnostic) | 55% | 55% |
| Operating shortfall (gov subsidy required) | €98 M / yr | €46 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€485 M / yr** | **€433 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`durban.toml`](durban.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`durban-network-map.png`](durban-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`durban.corridor.geojson`](durban.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`durban.stations.json`](durban.stations.json) | Machine-readable station list |
| [`durban.design-quality.yaml`](durban.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug durban

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug durban \
    --sidecar .cache/osr-pipeline/rasters/durban.grid.json \
    --out-dir designs/.../Durban

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../durban.toml \
    --out designs/.../README.md
```

`scripts/regenerate-durban.sh` chains steps 3 + drift tests into a single command.
