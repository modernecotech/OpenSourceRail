# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 9,780,429

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Baghdad rail network on OpenStreetMap](baghdad-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`baghdad.corridor.geojson`](baghdad.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 217 |
| Interchange stations | 37 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 44.9% |
| Route length (double track) | 509.5 km |
| Revenue fleet | 364 × 6-car trainsets |
| Spare + cold-reserve | 44 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 55.7 km | 23 | 45 | N Outer ↔ S Outer |
| line-2 | 52.0 km | 26 | 41 | SE Outer ↔ NW Outer |
| line-3 | 56.3 km | 23 | 45 | SW Outer ↔ NE Outer |
| line-4 | 56.8 km | 22 | 46 | SE Outer ↔ NW Mid |
| line-5 | 57.6 km | 24 | 46 | E Outer ↔ W Outer |
| line-6 | 41.9 km | 17 | 34 | W Mid ↔ E Mid |
| line-7 | 46.7 km | 21 | 38 | NE Mid ↔ SW Outer |
| line-8 | 42.9 km | 14 | 35 | NW Mid ↔ S Outer |
| line-9 | 99.7 km | 48 | 78 | NW Mid ↔ NW Mid |
| **Total** | **509.5 km** | **217 unique** | **408** | |

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
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 8,640 = **155,520 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,555,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **1,010,880 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment (capped by practical service capacity)): ≈ **790,454 – 1,010,880 trips/day**

## Catchment

- City population: **9,780,429**
- Anchor-weighted coverage: 44.9%
- Catchment population: **≈ 4,391,412** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 37 | 500 kW | 3000 kWh |
| Major | 53 | 400 kW | 2500 kWh |
| Standard | 99 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **205** | **81,900 kW** | **526,500 kWh** |

Aggregate station-rail charging power: **113,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,359 kWh | 56.6 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.7 kWh/stop | 524 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 410 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 526 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (476.2 km @ $3.0 M/km) | $1.43 bn |
| Elevated (31.4 km @ $12.0 M/km) | $377 M |
| Elevated-interchange premium (19 sites @ $4.50 M) | $86 M |
| **Civil subtotal** | **$1.89 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 13 | $600 k | $7.8 M |
| `standard` | 99 | $2.50 M | $248 M |
| `major` | 53 | $4.50 M | $238 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 37 | $12.0 M | $444 M |
| **Stations subtotal** | | | **$1.01 bn** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 15 | $2.0 M | $30 M |
| **Depots subtotal** | | | **$42 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 408 | $8.40 M | $3.43 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 2448 | $100 k | $245 M |
| High sensitivity check | 2448 | $200 k | $490 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 509.5 km × $0.050 M/km | $25 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $90 M |
| EPC integration + project management (7%) | on subtotal | $471 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.89 bn |
| Stations | $1.01 bn |
| Depots | $42 M |
| Rolling stock | $3.43 bn |
| Railway production plant | $245 M |
| Residual train-control wayside + charging microgrids | $115 M |
| EPC overhead (7%) | $471 M |
| **CAPEX total** | **$7.20 bn** |
| Per-route-km | $14 M / km |
| Per-capita (city pop) | $736 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh baghdad`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$542 M / yr** | $55 |
| Steady-state, low-ridership (year 6+) | **$508 M / yr** | $52 |
| Steady-state, high-ridership (year 6+) | **$508 M / yr** | $52 |
| Steady-state, operating-neutral revenue case | **$508 M / yr** | $52 |
| Lifecycle envelope (yr 1–25, low scenario) | **$12.87 bn cumulative** | $1,316 |
| Lifecycle envelope (yr 1–25, high scenario) | **$12.87 bn cumulative** | $1,316 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$12.87 bn cumulative** | $1,316 |

_Population basis: 9,780,429 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $4.32 bn | 4.0% | 25 y, 5 y grace | $318 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $1.80 bn | 8.5% | 25 y, 5 y grace | $190 M / yr |
| Government equity (no debt service) | 15% | $1.08 bn | — | — | — |
| **Total** | **100%** | **$7.20 bn** | | | **$508 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $173 M / yr + bonds $153 M / yr = **$326 M / yr** total — plus the equity tranche amortised across construction ($216 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $137 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $59 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.3 M |
| Traction energy (1715.9 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (3,069 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $20 M |
| **OPEX subtotal** | | **$217 M / yr** |

_Annual fleet utilisation: 364 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 71.5 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.63 |
| Operating-neutral single-trip fare (6 % pass) | $0.76 |
| Day pass (3 trips) | $1.94 (15 % bulk discount) |
| Monthly unlimited pass | $22.80 (~6 % of median monthly income) |
| Annual pass | $250.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (1,010,880 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 790,454 | 1,010,880 | 677,078 |
| Daily paid trips / catchment | 18% | 23% | 15% |
| Daily paid trips / city population | 8% | 10% | 7% |
| Annual paid trips | 288.5 M | 369.0 M | 247.1 M |
| Farebox revenue | $219 M / yr | $280 M / yr | $188 M / yr |
| Station shop leases | $11 M / yr | $11 M / yr | $11 M / yr |
| Advertising boards | $18 M / yr | $18 M / yr | $18 M / yr |
| **Total revenue** | **$248 M / yr** | **$309 M / yr** | **$217 M / yr** |
| Revenue / OPEX recovery | 115% | 143% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gov debt service + residual OPEX subsidy | $508 M / yr | $508 M / yr | **$508 M / yr** |
| Operating surplus after OPEX | $31 M / yr | $93 M / yr | $0 / yr |

_Commercial-revenue assumptions: 35,040 m² of station shop/kiosk leases at $30/m²/month and 6,540 advertising boards at $266/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`baghdad.toml`](baghdad.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`baghdad-network-map.png`](baghdad-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`baghdad.corridor.geojson`](baghdad.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`baghdad.stations.json`](baghdad.stations.json) | Machine-readable station list |
| [`baghdad.design-quality.yaml`](baghdad.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug baghdad

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug baghdad \
    --sidecar .cache/osr-pipeline/rasters/baghdad.grid.json \
    --out-dir designs/.../Baghdad

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../baghdad.toml \
    --out designs/.../README.md
```

`scripts/regenerate-baghdad.sh` chains steps 3 + drift tests into a single command.
