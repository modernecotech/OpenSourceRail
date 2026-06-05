# Omdurman — Urban Rail Network

**Country:** SD · **Population:** 2,800,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Omdurman rail network on OpenStreetMap](omdurman-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`omdurman.corridor.geojson`](omdurman.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 103 |
| Interchange stations | 17 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 47.4% |
| Route length (double track) | 255.0 km |
| Revenue fleet | 185 × 4-car trainsets |
| Spare + cold-reserve | 22 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 38.2 km | 15 | 31 | SE Outer ↔ NW Mid |
| line-2 | 34.8 km | 14 | 29 | NE Mid ↔ SW Outer |
| line-3 | 39.1 km | 16 | 32 | S Outer ↔ N Outer |
| line-4 | 30.3 km | 14 | 25 | W Mid ↔ E Outer |
| line-5 | 27.4 km | 11 | 23 | W Mid ↔ N Outer |
| line-6 | 85.3 km | 34 | 67 | W Mid ↔ W Mid |
| **Total** | **255.0 km** | **103 unique** | **207** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 480 × 12 = **5,760 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 5,760 = **69,120 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **691,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **449,280 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **238,896 – 398,160 trips/day**

## Catchment

- City population: **2,800,000**
- Anchor-weighted coverage: 47.4%
- Catchment population: **≈ 1,327,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 17 | 500 kW | 3000 kWh |
| Major | 8 | 400 kW | 2500 kWh |
| Standard | 68 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **103** | **41,600 kW** | **274,000 kWh** |

Aggregate station-rail charging power: **56,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 680 kWh | 42.5 km average line length |
| Onboard battery coverage | 0.7× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.2 kWh/stop | 551 kW average charger across stops |
| Stops to refill one trainset pack | 52 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 208 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 274 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (244.2 km @ $3.0 M/km) | $733 M |
| Elevated (9.7 km @ $12.0 M/km) | $117 M |
| Elevated-interchange premium (8 sites @ $4.50 M) | $36 M |
| **Civil subtotal** | **$885 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 68 | $2.50 M | $170 M |
| `major` | 8 | $4.50 M | $36 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 17 | $12.0 M | $204 M |
| **Stations subtotal** | | | **$456 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 9 | $2.0 M | $18 M |
| **Depots subtotal** | | | **$30 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 207 | $5.60 M | $1.16 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 828 | $100 k | $83 M |
| High sensitivity check | 828 | $200 k | $166 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 255.0 km × $0.050 M/km | $13 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $41 M |
| EPC integration + project management (7%) | on subtotal | $187 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $885 M |
| Stations | $456 M |
| Depots | $30 M |
| Rolling stock | $1.16 bn |
| Railway production plant | $83 M |
| Residual train-control wayside + charging microgrids | $53 M |
| EPC overhead (7%) | $187 M |
| **CAPEX total** | **$2.85 bn** |
| Per-route-km | $11 M / km |
| Per-capita (city pop) | $1,019 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh omdurman`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$201 M / yr** | $72 |
| Steady-state, low-ridership (year 11+) | **$250 M / yr** | $89 |
| Steady-state, high-ridership (year 11+) | **$238 M / yr** | $85 |
| Steady-state, operating-neutral revenue case | **$196 M / yr** | $70 |
| Lifecycle envelope (yr 1–40, low scenario) | **$9.52 bn cumulative** | $3,400 |
| Lifecycle envelope (yr 1–40, high scenario) | **$9.14 bn cumulative** | $3,263 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$7.89 bn cumulative** | $2,819 |

_Population basis: 2,800,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $54 M / yr → $41 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $1.71 bn | 3.0% | 40 y, 10 y grace | $87 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $713 M | 15.0% | 40 y, 10 y grace | $109 M / yr |
| Government equity (no debt service) | 15% | $428 M | — | — | — |
| **Total** | **100%** | **$2.85 bn** | | | **$196 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $51 M / yr + bonds $107 M / yr = **$158 M / yr** total — plus the equity tranche amortised across construction ($43 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $46 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $27 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $635 k |
| Traction energy (581.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,542 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $2.8 M |
| **OPEX subtotal** | | **$77 M / yr** |

_Annual fleet utilisation: 185 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 36.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$110 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.18 |
| Operating-neutral single-trip fare (6 % pass) | $0.22 |
| Day pass (3 trips) | $0.56 (15 % bulk discount) |
| Monthly unlimited pass | $6.60 (~6 % of median monthly income) |
| Annual pass | $72.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (449,280 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 238,896 | 398,160 | 914,936 |
| Daily paid trips / catchment | 18% | 30% | 69% |
| Daily paid trips / city population | 9% | 14% | 33% |
| Annual paid trips | 87.2 M | 145.3 M | 334.0 M |
| Farebox revenue | $19 M / yr | $32 M / yr | $73 M / yr |
| Station shop leases | $1.6 M / yr | $1.6 M / yr | $1.6 M / yr |
| Advertising boards | $2.2 M / yr | $2.2 M / yr | $2.2 M / yr |
| **Total revenue** | **$23 M / yr** | **$36 M / yr** | **$77 M / yr** |
| Revenue / OPEX recovery | 30% | 46% | 100% |
| Country farebox-only policy target (diagnostic) | 30% | 30% | 30% |
| Remaining steady-state gov commitment | $250 M / yr | $238 M / yr | **$196 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 14,880 m² of station shop/kiosk leases at $10/m²/month and 2,856 advertising boards at $77/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`omdurman.toml`](omdurman.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`omdurman-network-map.png`](omdurman-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`omdurman.corridor.geojson`](omdurman.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`omdurman.stations.json`](omdurman.stations.json) | Machine-readable station list |
| [`omdurman.design-quality.yaml`](omdurman.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug omdurman

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug omdurman \
    --sidecar .cache/osr-pipeline/rasters/omdurman.grid.json \
    --out-dir designs/.../Omdurman

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../omdurman.toml \
    --out designs/.../README.md
```

`scripts/regenerate-omdurman.sh` chains steps 3 + drift tests into a single command.
