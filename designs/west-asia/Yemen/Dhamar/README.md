# Dhamar — Urban Rail Network

**Country:** YE · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Dhamar rail network on OpenStreetMap](dhamar-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`dhamar.corridor.geojson`](dhamar.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 18 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 75.9% |
| Route length (double track) | 32.3 km |
| Revenue fleet | 40 × 2-car trainsets |
| Spare + cold-reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 11.2 km | 7 | 16 | S Inner ↔ N Outer |
| line-2 | 13.5 km | 7 | 18 | SW Outer ↔ NW Inner |
| line-3 |  7.7 km | 4 | 12 | E Mid ↔ N Mid |
| **Total** | **32.3 km** | **18 unique** | **46** | |

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
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **40,986 – 68,310 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 75.9%
- Catchment population: **≈ 227,700** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 3 | 400 kW | 2500 kWh |
| Standard | 6 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **18** | **12,000 kW** | **83,500 kWh** |

Aggregate station-rail charging power: **12,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 86 kWh | 10.8 km average line length |
| Onboard battery coverage | 2.8× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 11.1 kWh/stop | 667 kW average charger across stops |
| Stops to refill one trainset pack | 22 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 60 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 84 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (31.6 km @ $3.0 M/km) | $95 M |
| **Civil subtotal** | **$95 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 6 | $2.50 M | $15 M |
| `major` | 3 | $4.50 M | $14 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 3 | $8.0 M | $24 M |
| **Stations subtotal** | | | **$80 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 46 | $2.80 M | $129 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 92 | $100 k | $9.2 M |
| High sensitivity check | 92 | $200 k | $18 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 32.3 km × $0.050 M/km | $1.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $8.4 M |
| EPC integration + project management (7%) | on subtotal | $24 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $95 M |
| Stations | $80 M |
| Depots | $22 M |
| Rolling stock | $129 M |
| Railway production plant | $9.2 M |
| Residual train-control wayside + charging microgrids | $10 M |
| EPC overhead (7%) | $24 M |
| **CAPEX total** | **$369 M** |
| Per-route-km | $11 M / km |
| Per-capita (city pop) | $1,230 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh dhamar`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$29 M / yr** | $96 |
| Steady-state, low-ridership (year 11+) | **$34 M / yr** | $114 |
| Steady-state, high-ridership (year 11+) | **$33 M / yr** | $109 |
| Steady-state, operating-neutral revenue case | **$28 M / yr** | $93 |
| Lifecycle envelope (yr 1–40, low scenario) | **$1.32 bn cumulative** | $4,388 |
| Lifecycle envelope (yr 1–40, high scenario) | **$1.27 bn cumulative** | $4,228 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.13 bn cumulative** | $3,762 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $6.3 M / yr → $4.7 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $221 M | 3.0% | 40 y, 10 y grace | $11 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $92 M | 18.0% | 40 y, 10 y grace | $17 M / yr |
| Government equity (no debt service) | 15% | $55 M | — | — | — |
| **Total** | **100%** | **$369 M** | | | **$28 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $6.6 M / yr + bonds $17 M / yr = **$23 M / yr** total — plus the equity tranche amortised across construction ($5.5 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $5.2 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $3.9 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $79 k |
| Traction energy (39.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (206 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $277 k |
| **OPEX subtotal** | | **$9.4 M / yr** |

_Annual fleet utilisation: 40 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 4.9 M train-km / yr (~123 k km / trainset / yr)._

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

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (112,320 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 40,986 | 68,310 | 148,234 |
| Daily paid trips / catchment | 18% | 30% | 65% |
| Daily paid trips / city population | 14% | 23% | 49% |
| Annual paid trips | 15.0 M | 24.9 M | 54.1 M |
| Farebox revenue | $2.4 M / yr | $4.0 M / yr | $8.7 M / yr |
| Station shop leases | $329 k / yr | $329 k / yr | $329 k / yr |
| Advertising boards | $459 k / yr | $459 k / yr | $459 k / yr |
| **Total revenue** | **$3.2 M / yr** | **$4.8 M / yr** | **$9.4 M / yr** |
| Revenue / OPEX recovery | 34% | 51% | 100% |
| Country farebox-only policy target (diagnostic) | 25% | 25% | 25% |
| Remaining steady-state gov commitment | $34 M / yr | $33 M / yr | **$28 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 3,120 m² of station shop/kiosk leases at $10/m²/month and 600 advertising boards at $75/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`dhamar.toml`](dhamar.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`dhamar-network-map.png`](dhamar-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`dhamar.corridor.geojson`](dhamar.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`dhamar.stations.json`](dhamar.stations.json) | Machine-readable station list |
| [`dhamar.design-quality.yaml`](dhamar.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug dhamar

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug dhamar \
    --sidecar .cache/osr-pipeline/rasters/dhamar.grid.json \
    --out-dir designs/.../Dhamar

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../dhamar.toml \
    --out designs/.../README.md
```

`scripts/regenerate-dhamar.sh` chains steps 3 + drift tests into a single command.
