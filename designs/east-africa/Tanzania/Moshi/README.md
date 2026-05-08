# Moshi — Urban Rail Network

**Country:** TZ · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Moshi rail network on OpenStreetMap](moshi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`moshi.corridor.geojson`](moshi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 21 |
| Interchange stations | 5 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 76.3% |
| Route length (double track) | 35.7 km |
| Revenue fleet | 45 × 2-car trainsets |
| Spare + cold-reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 11.9 km | 7 | 17 | E Outer ↔ SW Mid |
| line-2 | 11.1 km | 8 | 16 | NW Mid ↔ S Mid |
| line-3 | 12.7 km | 6 | 18 | SW Mid ↔ N Outer |
| **Total** | **35.7 km** | **21 unique** | **51** | |

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
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 2,520 = **15,120 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **151,200 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **22,890 – 34,335 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 76.3%
- Catchment population: **≈ 228,900** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 5 | 500 kW | 3000 kWh |
| Major | 2 | 400 kW | 2500 kWh |
| Standard | 8 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **21** | **13,200 kW** | **91,000 kWh** |

Aggregate station-rail charging power: **13,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 95 kWh | 11.9 km average line length |
| Onboard battery coverage | 2.5× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.7 kWh/stop | 643 kW average charger across stops |
| Stops to refill one trainset pack | 22 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 66 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 91 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (28.9 km @ €3.5 M/km) | €101 M |
| Elevated (6.4 km @ €18 M/km) | €116 M |
| Elevated-interchange premium (2 sites @ €20 M) | €40 M |
| **Civil subtotal** | **€257 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 8 | €1.5 M | €12 M |
| `major` | 2 | €3.0 M | €6.0 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 5 | €4.5 M | €22 M |
| **Stations subtotal** | | | **€56 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 51 | €2.0 M | €102 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 35.7 km × €0.015 M/km | €0.5 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €8.6 M |
| EPC integration + project management (7%) | on subtotal | €32 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €257 M |
| Stations | €56 M |
| Depots | €40 M |
| Rolling stock | €102 M |
| Residual train-control wayside + charging microgrids | €9.1 M |
| EPC overhead (7%) | €32 M |
| **CAPEX total** | **€496 M** |
| Per-route-km | €14 M / km |
| Per-capita (city pop) | €1,655 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh moshi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€34 M / yr** | €112 |
| Steady-state, low-ridership (year 8+) | **€43 M / yr** | €145 |
| Steady-state, high-ridership (year 8+) | **€42 M / yr** | €140 |
| Lifecycle envelope (yr 1–30, low scenario) | **€1.24 bn cumulative** | €4,120 |
| Lifecycle envelope (yr 1–30, high scenario) | **€1.20 bn cumulative** | €4,014 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€10 M / yr (low) → €9.0 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €298 M | 3.8% | 30 y, 7 y grace | €20 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €124 M | 9.5% | 30 y, 7 y grace | €13 M / yr |
| Government equity (no debt service) | 15% | €74 M | — | — | — |
| **Total** | **100%** | **€496 M** | | | **€33 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €11 M / yr + bonds €12 M / yr = **€23 M / yr** total — plus the equity tranche amortised across construction (€11 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €4.1 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €7.1 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €27 k |
| Traction energy (44.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (226 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €576 k |
| **OPEX subtotal** | | **€12 M / yr** |

_Annual fleet utilisation: 45 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 5.6 M train-km / yr (~123 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.25 (~$0.28 USD) |
| Day pass (3 trips) | €0.65 (15 % bulk discount) |
| Monthly unlimited pass | €7.59 (~5 % of median monthly income) |
| Annual pass | €83.49 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 5.5 M | 10.9 M |
| Farebox revenue | €1.4 M / yr | €2.8 M / yr |
| Farebox / OPEX recovery | 12% | 24% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €10 M / yr | €9.0 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€43 M / yr** | **€42 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`moshi.toml`](moshi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`moshi-network-map.png`](moshi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`moshi.corridor.geojson`](moshi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`moshi.stations.json`](moshi.stations.json) | Machine-readable station list |
| [`moshi.design-quality.yaml`](moshi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug moshi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug moshi \
    --sidecar .cache/osr-pipeline/rasters/moshi.grid.json \
    --out-dir designs/.../Moshi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../moshi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-moshi.sh` chains steps 3 + drift tests into a single command.
