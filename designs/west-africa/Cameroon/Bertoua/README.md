# Bertoua — Urban Rail Network

**Country:** CM · **Population:** 350,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Bertoua rail network on OpenStreetMap](bertoua-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`bertoua.corridor.geojson`](bertoua.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 20 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 77.0% |
| Route length (double track) | 28.8 km |
| Revenue fleet | 28 × 3-car trainsets |
| Spare + cold-reserve | 6 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 |  9.0 km | 7 | 11 | W Mid ↔ SE Mid |
| line-2 | 10.4 km | 7 | 12 | NW Mid ↔ NE Outer |
| line-3 |  9.4 km | 6 | 11 | S Outer ↔ NW Mid |
| **Total** | **28.8 km** | **20 unique** | **34** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 360 × 12 = **4,320 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 4,320 = **25,920 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **259,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **168,480 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **48,510 – 80,850 trips/day**

## Catchment

- City population: **350,000**
- Anchor-weighted coverage: 77.0%
- Catchment population: **≈ 269,500** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 4 | 400 kW | 2500 kWh |
| Standard | 7 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **20** | **12,700 kW** | **88,000 kWh** |

Aggregate station-rail charging power: **13,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 115 kWh | 9.6 km average line length |
| Onboard battery coverage | 3.1× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 10.8 kWh/stop | 650 kW average charger across stops |
| Stops to refill one trainset pack | 33 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 64 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 88 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (27.6 km @ $3.0 M/km) | $83 M |
| Elevated (1.2 km @ $12.0 M/km) | $14 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$101 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 7 | $2.50 M | $18 M |
| `major` | 4 | $4.50 M | $18 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$99 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 34 | $4.20 M | $143 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 102 | $100 k | $10 M |
| High sensitivity check | 102 | $200 k | $20 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 28.8 km × $0.050 M/km | $1.4 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $9.6 M |
| EPC integration + project management (7%) | on subtotal | $27 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $101 M |
| Stations | $99 M |
| Depots | $22 M |
| Rolling stock | $143 M |
| Railway production plant | $10 M |
| Residual train-control wayside + charging microgrids | $11 M |
| EPC overhead (7%) | $27 M |
| **CAPEX total** | **$413 M** |
| Per-route-km | $14 M / km |
| Per-capita (city pop) | $1,181 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh bertoua`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 8** and runs for **23 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$27 M / yr** | $77 |
| Steady-state, low-ridership (year 8+) | **$30 M / yr** | $85 |
| Steady-state, high-ridership (year 8+) | **$27 M / yr** | $76 |
| Steady-state, operating-neutral revenue case | **$27 M / yr** | $76 |
| Lifecycle envelope (yr 1–30, low scenario) | **$873 M cumulative** | $2,495 |
| Lifecycle envelope (yr 1–30, high scenario) | **$804 M cumulative** | $2,298 |
| Lifecycle envelope (yr 1–30, operating-neutral after opening) | **$804 M cumulative** | $2,298 |

_Population basis: 350,000 (catchment per `lib/city-batches/world-sample.toml`). After year 30, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $3.0 M / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $248 M | 3.8% | 30 y, 7 y grace | $16 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $103 M | 8.5% | 30 y, 7 y grace | $10 M / yr |
| Government equity (no debt service) | 15% | $62 M | — | — | — |
| **Total** | **100%** | **$413 M** | | | **$27 M / yr** |

_During the 7-year grace period the operator pays interest only — multilateral $9.4 M / yr + bonds $8.8 M / yr = **$18 M / yr** total — plus the equity tranche amortised across construction ($8.9 M / yr × 7 yr). Principal repayment begins in year 8 on a 23-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $5.7 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $4.4 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $72 k |
| Traction energy (56.6 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (185 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $559 k |
| **OPEX subtotal** | | **$11 M / yr** |

_Annual fleet utilisation: 28 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 4.7 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$180 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.30 |
| Operating-neutral single-trip fare (6 % pass) | $0.36 |
| Day pass (3 trips) | $0.92 (15 % bulk discount) |
| Monthly unlimited pass | $10.80 (~6 % of median monthly income) |
| Annual pass | $118.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (168,480 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 48,510 | 80,850 | 71,389 |
| Daily paid trips / catchment | 18% | 30% | 26% |
| Daily paid trips / city population | 14% | 23% | 20% |
| Annual paid trips | 17.7 M | 29.5 M | 26.1 M |
| Farebox revenue | $6.4 M / yr | $11 M / yr | $9.4 M / yr |
| Station shop leases | $538 k / yr | $538 k / yr | $538 k / yr |
| Advertising boards | $869 k / yr | $869 k / yr | $869 k / yr |
| **Total revenue** | **$7.8 M / yr** | **$12 M / yr** | **$11 M / yr** |
| Revenue / OPEX recovery | 72% | 112% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Remaining steady-state gov commitment | $30 M / yr | $27 M / yr | **$27 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $1.2 M / yr | $0 / yr |

_Commercial-revenue assumptions: 3,536 m² of station shop/kiosk leases at $14/m²/month and 676 advertising boards at $126/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`bertoua.toml`](bertoua.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`bertoua-network-map.png`](bertoua-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`bertoua.corridor.geojson`](bertoua.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`bertoua.stations.json`](bertoua.stations.json) | Machine-readable station list |
| [`bertoua.design-quality.yaml`](bertoua.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug bertoua

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug bertoua \
    --sidecar .cache/osr-pipeline/rasters/bertoua.grid.json \
    --out-dir designs/.../Bertoua

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../bertoua.toml \
    --out designs/.../README.md
```

`scripts/regenerate-bertoua.sh` chains steps 3 + drift tests into a single command.
