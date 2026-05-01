# Amman — Urban Rail Network

**Country:** JO · **Population:** 4,007,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Amman rail network on OpenStreetMap](amman-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`amman.corridor.geojson`](amman.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 171 |
| Interchange stations | 29 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 50.9% |
| Route length (double track) | 354.0 km |
| Revenue fleet | 256 × 6-car trainsets |
| Spare + cold-reserve | 30 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 52.5 km | 24 | 42 | NE Outer ↔ SW Outer |
| line-2 | 40.1 km | 16 | 32 | S Mid ↔ NE Outer |
| line-3 | 41.6 km | 19 | 34 | NW Outer ↔ S Mid |
| line-4 | 33.0 km | 18 | 27 | N Mid ↔ SE Mid |
| line-5 | 36.6 km | 20 | 30 | SE Mid ↔ W Outer |
| line-6 | 31.5 km | 17 | 26 | E Mid ↔ NW Outer |
| line-7 | 29.4 km | 16 | 25 | W Outer ↔ NE Mid |
| line-8 | 89.2 km | 42 | 70 | W Mid ↔ W Mid |
| **Total** | **354.0 km** | **171 unique** | **286** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Nominal capacity | 900 pax (seated + standing, `metro-6car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 900 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 900 × 12 = **10,800 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 10,800 = **172,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,728,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **203,956 – 305,934 trips/day**

## Catchment

- City population: **4,007,000**
- Anchor-weighted coverage: 50.9%
- Catchment population: **≈ 2,039,563** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 29 | 500 kW | 3000 kWh |
| Major | 62 | 400 kW | 2500 kWh |
| Standard | 64 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **169** | **70,000 kW** | **449,000 kWh** |

Aggregate station-rail charging power: **92,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (323.9 km @ €3.5 M/km) | €1.13 bn |
| Elevated (29.2 km @ €18 M/km) | €525 M |
| Elevated-interchange premium (14 sites @ €20 M) | €280 M |
| **Civil subtotal** | **€1.94 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 64 | €1.5 M | €96 M |
| `major` | 62 | €3.0 M | €186 M |
| `terminal` | 13 | €2.5 M | €32 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| `interchange-elevated` | 27 | €4.5 M | €122 M |
| **Stations subtotal** | | | **€449 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 13 | €3.0 M | €39 M |
| **Depots subtotal** | | | **€64 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 286 | €6.0 M | €1.72 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 354.0 km × €0.015 M/km | €5.3 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 354.0 km × €0.8 M/km | €282 M |
| EPC integration + project management (7%) | on subtotal | €312 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.94 bn |
| Stations | €449 M |
| Depots | €64 M |
| Rolling stock | €1.72 bn |
| Residual train-control wayside + power | €288 M |
| EPC overhead (7%) | €312 M |
| **CAPEX total** | **€4.77 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,190 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh amman`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€347 M / yr** | €87 |
| Steady-state, low-ridership (year 6+) | **€399 M / yr** | €100 |
| Steady-state, high-ridership (year 6+) | **€334 M / yr** | €83 |
| Lifecycle envelope (yr 1–25, low scenario) | **€9.72 bn cumulative** | €2,427 |
| Lifecycle envelope (yr 1–25, high scenario) | **€8.42 bn cumulative** | €2,102 |

_Population basis: 4,007,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€72 M / yr (low) → €7.0 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.86 bn | 4.0% | 25 y, 5 y grace | €210 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.19 bn | 7.5% | 25 y, 5 y grace | €117 M / yr |
| Government equity (no debt service) | 15% | €715 M | — | — | — |
| **Total** | **100%** | **€4.77 bn** | | | **€327 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €114 M / yr + bonds €89 M / yr = **€204 M / yr** total — plus the equity tranche amortised across construction (€143 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €69 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €49 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €265 k |
| Traction energy (1206.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,136 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €19 M |
| **OPEX subtotal** | | **€137 M / yr** |

_Annual fleet utilisation: 256 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 50.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$580 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.89 (~$0.97 USD) |
| Day pass (3 trips) | €2.27 (15 % bulk discount) |
| Monthly unlimited pass | €26.68 (~5 % of median monthly income) |
| Annual pass | €293.48 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 73.1 M | 146.3 M |
| Farebox revenue | €65 M / yr | €130 M / yr |
| Farebox / OPEX recovery | 47% | 95% |
| Country policy-target recovery (diagnostic) | 55% | 55% |
| Operating shortfall (gov subsidy required) | €72 M / yr | €7.0 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€399 M / yr** | **€334 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`amman.toml`](amman.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`amman-network-map.png`](amman-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`amman.corridor.geojson`](amman.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`amman.stations.json`](amman.stations.json) | Machine-readable station list |
| [`amman.design-quality.yaml`](amman.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug amman

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug amman \
    --sidecar .cache/osr-pipeline/rasters/amman.grid.json \
    --out-dir designs/.../Amman

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../amman.toml \
    --out designs/.../README.md
```

`scripts/regenerate-amman.sh` chains steps 3 + drift tests into a single command.
