# Kakamega — Urban Rail Network

**Country:** KE · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kakamega rail network on OpenStreetMap](kakamega-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kakamega.corridor.geojson`](kakamega.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 24 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 77.4% |
| Route length (double track) | 42.4 km |
| Revenue fleet | 85 × 2-car trainsets |
| Revenue fleet passenger capacity | 20,400 AW2 pax (27,200 AW3 crush) |
| Spare + cold-reserve | 10 × 2-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 13.6 km | 8 | 30 | SE Mid ↔ W Mid |
| line-2 | 15.4 km | 8 | 35 | NE Outer ↔ W Mid |
| line-3 | 13.3 km | 8 | 30 | S Outer ↔ NW Mid |
| **Total** | **42.4 km** | **24 unique** | **95** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 240 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 320 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 20,400 AW2 pax (27,200 AW3 crush) |
| Total fleet capacity | 22,800 AW2 pax (30,400 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 240 AW2 passengers (`tram-2car`)
- **Revenue fleet simultaneous capacity:** 85 × 240 = **20,400 AW2 passengers** (27,200 AW3 crush)
- **Total fleet passenger capacity:** 95 × 240 = **22,800 AW2 passengers** (30,400 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 240 × 20 = **4,800 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 4,800 = **28,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **288,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **230,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **58,050 – 104,490 trips/day**

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 77.4%
- Catchment population: **≈ 232,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 3 | 400 kW | 2500 kWh |
| Standard | 12 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **24** | **13,800 kW** | **95,500 kWh** |

Aggregate station-rail charging power: **15,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 113 kWh | 14.1 km average line length |
| Onboard battery coverage | 2.1× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.4 kWh/stop | 625 kW average charger across stops |
| Stops to refill one trainset pack | 23 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 69 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 96 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (40.5 km @ $3.0 M/km) | $122 M |
| Elevated (1.5 km @ $12.0 M/km) | $18 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$145 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 12 | $2.50 M | $30 M |
| `major` | 3 | $4.50 M | $14 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$107 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 95 | $2.80 M | $266 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 190 | $100 k | $19 M |
| High sensitivity check | 190 | $200 k | $38 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 42.4 km × $0.050 M/km | $2.1 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $10 M |
| EPC integration + project management (7%) | on subtotal | $40 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $145 M |
| Stations | $107 M |
| Depots | $22 M |
| Rolling stock | $266 M |
| Railway production plant | $19 M |
| Residual train-control wayside + charging microgrids | $13 M |
| EPC overhead (7%) | $40 M |
| **CAPEX total** | **$611 M** |
| Per-route-km | $14 M / km |
| Per-capita (city pop) | $2,037 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kakamega`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$15 M / yr** | $49 |
| Steady-state, low-ridership (year 8+) | **$15 M / yr** | $50 |
| Steady-state, high-ridership (year 8+) | **$4.7 M / yr** | $16 |
| Steady-state, operating-neutral revenue case | **$13 M / yr** | $42 |
| Lifecycle envelope (yr 1–40, low scenario) | **$602 M cumulative** | $2,005 |
| Lifecycle envelope (yr 1–40, high scenario) | **$259 M cumulative** | $862 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$524 M cumulative** | $1,747 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $2.3 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $8.0 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $244 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $306 M | 2.0% | 40 y, 7 y grace | $13 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 11.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $61 M | — | — | — |
| **Total** | **100%** | **$611 M** | | | **$13 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $6.1 M / yr + fallback bonds $0 k / yr = **$6.1 M / yr** total. The $244 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($8.7 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $11 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $5.5 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $105 k |
| Traction energy (84.0 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (266 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $1.0 M |
| **OPEX subtotal** | | **$17 M / yr** |

_Annual fleet utilisation: 85 revenue trainsets × 20.5 h/day × 365 d/yr × 22 km/h commercial × 75% revenue factor = 10.5 M train-km / yr (~123 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.61 |
| Day pass (3 trips) | $1.56 (15 % bulk discount) |
| Monthly unlimited pass | $18.40 (~8 % of median monthly income) |
| Annual pass | $202.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (230,400 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 58,050 | 104,490 | 68,537 |
| Daily paid trips / catchment | 25% | 45% | 30% |
| Daily paid trips / city population | 19% | 35% | 23% |
| Annual paid trips | 21.2 M | 38.1 M | 25.0 M |
| Farebox revenue | $13 M / yr | $23 M / yr | $15 M / yr |
| Station shop leases | $718 k / yr | $718 k / yr | $718 k / yr |
| Advertising boards | $1.2 M / yr | $1.2 M / yr | $1.2 M / yr |
| **Total revenue** | **$15 M / yr** | **$25 M / yr** | **$17 M / yr** |
| Revenue / OPEX recovery | 86% | 147% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Gross repayable-debt service + residual OPEX subsidy | $15 M / yr | $13 M / yr | **$13 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$8.0 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $15 M / yr | $4.7 M / yr | **$13 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $8.0 M / yr | $0 / yr |

_Commercial-revenue assumptions: 3,696 m² of station shop/kiosk leases at $18/m²/month and 720 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kakamega.toml`](kakamega.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kakamega-network-map.png`](kakamega-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kakamega.corridor.geojson`](kakamega.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kakamega.stations.json`](kakamega.stations.json) | Machine-readable station list |
| [`kakamega.design-quality.yaml`](kakamega.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kakamega

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kakamega \
    --sidecar .cache/osr-pipeline/rasters/kakamega.grid.json \
    --out-dir designs/.../Kakamega

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kakamega.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kakamega.sh` chains steps 3 + drift tests into a single command.
