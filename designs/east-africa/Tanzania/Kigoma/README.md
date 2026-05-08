# Kigoma — Urban Rail Network

**Country:** TZ · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kigoma rail network on OpenStreetMap](kigoma-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kigoma.corridor.geojson`](kigoma.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 24 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 77.0% |
| Route length (double track) | 35.0 km |
| Revenue fleet | 43 × 2-car trainsets |
| Spare + cold-reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 12.5 km | 9 | 17 | E Outer ↔ SW Outer |
| line-2 | 13.6 km | 9 | 19 | N Outer ↔ SE Outer |
| line-3 |  8.8 km | 6 | 13 | S Mid ↔ N Mid |
| **Total** | **35.0 km** | **24 unique** | **49** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **23,100 – 34,650 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 77.0%
- Catchment population: **≈ 231,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 9 | 400 kW | 2500 kWh |
| Standard | 6 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **24** | **14,400 kW** | **98,500 kWh** |

Aggregate station-rail charging power: **15,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 93 kWh | 11.7 km average line length |
| Onboard battery coverage | 2.6× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.4 kWh/stop | 625 kW average charger across stops |
| Stops to refill one trainset pack | 23 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 72 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 98 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **€1.0 M per self-contained car** rolling stock, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (34.8 km @ €3.5 M/km) | €122 M |
| **Civil subtotal** | **€122 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 6 | €1.5 M | €9.0 M |
| `major` | 9 | €3.0 M | €27 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 3 | €4.5 M | €14 M |
| **Stations subtotal** | | | **€65 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 49 | €2.0 M | €98 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 35.0 km × €0.015 M/km | €0.5 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | €9.7 M |
| EPC integration + project management (7%) | on subtotal | €23 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €122 M |
| Stations | €65 M |
| Depots | €40 M |
| Rolling stock | €98 M |
| Residual train-control wayside + charging microgrids | €10 M |
| EPC overhead (7%) | €23 M |
| **CAPEX total** | **€358 M** |
| Per-route-km | €10 M / km |
| Per-capita (city pop) | €1,195 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kigoma`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **€24 M / yr** | €81 |
| Steady-state, low-ridership (year 8+) | **€32 M / yr** | €105 |
| Steady-state, high-ridership (year 8+) | **€30 M / yr** | €101 |
| Lifecycle envelope (yr 1–30, low scenario) | **€897 M cumulative** | €2,989 |
| Lifecycle envelope (yr 1–30, high scenario) | **€865 M cumulative** | €2,883 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero and only the OPEX shortfall remains — ~€7.7 M / yr (low) → €6.3 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €215 M | 3.8% | 30 y, 7 y grace | €14 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €90 M | 9.5% | 30 y, 7 y grace | €9.7 M / yr |
| Government equity (no debt service) | 15% | €54 M | — | — | — |
| **Total** | **100%** | **€358 M** | | | **€24 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral €8.2 M / yr + bonds €8.5 M / yr = **€17 M / yr** total — plus the equity tranche amortised across construction (€7.7 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €3.9 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €4.5 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | €26 k |
| Traction energy (42.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (222 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €566 k |
| **OPEX subtotal** | | **€9.0 M / yr** |

_Annual fleet utilisation: 43 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 5.3 M train-km / yr (~123 k km / trainset / yr)._

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
| Farebox / OPEX recovery | 15% | 31% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €7.7 M / yr | €6.3 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€32 M / yr** | **€30 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kigoma.toml`](kigoma.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kigoma-network-map.png`](kigoma-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kigoma.corridor.geojson`](kigoma.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kigoma.stations.json`](kigoma.stations.json) | Machine-readable station list |
| [`kigoma.design-quality.yaml`](kigoma.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kigoma

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kigoma \
    --sidecar .cache/osr-pipeline/rasters/kigoma.grid.json \
    --out-dir designs/.../Kigoma

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kigoma.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kigoma.sh` chains steps 3 + drift tests into a single command.
