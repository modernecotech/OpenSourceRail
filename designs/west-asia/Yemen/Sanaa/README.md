# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`sanaa.corridor.geojson`](sanaa.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 126 |
| Interchange stations | 32 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 78.0% |
| Route length (double track) | 260.8 km |
| Revenue fleet | 193 × 6-car trainsets |
| Spare + cold-reserve | 25 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.2 km | 17 | 34 | SE Outer ↔ NW Outer |
| line-2 | 28.8 km | 15 | 24 | S Mid ↔ N Outer |
| line-3 | 22.1 km | 10 | 19 | N Mid ↔ SW Mid |
| line-4 | 27.1 km | 13 | 23 | N Mid ↔ S Mid |
| line-5 | 27.1 km | 10 | 23 | SE Outer ↔ SW Inner |
| line-6 | 24.5 km | 12 | 20 | E Inner ↔ W Outer |
| line-7 | 20.6 km | 9 | 18 | NW Mid ↔ E Mid |
| line-8 | 17.2 km | 11 | 15 | SW Mid ↔ NE Inner |
| line-9 | 52.3 km | 29 | 42 | NW Mid ↔ W Inner |
| **Total** | **260.8 km** | **126 unique** | **218** | |

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
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **552,825 – 921,375 trips/day**

## Catchment

- City population: **3,937,500**
- Anchor-weighted coverage: 78.0%
- Catchment population: **≈ 3,071,250** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 32 | 500 kW | 3000 kWh |
| Major | 34 | 400 kW | 2500 kWh |
| Standard | 36 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **118** | **52,900 kW** | **338,000 kWh** |

Aggregate station-rail charging power: **69,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 695 kWh | 29.0 km average line length |
| Onboard battery coverage | 1.0× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 548 kW average charger across stops |
| Stops to refill one trainset pack | 79 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 264 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 338 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (239.4 km @ $3.0 M/km) | $718 M |
| Elevated (20.6 km @ $12.0 M/km) | $247 M |
| Elevated-interchange premium (19 sites @ $4.50 M) | $86 M |
| **Civil subtotal** | **$1.05 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 8 | $600 k | $4.8 M |
| `standard` | 36 | $2.50 M | $90 M |
| `major` | 34 | $4.50 M | $153 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 32 | $12.0 M | $384 M |
| **Stations subtotal** | | | **$704 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 218 | $8.40 M | $1.83 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1308 | $100 k | $131 M |
| High sensitivity check | 1308 | $200 k | $262 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 260.8 km × $0.050 M/km | $13 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $61 M |
| EPC integration + project management (7%) | on subtotal | $268 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.05 bn |
| Stations | $704 M |
| Depots | $42 M |
| Rolling stock | $1.83 bn |
| Railway production plant | $131 M |
| Residual train-control wayside + charging microgrids | $74 M |
| EPC overhead (7%) | $268 M |
| **CAPEX total** | **$4.10 bn** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $1,042 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh sanaa`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$320 M / yr** | $81 |
| Steady-state, low-ridership (year 11+) | **$385 M / yr** | $98 |
| Steady-state, high-ridership (year 11+) | **$363 M / yr** | $92 |
| Steady-state, operating-neutral revenue case | **$311 M / yr** | $79 |
| Lifecycle envelope (yr 1–40, low scenario) | **$14.75 bn cumulative** | $3,746 |
| Lifecycle envelope (yr 1–40, high scenario) | **$14.10 bn cumulative** | $3,582 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$12.54 bn cumulative** | $3,185 |

_Population basis: 3,937,500 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $74 M / yr → $52 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $2.46 bn | 3.0% | 40 y, 10 y grace | $126 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $1.03 bn | 18.0% | 40 y, 10 y grace | $186 M / yr |
| Government equity (no debt service) | 15% | $615 M | — | — | — |
| **Total** | **100%** | **$4.10 bn** | | | **$311 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $74 M / yr + bonds $185 M / yr = **$258 M / yr** total — plus the equity tranche amortised across construction ($62 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $73 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $36 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $650 k |
| Traction energy (909.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,577 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $2.1 M |
| **OPEX subtotal** | | **$112 M / yr** |

_Annual fleet utilisation: 193 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 37.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$80 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.13 |
| Operating-neutral single-trip fare (6 % pass) | $0.16 |
| Day pass (3 trips) | $0.41 (15 % bulk discount) |
| Monthly unlimited pass | $4.80 (~6 % of median monthly income) |
| Annual pass | $52.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (1,010,880 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 552,825 | 921,375 | 1,813,251 |
| Daily paid trips / catchment | 18% | 30% | 59% |
| Daily paid trips / city population | 14% | 23% | 46% |
| Annual paid trips | 201.8 M | 336.3 M | 661.8 M |
| Farebox revenue | $32 M / yr | $54 M / yr | $106 M / yr |
| Station shop leases | $2.6 M / yr | $2.6 M / yr | $2.6 M / yr |
| Advertising boards | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| **Total revenue** | **$38 M / yr** | **$60 M / yr** | **$112 M / yr** |
| Revenue / OPEX recovery | 34% | 53% | 100% |
| Country farebox-only policy target (diagnostic) | 25% | 25% | 25% |
| Gov debt service + residual OPEX subsidy | $385 M / yr | $363 M / yr | **$311 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 24,744 m² of station shop/kiosk leases at $10/m²/month and 4,508 advertising boards at $75/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`sanaa-network-map.png`](sanaa-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`sanaa.stations.json`](sanaa.stations.json) | Machine-readable station list |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug sanaa

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug sanaa \
    --sidecar .cache/osr-pipeline/rasters/sanaa.grid.json \
    --out-dir designs/.../Sanaa

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../sanaa.toml \
    --out designs/.../README.md
```

`scripts/regenerate-sanaa.sh` chains steps 3 + drift tests into a single command.
