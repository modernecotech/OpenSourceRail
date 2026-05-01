# Bandung — Urban Rail Network

**Country:** ID · **Population:** 2,615,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Bandung rail network on OpenStreetMap](bandung-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`bandung.corridor.geojson`](bandung.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 125 |
| Interchange stations | 22 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 40.7% |
| Route length (double track) | 257.5 km |
| Revenue fleet | 186 × 4-car trainsets |
| Spare + cold-reserve | 22 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 43.4 km | 22 | 35 | W Outer ↔ E Outer |
| line-2 | 37.2 km | 19 | 30 | N Outer ↔ S Mid |
| line-3 | 39.1 km | 21 | 32 | SE Outer ↔ NW Outer |
| line-4 | 30.2 km | 17 | 25 | SW Outer ↔ E Mid |
| line-5 | 28.5 km | 13 | 24 | W Mid ↔ NE Outer |
| line-6 | 79.1 km | 34 | 62 | NW Mid ↔ NW Mid |
| **Total** | **257.5 km** | **125 unique** | **208** | |

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
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 6,480 = **77,760 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **777,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **106,430 – 159,645 trips/day**

## Catchment

- City population: **2,615,000**
- Anchor-weighted coverage: 40.7%
- Catchment population: **≈ 1,064,305** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 22 | 500 kW | 3000 kWh |
| Major | 49 | 400 kW | 2500 kWh |
| Standard | 44 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **125** | **53,300 kW** | **343,500 kWh** |

Aggregate station-rail charging power: **67,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 687 kWh | 42.9 km average line length |
| Onboard battery coverage | 0.7× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.0 kWh/stop | 542 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 266 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 344 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (219.7 km @ €3.5 M/km) | €769 M |
| Elevated (31.8 km @ €18 M/km) | €572 M |
| Elevated-interchange premium (12 sites @ €20 M) | €240 M |
| **Civil subtotal** | **€1.58 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | €0.4 M | €0.4 M |
| `standard` | 44 | €1.5 M | €66 M |
| `major` | 49 | €3.0 M | €147 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 4 | €4.5 M | €18 M |
| `interchange-elevated` | 18 | €4.5 M | €81 M |
| **Stations subtotal** | | | **€338 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 208 | €4.0 M | €832 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 257.5 km × €0.015 M/km | €3.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €48 M |
| EPC integration + project management (7%) | on subtotal | €200 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.58 bn |
| Stations | €338 M |
| Depots | €52 M |
| Rolling stock | €832 M |
| Residual train-control wayside + charging microgrids | €52 M |
| EPC overhead (7%) | €200 M |
| **CAPEX total** | **€3.05 bn** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €1,168 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh bandung`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€216 M / yr** | €83 |
| Steady-state, low-ridership (year 6+) | **€262 M / yr** | €100 |
| Steady-state, high-ridership (year 6+) | **€239 M / yr** | €91 |
| Lifecycle envelope (yr 1–25, low scenario) | **€6.33 bn cumulative** | €2,420 |
| Lifecycle envelope (yr 1–25, high scenario) | **€5.86 bn cumulative** | €2,241 |

_Population basis: 2,615,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€57 M / yr (low) → €34 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.83 bn | 4.0% | 25 y, 5 y grace | €135 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €764 M | 6.7% | 25 y, 5 y grace | €70 M / yr |
| Government equity (no debt service) | 15% | €458 M | — | — | — |
| **Total** | **100%** | **€3.05 bn** | | | **€205 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €73 M / yr + bonds €51 M / yr = **€124 M / yr** total — plus the equity tranche amortised across construction (€92 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €33 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €39 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €189 k |
| Traction energy (584.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,557 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €7.7 M |
| **OPEX subtotal** | | **€81 M / yr** |

_Annual fleet utilisation: 186 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 36.5 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$320 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.49 (~$0.53 USD) |
| Day pass (3 trips) | €1.25 (15 % bulk discount) |
| Monthly unlimited pass | €14.72 (~5 % of median monthly income) |
| Annual pass | €161.92 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 47.7 M | 95.4 M |
| Farebox revenue | €23 M / yr | €47 M / yr |
| Farebox / OPEX recovery | 29% | 58% |
| Country policy-target recovery (diagnostic) | 60% | 60% |
| Operating shortfall (gov subsidy required) | €57 M / yr | €34 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€262 M / yr** | **€239 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`bandung.toml`](bandung.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`bandung-network-map.png`](bandung-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`bandung.corridor.geojson`](bandung.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`bandung.stations.json`](bandung.stations.json) | Machine-readable station list |
| [`bandung.design-quality.yaml`](bandung.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug bandung

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug bandung \
    --sidecar .cache/osr-pipeline/rasters/bandung.grid.json \
    --out-dir designs/.../Bandung

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../bandung.toml \
    --out designs/.../README.md
```

`scripts/regenerate-bandung.sh` chains steps 3 + drift tests into a single command.
