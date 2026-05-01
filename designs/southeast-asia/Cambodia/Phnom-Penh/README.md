# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 106 |
| Interchange stations | 23 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 48.3% |
| Route length (double track) | 227.7 km |
| Revenue fleet | 166 × 4-car trainsets |
| Spare + cold-reserve | 20 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 38.6 km | 18 | 31 | SE Outer ↔ N Outer |
| line-2 | 31.4 km | 16 | 26 | E Outer ↔ W Mid |
| line-3 | 28.1 km | 11 | 24 | N Mid ↔ SW Mid |
| line-4 | 25.9 km | 15 | 21 | SW Mid ↔ NE Mid |
| line-5 | 41.2 km | 18 | 34 | NW Outer ↔ SE Outer |
| line-6 | 62.4 km | 29 | 50 | W Mid ↔ W Mid |
| **Total** | **227.7 km** | **106 unique** | **186** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **110,172 – 165,258 trips/day**

## Catchment

- City population: **2,281,000**
- Anchor-weighted coverage: 48.3%
- Catchment population: **≈ 1,101,723** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 23 | 500 kW | 3000 kWh |
| Major | 25 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **104** | **44,800 kW** | **290,500 kWh** |

Aggregate station-rail charging power: **57,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (186.2 km @ €3.5 M/km) | €652 M |
| Elevated (40.2 km @ €18 M/km) | €724 M |
| Elevated-interchange premium (8 sites @ €20 M) | €160 M |
| **Civil subtotal** | **€1.54 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 46 | €1.5 M | €69 M |
| `major` | 25 | €3.0 M | €75 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 10 | €4.5 M | €45 M |
| `interchange-elevated` | 13 | €4.5 M | €58 M |
| **Stations subtotal** | | | **€274 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 186 | €4.0 M | €744 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 227.7 km × €0.015 M/km | €3.4 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 227.7 km × €0.8 M/km | €181 M |
| EPC integration + project management (7%) | on subtotal | €195 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.54 bn |
| Stations | €274 M |
| Depots | €52 M |
| Rolling stock | €744 M |
| Residual train-control wayside + power | €185 M |
| EPC overhead (7%) | €195 M |
| **CAPEX total** | **€2.99 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,309 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh phnom-penh`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€195 M / yr** | €86 |
| Steady-state, low-ridership (year 8+) | **€251 M / yr** | €110 |
| Steady-state, high-ridership (year 8+) | **€237 M / yr** | €104 |
| Lifecycle envelope (yr 1–30, low scenario) | **€7.13 bn cumulative** | €3,126 |
| Lifecycle envelope (yr 1–30, high scenario) | **€6.82 bn cumulative** | €2,988 |

_Population basis: 2,281,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€58 M / yr (low) → €44 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.79 bn | 4.0% | 30 y, 7 y grace | €121 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €746 M | 8.0% | 30 y, 7 y grace | €72 M / yr |
| Government equity (no debt service) | 15% | €448 M | — | — | — |
| **Total** | **100%** | **€2.99 bn** | | | **€193 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €72 M / yr + bonds €60 M / yr = **€131 M / yr** total — plus the equity tranche amortised across construction (€64 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €30 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €37 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €170 k |
| Traction energy (521.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,378 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €4.6 M |
| **OPEX subtotal** | | **€72 M / yr** |

_Annual fleet utilisation: 166 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 32.6 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$215 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.33 (~$0.36 USD) |
| Day pass (3 trips) | €0.84 (15 % bulk discount) |
| Monthly unlimited pass | €9.89 (~5 % of median monthly income) |
| Annual pass | €108.79 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 41.6 M | 83.3 M |
| Farebox revenue | €14 M / yr | €27 M / yr |
| Farebox / OPEX recovery | 19% | 38% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €58 M / yr | €44 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€251 M / yr** | **€237 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`phnom-penh-network-map.png`](phnom-penh-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`phnom-penh.stations.json`](phnom-penh.stations.json) | Machine-readable station list |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug phnom-penh

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug phnom-penh \
    --sidecar .cache/osr-pipeline/rasters/phnom-penh.grid.json \
    --out-dir designs/.../Phnom-Penh

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../phnom-penh.toml \
    --out designs/.../README.md
```

`scripts/regenerate-phnom-penh.sh` chains steps 3 + drift tests into a single command.
