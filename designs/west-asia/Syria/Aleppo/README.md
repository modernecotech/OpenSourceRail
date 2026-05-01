# Aleppo — Urban Rail Network

**Country:** SY · **Population:** 1,639,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Aleppo rail network on OpenStreetMap](aleppo-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`aleppo.corridor.geojson`](aleppo.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 88 |
| Interchange stations | 16 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 46.2% |
| Route length (double track) | 175.7 km |
| Revenue fleet | 129 × 4-car trainsets |
| Spare + cold-reserve | 16 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 29.8 km | 16 | 25 | W Outer ↔ E Outer |
| line-2 | 32.4 km | 17 | 27 | SE Outer ↔ NW Outer |
| line-3 | 35.4 km | 17 | 29 | NE Outer ↔ SW Outer |
| line-4 | 20.7 km | 13 | 18 | W Outer ↔ E Mid |
| line-5 | 57.4 km | 26 | 46 | NW Mid ↔ NW Mid |
| **Total** | **175.7 km** | **88 unique** | **145** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **75,721 – 113,582 trips/day**

## Catchment

- City population: **1,639,000**
- Anchor-weighted coverage: 46.2%
- Catchment population: **≈ 757,218** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 16 | 500 kW | 3000 kWh |
| Major | 30 | 400 kW | 2500 kWh |
| Standard | 32 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **86** | **38,100 kW** | **248,000 kWh** |

Aggregate station-rail charging power: **47,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (168.1 km @ €3.5 M/km) | €588 M |
| Elevated (6.9 km @ €18 M/km) | €124 M |
| Elevated-interchange premium (6 sites @ €20 M) | €120 M |
| **Civil subtotal** | **€833 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 32 | €1.5 M | €48 M |
| `major` | 30 | €3.0 M | €90 M |
| `terminal` | 7 | €2.5 M | €18 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| `interchange-elevated` | 14 | €4.5 M | €63 M |
| **Stations subtotal** | | | **€232 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 145 | €4.0 M | €580 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 175.7 km × €0.015 M/km | €2.6 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 175.7 km × €0.8 M/km | €140 M |
| EPC integration + project management (7%) | on subtotal | €128 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €833 M |
| Stations | €232 M |
| Depots | €46 M |
| Rolling stock | €580 M |
| Residual train-control wayside + power | €143 M |
| EPC overhead (7%) | €128 M |
| **CAPEX total** | **€1.96 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €1,197 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh aleppo`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€180 M / yr** | €110 |
| Steady-state, low-ridership (year 11+) | **€222 M / yr** | €135 |
| Steady-state, high-ridership (year 11+) | **€219 M / yr** | €133 |
| Lifecycle envelope (yr 1–35, low scenario) | **€7.35 bn cumulative** | €4,487 |
| Lifecycle envelope (yr 1–35, high scenario) | **€7.27 bn cumulative** | €4,438 |

_Population basis: 1,639,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero and only the OPEX shortfall remains — ~€43 M / yr (low) → €40 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.18 bn | 4.5% | 35 y, 10 y grace | €79 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €490 M | 20.0% | 35 y, 10 y grace | €99 M / yr |
| Government equity (no debt service) | 15% | €294 M | — | — | — |
| **Total** | **100%** | **€1.96 bn** | | | **€178 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €53 M / yr + bonds €98 M / yr = **€151 M / yr** total — plus the equity tranche amortised across construction (€29 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €23 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €22 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €131 k |
| Traction energy (405.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,066 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.2 M |
| **OPEX subtotal** | | **€47 M / yr** |

_Annual fleet utilisation: 129 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 25.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$70 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.11 (~$0.12 USD) |
| Day pass (3 trips) | €0.27 (15 % bulk discount) |
| Monthly unlimited pass | €3.22 (~5 % of median monthly income) |
| Annual pass | €35.42 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 29.9 M | 59.8 M |
| Farebox revenue | €3.2 M / yr | €6.4 M / yr |
| Farebox / OPEX recovery | 7% | 14% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €43 M / yr | €40 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€222 M / yr** | **€219 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`aleppo.toml`](aleppo.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`aleppo-network-map.png`](aleppo-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`aleppo.corridor.geojson`](aleppo.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`aleppo.stations.json`](aleppo.stations.json) | Machine-readable station list |
| [`aleppo.design-quality.yaml`](aleppo.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug aleppo

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug aleppo \
    --sidecar .cache/osr-pipeline/rasters/aleppo.grid.json \
    --out-dir designs/.../Aleppo

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../aleppo.toml \
    --out designs/.../README.md
```

`scripts/regenerate-aleppo.sh` chains steps 3 + drift tests into a single command.
