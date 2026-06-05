# Kanpur — Urban Rail Network

**Country:** IN · **Population:** 3,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kanpur rail network on OpenStreetMap](kanpur-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kanpur.corridor.geojson`](kanpur.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 7 |
| Unique stations | 149 |
| Interchange stations | 18 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 43.8% |
| Route length (double track) | 339.0 km |
| Revenue fleet | 245 × 6-car trainsets |
| Spare + cold-reserve | 28 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 46.5 km | 22 | 38 | W Mid ↔ NE Outer |
| line-2 | 35.0 km | 20 | 29 | NW Mid ↔ SE Mid |
| line-3 | 51.7 km | 22 | 41 | N Mid ↔ S Outer |
| line-4 | 51.1 km | 23 | 41 | E Outer ↔ W Outer |
| line-5 | 28.6 km | 11 | 24 | SW Outer ↔ E Inner |
| line-6 | 33.0 km | 16 | 27 | S Inner ↔ NE Outer |
| line-7 | 93.2 km | 36 | 73 | NW Mid ↔ NW Mid |
| **Total** | **339.0 km** | **149 unique** | **273** | |

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
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **252,288 – 420,480 trips/day**

## Catchment

- City population: **3,200,000**
- Anchor-weighted coverage: 43.8%
- Catchment population: **≈ 1,401,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 18 | 500 kW | 3000 kWh |
| Major | 55 | 400 kW | 2500 kWh |
| Standard | 54 | 300 kW | 2000 kWh |
| Terminal | 11 | 500 kW | 3000 kWh |
| **Total installed** | **139** | **57,700 kW** | **372,500 kWh** |

Aggregate station-rail charging power: **78,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,162 kWh | 48.4 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 525 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 288 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 372 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (321.2 km @ $3.0 M/km) | $964 M |
| Elevated (16.6 km @ $12.0 M/km) | $200 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$1.21 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 11 | $600 k | $6.6 M |
| `standard` | 54 | $2.50 M | $135 M |
| `major` | 55 | $4.50 M | $248 M |
| `terminal` | 11 | $4.50 M | $50 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 18 | $12.0 M | $216 M |
| **Stations subtotal** | | | **$660 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 273 | $8.40 M | $2.29 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1638 | $100 k | $164 M |
| High sensitivity check | 1638 | $200 k | $328 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 339.0 km × $0.050 M/km | $17 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $61 M |
| EPC integration + project management (7%) | on subtotal | $311 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.21 bn |
| Stations | $660 M |
| Depots | $34 M |
| Rolling stock | $2.29 bn |
| Railway production plant | $164 M |
| Residual train-control wayside + charging microgrids | $78 M |
| EPC overhead (7%) | $311 M |
| **CAPEX total** | **$4.75 bn** |
| Per-route-km | $14 M / km |
| Per-capita (city pop) | $1,484 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kanpur`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$342 M / yr** | $107 |
| Steady-state, low-ridership (year 6+) | **$407 M / yr** | $127 |
| Steady-state, high-ridership (year 6+) | **$379 M / yr** | $119 |
| Steady-state, operating-neutral revenue case | **$323 M / yr** | $101 |
| Lifecycle envelope (yr 1–25, low scenario) | **$9.86 bn cumulative** | $3,081 |
| Lifecycle envelope (yr 1–25, high scenario) | **$9.29 bn cumulative** | $2,904 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$8.18 bn cumulative** | $2,555 |

_Population basis: 3,200,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $84 M / yr → $56 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $2.85 bn | 4.0% | 25 y, 5 y grace | $210 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $1.19 bn | 7.2% | 25 y, 5 y grace | $114 M / yr |
| Government equity (no debt service) | 15% | $712 M | — | — | — |
| **Total** | **100%** | **$4.75 bn** | | | **$323 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $114 M / yr + bonds $85 M / yr = **$199 M / yr** total — plus the equity tranche amortised across construction ($142 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $92 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $38 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $845 k |
| Traction energy (1154.9 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,046 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $7.9 M |
| **OPEX subtotal** | | **$139 M / yr** |

_Annual fleet utilisation: 245 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 48.1 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.38 |
| Operating-neutral single-trip fare (6 % pass) | $0.46 |
| Day pass (3 trips) | $1.17 (15 % bulk discount) |
| Monthly unlimited pass | $13.80 (~6 % of median monthly income) |
| Annual pass | $151.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (786,240 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 252,288 | 420,480 | 752,974 |
| Daily paid trips / catchment | 18% | 30% | 54% |
| Daily paid trips / city population | 8% | 13% | 24% |
| Annual paid trips | 92.1 M | 153.5 M | 274.8 M |
| Farebox revenue | $42 M / yr | $71 M / yr | $126 M / yr |
| Station shop leases | $4.7 M / yr | $4.7 M / yr | $4.7 M / yr |
| Advertising boards | $7.4 M / yr | $7.4 M / yr | $7.4 M / yr |
| **Total revenue** | **$54 M / yr** | **$83 M / yr** | **$139 M / yr** |
| Revenue / OPEX recovery | 39% | 60% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gov debt service + residual OPEX subsidy | $407 M / yr | $379 M / yr | **$323 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 24,120 m² of station shop/kiosk leases at $18/m²/month and 4,508 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kanpur.toml`](kanpur.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kanpur-network-map.png`](kanpur-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kanpur.corridor.geojson`](kanpur.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kanpur.stations.json`](kanpur.stations.json) | Machine-readable station list |
| [`kanpur.design-quality.yaml`](kanpur.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kanpur

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kanpur \
    --sidecar .cache/osr-pipeline/rasters/kanpur.grid.json \
    --out-dir designs/.../Kanpur

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kanpur.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kanpur.sh` chains steps 3 + drift tests into a single command.
