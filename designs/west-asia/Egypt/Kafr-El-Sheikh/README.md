# Kafr-El-Sheikh — Urban Rail Network

**Country:** EG · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kafr-El-Sheikh rail network on OpenStreetMap](kafr-el-sheikh-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kafr-el-sheikh.corridor.geojson`](kafr-el-sheikh.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 22 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 75.2% |
| Route length (double track) | 33.0 km |
| Revenue fleet | 41 × 2-car trainsets |
| Spare + cold-reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 15.7 km | 9 | 21 | NE Outer ↔ SW Mid |
| line-2 |  8.7 km | 7 | 13 | SW Mid ↔ S Mid |
| line-3 |  8.6 km | 6 | 13 | NE Inner ↔ NW Mid |
| **Total** | **33.0 km** | **22 unique** | **47** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 240 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 320 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 240 AW2 passengers (`tram-2car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 240 × 12 = **2,880 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 2,880 = **17,280 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **172,800 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **112,320 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **40,608 – 67,680 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 75.2%
- Catchment population: **≈ 225,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 7 | 400 kW | 2500 kWh |
| Standard | 5 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **21** | **13,300 kW** | **91,500 kWh** |

Aggregate station-rail charging power: **13,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 88 kWh | 11.0 km average line length |
| Onboard battery coverage | 2.7× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.4 kWh/stop | 625 kW average charger across stops |
| Stops to refill one trainset pack | 23 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 66 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 92 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (31.0 km @ $3.0 M/km) | $93 M |
| Elevated (1.9 km @ $12.0 M/km) | $23 M |
| Elevated-interchange premium (2 sites @ $4.50 M) | $9.0 M |
| **Civil subtotal** | **$125 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 5 | $2.50 M | $12 M |
| `major` | 7 | $4.50 M | $32 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$108 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 5 | $2.0 M | $10 M |
| **Depots subtotal** | | | **$22 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 47 | $2.80 M | $132 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 94 | $100 k | $9.4 M |
| High sensitivity check | 94 | $200 k | $19 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 33.0 km × $0.050 M/km | $1.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $11 M |
| EPC integration + project management (7%) | on subtotal | $29 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $125 M |
| Stations | $108 M |
| Depots | $22 M |
| Rolling stock | $132 M |
| Railway production plant | $9.4 M |
| Residual train-control wayside + charging microgrids | $12 M |
| EPC overhead (7%) | $29 M |
| **CAPEX total** | **$437 M** |
| Per-route-km | $13 M / km |
| Per-capita (city pop) | $1,456 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kafr-el-sheikh`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$36 M / yr** | $121 |
| Steady-state, low-ridership (year 6+) | **$35 M / yr** | $116 |
| Steady-state, high-ridership (year 6+) | **$33 M / yr** | $111 |
| Steady-state, operating-neutral revenue case | **$33 M / yr** | $111 |
| Lifecycle envelope (yr 1–25, low scenario) | **$878 M cumulative** | $2,925 |
| Lifecycle envelope (yr 1–25, high scenario) | **$850 M cumulative** | $2,834 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$850 M cumulative** | $2,834 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $1.4 M / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $262 M | 4.5% | 25 y, 5 y grace | $20 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $109 M | 10.5% | 25 y, 5 y grace | $13 M / yr |
| Government equity (no debt service) | 15% | $66 M | — | — | — |
| **Total** | **100%** | **$437 M** | | | **$33 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $12 M / yr + bonds $11 M / yr = **$23 M / yr** total — plus the equity tranche amortised across construction ($13 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $5.3 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $5.1 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $82 k |
| Traction energy (40.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (210 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $917 k |
| **OPEX subtotal** | | **$11 M / yr** |

_Annual fleet utilisation: 41 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 5.1 M train-km / yr (~123 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$260 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.43 |
| Operating-neutral single-trip fare (6 % pass) | $0.52 |
| Day pass (3 trips) | $1.33 (15 % bulk discount) |
| Monthly unlimited pass | $15.60 (~6 % of median monthly income) |
| Annual pass | $171.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (112,320 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 40,608 | 67,680 | 47,847 |
| Daily paid trips / catchment | 18% | 30% | 21% |
| Daily paid trips / city population | 14% | 23% | 16% |
| Annual paid trips | 14.8 M | 24.7 M | 17.5 M |
| Farebox revenue | $7.7 M / yr | $13 M / yr | $9.1 M / yr |
| Station shop leases | $879 k / yr | $879 k / yr | $879 k / yr |
| Advertising boards | $1.4 M / yr | $1.4 M / yr | $1.4 M / yr |
| **Total revenue** | **$10.0 M / yr** | **$15 M / yr** | **$11 M / yr** |
| Revenue / OPEX recovery | 88% | 133% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Remaining steady-state gov commitment | $35 M / yr | $33 M / yr | **$33 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $3.8 M / yr | $0 / yr |

_Commercial-revenue assumptions: 4,000 m² of station shop/kiosk leases at $21/m²/month and 756 advertising boards at $182/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kafr-el-sheikh.toml`](kafr-el-sheikh.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kafr-el-sheikh-network-map.png`](kafr-el-sheikh-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kafr-el-sheikh.corridor.geojson`](kafr-el-sheikh.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kafr-el-sheikh.stations.json`](kafr-el-sheikh.stations.json) | Machine-readable station list |
| [`kafr-el-sheikh.design-quality.yaml`](kafr-el-sheikh.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kafr-el-sheikh

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kafr-el-sheikh \
    --sidecar .cache/osr-pipeline/rasters/kafr-el-sheikh.grid.json \
    --out-dir designs/.../Kafr-El-Sheikh

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kafr-el-sheikh.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kafr-el-sheikh.sh` chains steps 3 + drift tests into a single command.
