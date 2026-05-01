# Kathmandu — Urban Rail Network

**Country:** NP · **Population:** 1,442,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kathmandu rail network on OpenStreetMap](kathmandu-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kathmandu.corridor.geojson`](kathmandu.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 102 |
| Interchange stations | 27 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 45.5% |
| Route length (double track) | 202.6 km |
| Revenue fleet | 148 × 4-car trainsets |
| Spare + cold-reserve | 19 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 32.9 km | 18 | 27 | W Outer ↔ E Outer |
| line-2 | 30.3 km | 16 | 25 | NE Mid ↔ SW Outer |
| line-3 | 24.3 km | 13 | 20 | S Mid ↔ NE Outer |
| line-4 | 27.8 km | 17 | 24 | SE Mid ↔ NW Mid |
| line-5 | 28.3 km | 11 | 24 | S Mid ↔ NW Outer |
| line-6 | 59.1 km | 28 | 47 | W Mid ↔ W Mid |
| **Total** | **202.6 km** | **102 unique** | **167** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **65,611 – 98,416 trips/day**

## Catchment

- City population: **1,442,000**
- Anchor-weighted coverage: 45.5%
- Catchment population: **≈ 656,110** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 27 | 500 kW | 3000 kWh |
| Major | 34 | 400 kW | 2500 kWh |
| Standard | 30 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **101** | **45,600 kW** | **293,000 kWh** |

Aggregate station-rail charging power: **56,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (168.6 km @ €3.5 M/km) | €590 M |
| Elevated (29.0 km @ €18 M/km) | €521 M |
| Elevated-interchange premium (13 sites @ €20 M) | €260 M |
| **Civil subtotal** | **€1.37 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | €0.4 M | €0.8 M |
| `standard` | 30 | €1.5 M | €45 M |
| `major` | 34 | €3.0 M | €102 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 27 | €4.5 M | €122 M |
| **Stations subtotal** | | | **€295 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 167 | €4.0 M | €668 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 202.6 km × €0.015 M/km | €3.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no route traction power) | per-stop allowance by station archetype | €42 M |
| EPC integration + project management (7%) | on subtotal | €170 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.37 bn |
| Stations | €295 M |
| Depots | €52 M |
| Rolling stock | €668 M |
| Residual train-control wayside + charging microgrids | €45 M |
| EPC overhead (7%) | €170 M |
| **CAPEX total** | **€2.60 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,804 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kathmandu`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€151 M / yr** | €105 |
| Steady-state, low-ridership (year 8+) | **€213 M / yr** | €148 |
| Steady-state, high-ridership (year 8+) | **€208 M / yr** | €144 |
| Lifecycle envelope (yr 1–30, low scenario) | **€5.97 bn cumulative** | €4,137 |
| Lifecycle envelope (yr 1–30, high scenario) | **€5.84 bn cumulative** | €4,047 |

_Population basis: 1,442,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€58 M / yr (low) → €53 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.56 bn | 3.0% | 30 y, 7 y grace | €95 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €650 M | 7.5% | 30 y, 7 y grace | €60 M / yr |
| Government equity (no debt service) | 15% | €390 M | — | — | — |
| **Total** | **100%** | **€2.60 bn** | | | **€155 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €47 M / yr + bonds €49 M / yr = **€96 M / yr** total — plus the equity tranche amortised across construction (€56 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €27 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €34 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €148 k |
| Traction energy (465.1 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,228 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €2.7 M |
| **OPEX subtotal** | | **€64 M / yr** |

_Annual fleet utilisation: 148 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 29.1 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$140 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.21 (~$0.23 USD) |
| Day pass (3 trips) | €0.55 (15 % bulk discount) |
| Monthly unlimited pass | €6.44 (~5 % of median monthly income) |
| Annual pass | €70.84 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 26.3 M | 52.6 M |
| Farebox revenue | €5.6 M / yr | €11 M / yr |
| Farebox / OPEX recovery | 9% | 18% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €58 M / yr | €53 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€213 M / yr** | **€208 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kathmandu.toml`](kathmandu.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kathmandu-network-map.png`](kathmandu-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kathmandu.corridor.geojson`](kathmandu.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kathmandu.stations.json`](kathmandu.stations.json) | Machine-readable station list |
| [`kathmandu.design-quality.yaml`](kathmandu.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kathmandu

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kathmandu \
    --sidecar .cache/osr-pipeline/rasters/kathmandu.grid.json \
    --out-dir designs/.../Kathmandu

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kathmandu.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kathmandu.sh` chains steps 3 + drift tests into a single command.
