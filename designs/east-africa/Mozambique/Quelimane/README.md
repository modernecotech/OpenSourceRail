# Quelimane — Urban Rail Network

**Country:** MZ · **Population:** 350,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Quelimane rail network on OpenStreetMap](quelimane-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`quelimane.corridor.geojson`](quelimane.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 1 |
| Unique stations | 6 |
| Interchange stations | 0 |
| Multi-line transfer reachability | 100% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 47.6% |
| Route length (double track) | 10.3 km |
| Revenue fleet | 10 × 3-car trainsets |
| Spare + cold-reserve | 2 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 10.3 km | 6 | 12 | W Outer ↔ NE Outer |
| **Total** | **10.3 km** | **6 unique** | **12** | |

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
- **Network peak throughput (all lines, both directions):** 1 lines × 2 directions × 3,960 = **7,920 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **79,200 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **16,660 – 24,990 trips/day**

## Catchment

- City population: **350,000**
- Anchor-weighted coverage: 47.6%
- Catchment population: **≈ 166,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Major | 2 | 400 kW | 2500 kWh |
| Standard | 2 | 300 kW | 2000 kWh |
| Terminal | 1 | 500 kW | 3000 kWh |
| **Total installed** | **6** | **6,900 kW** | **52,000 kWh** |

Aggregate station-rail charging power: **4,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 124 kWh | 10.3 km average line length |
| Onboard battery coverage | 2.9× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 11.1 kWh/stop | 667 kW average charger across stops |
| Stops to refill one trainset pack | 32 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 34 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 52 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (10.1 km @ €3.5 M/km) | €35 M |
| **Civil subtotal** | **€35 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 2 | €1.5 M | €3.0 M |
| `major` | 2 | €3.0 M | €6.0 M |
| `terminal` | 1 | €2.5 M | €2.5 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| **Stations subtotal** | | | **€14 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 1 | €3.0 M | €3.0 M |
| **Depots subtotal** | | | **€28 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 12 | €3.0 M | €36 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 10.3 km × €0.015 M/km | €0.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €2.5 M |
| EPC integration + project management (7%) | on subtotal | €8.1 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €35 M |
| Stations | €14 M |
| Depots | €28 M |
| Rolling stock | €36 M |
| Residual train-control wayside + charging microgrids | €2.6 M |
| EPC overhead (7%) | €8.1 M |
| **CAPEX total** | **€125 M** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €356 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh quelimane`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€8.3 M / yr** | €24 |
| Steady-state, low-ridership (year 11+) | **€11 M / yr** | €30 |
| Steady-state, high-ridership (year 11+) | **€9.3 M / yr** | €27 |
| Lifecycle envelope (yr 1–35, low scenario) | **€347 M cumulative** | €992 |
| Lifecycle envelope (yr 1–35, high scenario) | **€315 M cumulative** | €901 |

_Population basis: 350,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero and only the OPEX shortfall remains — ~€1.9 M / yr (low) → €606 k / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €75 M | 3.0% | 35 y, 10 y grace | €4.3 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €31 M | 13.5% | 35 y, 10 y grace | €4.4 M / yr |
| Government equity (no debt service) | 15% | €19 M | — | — | — |
| **Total** | **100%** | **€125 M** | | | **€8.7 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €2.2 M / yr + bonds €4.2 M / yr = **€6.4 M / yr** total — plus the equity tranche amortised across construction (€1.9 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €1.4 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €1.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €8 k |
| Traction energy (20.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (74 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €149 k |
| **OPEX subtotal** | | **€3.2 M / yr** |

_Annual fleet utilisation: 10 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 1.7 M train-km / yr (~168 k km / trainset / yr)._

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
| Annual paid trips | 6.4 M | 12.8 M |
| Farebox revenue | €1.3 M / yr | €2.5 M / yr |
| Farebox / OPEX recovery | 40% | 81% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €1.9 M / yr | €606 k / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€11 M / yr** | **€9.3 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`quelimane.toml`](quelimane.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`quelimane-network-map.png`](quelimane-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`quelimane.corridor.geojson`](quelimane.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`quelimane.stations.json`](quelimane.stations.json) | Machine-readable station list |
| [`quelimane.design-quality.yaml`](quelimane.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug quelimane

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug quelimane \
    --sidecar .cache/osr-pipeline/rasters/quelimane.grid.json \
    --out-dir designs/.../Quelimane

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../quelimane.toml \
    --out designs/.../README.md
```

`scripts/regenerate-quelimane.sh` chains steps 3 + drift tests into a single command.
