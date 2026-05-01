# Kabul — Urban Rail Network

**Country:** AF · **Population:** 4,601,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kabul rail network on OpenStreetMap](kabul-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kabul.corridor.geojson`](kabul.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 7 |
| Unique stations | 136 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 52.7% |
| Route length (double track) | 260.9 km |
| Revenue fleet | 191 × 6-car trainsets |
| Spare + cold-reserve | 24 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 42.4 km | 24 | 35 | W Mid ↔ E Outer |
| line-2 | 37.1 km | 18 | 30 | NW Mid ↔ E Outer |
| line-3 | 26.3 km | 13 | 23 | SW Outer ↔ SE Mid |
| line-4 | 28.0 km | 16 | 24 | SE Mid ↔ NW Outer |
| line-5 | 28.7 km | 17 | 24 | SW Mid ↔ NE Mid |
| line-6 | 24.9 km | 14 | 21 | E Outer ↔ W Inner |
| line-7 | 73.6 km | 35 | 58 | NW Mid ↔ NW Mid |
| **Total** | **260.9 km** | **136 unique** | **215** | |

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
- **Network peak throughput (all lines, both directions):** 7 lines × 2 directions × 7,920 = **110,880 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,108,800 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **242,472 – 363,709 trips/day**

## Catchment

- City population: **4,601,000**
- Anchor-weighted coverage: 52.7%
- Catchment population: **≈ 2,424,727** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 60 | 400 kW | 2500 kWh |
| Standard | 38 | 300 kW | 2000 kWh |
| Terminal | 11 | 500 kW | 3000 kWh |
| **Total installed** | **134** | **57,900 kW** | **371,000 kWh** |

Aggregate station-rail charging power: **73,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 895 kWh | 37.3 km average line length |
| Onboard battery coverage | 0.8× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.0 kWh/stop | 542 kW average charger across stops |
| Stops to refill one trainset pack | 80 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 290 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 371 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (233.0 km @ €3.5 M/km) | €816 M |
| Elevated (23.3 km @ €18 M/km) | €420 M |
| Elevated-interchange premium (15 sites @ €20 M) | €300 M |
| **Civil subtotal** | **€1.54 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 38 | €1.5 M | €57 M |
| `major` | 60 | €3.0 M | €180 M |
| `terminal` | 11 | €2.5 M | €28 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| `interchange-elevated` | 22 | €4.5 M | €99 M |
| **Stations subtotal** | | | **€377 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 11 | €3.0 M | €33 M |
| **Depots subtotal** | | | **€58 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 215 | €6.0 M | €1.29 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 260.9 km × €0.015 M/km | €3.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €53 M |
| EPC integration + project management (7%) | on subtotal | €232 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.54 bn |
| Stations | €377 M |
| Depots | €58 M |
| Rolling stock | €1.29 bn |
| Residual train-control wayside + charging microgrids | €57 M |
| EPC overhead (7%) | €232 M |
| **CAPEX total** | **€3.55 bn** |
| Per-route-km | €14 M / km |
| Per-capita (city pop) | €772 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kabul`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€309 M / yr** | €67 |
| Steady-state, low-ridership (year 11+) | **€389 M / yr** | €85 |
| Steady-state, high-ridership (year 11+) | **€380 M / yr** | €83 |
| Lifecycle envelope (yr 1–35, low scenario) | **€12.82 bn cumulative** | €2,787 |
| Lifecycle envelope (yr 1–35, high scenario) | **€12.58 bn cumulative** | €2,734 |

_Population basis: 4,601,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero and only the OPEX shortfall remains — ~€83 M / yr (low) → €74 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.13 bn | 4.5% | 35 y, 10 y grace | €144 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €888 M | 18.0% | 35 y, 10 y grace | €162 M / yr |
| Government equity (no debt service) | 15% | €533 M | — | — | — |
| **Total** | **100%** | **€3.55 bn** | | | **€306 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €96 M / yr + bonds €160 M / yr = **€256 M / yr** total — plus the equity tranche amortised across construction (€53 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €52 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €39 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €192 k |
| Traction energy (900.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,577 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.8 M |
| **OPEX subtotal** | | **€93 M / yr** |

_Annual fleet utilisation: 191 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 37.5 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$75 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.12 (~$0.12 USD) |
| Day pass (3 trips) | €0.29 (15 % bulk discount) |
| Monthly unlimited pass | €3.45 (~5 % of median monthly income) |
| Annual pass | €37.95 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 84.0 M | 167.9 M |
| Farebox revenue | €9.7 M / yr | €19 M / yr |
| Farebox / OPEX recovery | 10% | 21% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €83 M / yr | €74 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€389 M / yr** | **€380 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kabul.toml`](kabul.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kabul-network-map.png`](kabul-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kabul.corridor.geojson`](kabul.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kabul.stations.json`](kabul.stations.json) | Machine-readable station list |
| [`kabul.design-quality.yaml`](kabul.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kabul

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kabul \
    --sidecar .cache/osr-pipeline/rasters/kabul.grid.json \
    --out-dir designs/.../Kabul

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kabul.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kabul.sh` chains steps 3 + drift tests into a single command.
