# Dar-Es-Salaam — Urban Rail Network

**Country:** TZ · **Population:** 7,404,689

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Dar-Es-Salaam rail network on OpenStreetMap](dar-es-salaam-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 7 |
| Unique stations | 162 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 27.5% |
| Route length (double track) | 393.1 km |
| Revenue fleet | 282 × 6-car trainsets |
| Spare + cold-reserve | 32 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 55.8 km | 24 | 45 | NW Outer ↔ SE Mid |
| line-2 | 53.8 km | 21 | 43 | SW Outer ↔ N Mid |
| line-3 | 59.9 km | 26 | 48 | NW Mid ↔ E Outer |
| line-4 | 38.4 km | 16 | 31 | W Mid ↔ SE Mid |
| line-5 | 50.7 km | 21 | 40 | NW Outer ↔ SE Mid |
| line-6 | 35.6 km | 14 | 29 | SW Mid ↔ N Mid |
| line-7 | 99.0 km | 41 | 78 | W Inner ↔ W Inner |
| **Total** | **393.1 km** | **162 unique** | **314** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 720 × 12 = **8,640 pphpd**
- **Network peak throughput (all lines, both directions):** 7 lines × 2 directions × 8,640 = **120,960 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,209,600 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **786,240 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **366,532 – 610,886 trips/day**

## Catchment

- City population: **7,404,689**
- Anchor-weighted coverage: 27.5%
- Catchment population: **≈ 2,036,289** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 21 | 400 kW | 2500 kWh |
| Standard | 101 | 300 kW | 2000 kWh |
| Terminal | 11 | 500 kW | 3000 kWh |
| **Total installed** | **158** | **61,200 kW** | **399,500 kWh** |

Aggregate station-rail charging power: **86,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,348 kWh | 56.2 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 532 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 306 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 400 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (358.1 km @ $3.0 M/km) | $1.07 bn |
| Elevated (31.9 km @ $12.0 M/km) | $383 M |
| Elevated-interchange premium (11 sites @ $4.50 M) | $50 M |
| **Civil subtotal** | **$1.51 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | $600 k | $3.0 M |
| `standard` | 101 | $2.50 M | $252 M |
| `major` | 21 | $4.50 M | $94 M |
| `terminal` | 11 | $4.50 M | $50 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 24 | $12.0 M | $288 M |
| **Stations subtotal** | | | **$692 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 11 | $2.0 M | $22 M |
| **Depots subtotal** | | | **$34 M** |

### Rolling stock

Rolling stock is costed at the **delivered production planning unit: $1.4 M per self-contained car**. The raw 3-car light-metro BOM floor remains 592,840 USD direct material plus 35 % assembly allowance = 800,334 USD per consist, but city CAPEX now adds production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. Motors, sensors, train-control computers, onboard batteries, roof PV, and charge hardware appear here ONLY — never re-billed elsewhere in the city cost stack.

| Per-car cost bucket | Basis | Cost |
|---|---|---|
| Direct material BOM floor | Welded frame, panels, glazing, doors, bogies, traction, batteries, HVAC, electronics, interiors | $267 k |
| Production labour + shop overhead | Cut/bend/weld, fit-out, harnessing, paint, factory supervision, utilities, rework reserve | $420 k |
| Fixtures, tooling, QA, certification evidence | Jigs/fixtures, dimensional QA, EN 15085/45545 evidence, supplier audits, homologation dossier amortisation | $310 k |
| Logistics, warranty, spares, commissioning | Freight, duty, insurance, initial spares/tools, manuals/training, site testing, acceptance runs | $403 k |
| **Total per car** | Delivered production planning unit | **$1.4 M** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 314 | $8.40 M | $2.64 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1884 | $100 k | $188 M |
| High sensitivity check | 1884 | $200 k | $377 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 393.1 km × $0.050 M/km | $19 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $62 M |
| EPC integration + project management (7%) | on subtotal | $360 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.51 bn |
| Stations | $692 M |
| Depots | $34 M |
| Rolling stock | $2.64 bn |
| Railway production plant | $188 M |
| Residual train-control wayside + charging microgrids | $82 M |
| EPC overhead (7%) | $360 M |
| **CAPEX total** | **$5.50 bn** |
| Per-route-km | $14 M / km |
| Per-capita (city pop) | $743 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh dar-es-salaam`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$374 M / yr** | $50 |
| Steady-state, low-ridership (year 8+) | **$472 M / yr** | $64 |
| Steady-state, high-ridership (year 8+) | **$443 M / yr** | $60 |
| Steady-state, operating-neutral revenue case | **$367 M / yr** | $50 |
| Lifecycle envelope (yr 1–30, low scenario) | **$13.48 bn cumulative** | $1,820 |
| Lifecycle envelope (yr 1–30, high scenario) | **$12.80 bn cumulative** | $1,728 |
| Lifecycle envelope (yr 1–30, operating-neutral after opening) | **$11.06 bn cumulative** | $1,493 |

_Population basis: 7,404,689 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $105 M / yr → $76 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $3.30 bn | 3.8% | 30 y, 7 y grace | $218 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $1.38 bn | 9.5% | 30 y, 7 y grace | $149 M / yr |
| Government equity (no debt service) | 15% | $825 M | — | — | — |
| **Total** | **100%** | **$5.50 bn** | | | **$367 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $125 M / yr + bonds $131 M / yr = **$256 M / yr** total — plus the equity tranche amortised across construction ($118 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $106 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $45 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $975 k |
| Traction energy (1329.3 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,371 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $6.6 M |
| **OPEX subtotal** | | **$158 M / yr** |

_Annual fleet utilisation: 282 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 55.4 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.28 |
| Operating-neutral single-trip fare (6 % pass) | $0.33 |
| Day pass (3 trips) | $0.84 (15 % bulk discount) |
| Monthly unlimited pass | $9.90 (~6 % of median monthly income) |
| Annual pass | $108.90 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (786,240 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 366,532 | 610,886 | 1,239,788 |
| Daily paid trips / catchment | 18% | 30% | 61% |
| Daily paid trips / city population | 5% | 8% | 17% |
| Annual paid trips | 133.8 M | 223.0 M | 452.5 M |
| Farebox revenue | $44 M / yr | $74 M / yr | $149 M / yr |
| Station shop leases | $3.2 M / yr | $3.2 M / yr | $3.2 M / yr |
| Advertising boards | $5.2 M / yr | $5.2 M / yr | $5.2 M / yr |
| **Total revenue** | **$53 M / yr** | **$82 M / yr** | **$158 M / yr** |
| Revenue / OPEX recovery | 33% | 52% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Remaining steady-state gov commitment | $472 M / yr | $443 M / yr | **$367 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 22,960 m² of station shop/kiosk leases at $13/m²/month and 4,396 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`dar-es-salaam.toml`](dar-es-salaam.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`dar-es-salaam-network-map.png`](dar-es-salaam-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`dar-es-salaam.stations.json`](dar-es-salaam.stations.json) | Machine-readable station list |
| [`dar-es-salaam.design-quality.yaml`](dar-es-salaam.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug dar-es-salaam

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug dar-es-salaam \
    --sidecar .cache/osr-pipeline/rasters/dar-es-salaam.grid.json \
    --out-dir designs/.../Dar-Es-Salaam

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../dar-es-salaam.toml \
    --out designs/.../README.md
```

`scripts/regenerate-dar-es-salaam.sh` chains steps 3 + drift tests into a single command.
