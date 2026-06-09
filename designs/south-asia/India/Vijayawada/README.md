# Vijayawada — Urban Rail Network

**Country:** IN · **Population:** 1,500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Vijayawada rail network on OpenStreetMap](vijayawada-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`vijayawada.corridor.geojson`](vijayawada.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 93 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 58.0% |
| Route length (double track) | 225.1 km |
| Revenue fleet | 272 × 4-car trainsets |
| Revenue fleet passenger capacity | 130,560 AW2 pax (174,080 AW3 crush) |
| Spare + cold-reserve | 31 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.4 km | 20 | 56 | NW Outer ↔ SE Outer |
| line-2 | 37.1 km | 15 | 50 | W Outer ↔ E Outer |
| line-3 | 28.6 km | 13 | 39 | SW Mid ↔ NE Mid |
| line-4 | 35.4 km | 12 | 48 | S Outer ↔ NW Outer |
| line-5 | 21.5 km | 9 | 30 | W Outer ↔ E Mid |
| line-6 | 61.1 km | 25 | 80 | NW Mid ↔ NW Mid |
| **Total** | **225.1 km** | **93 unique** | **303** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 130,560 AW2 pax (174,080 AW3 crush) |
| Total fleet capacity | 145,440 AW2 pax (193,920 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 272 × 480 = **130,560 AW2 passengers** (174,080 AW3 crush)
- **Total fleet passenger capacity:** 303 × 480 = **145,440 AW2 passengers** (193,920 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,152,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **921,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **217,499 – 391,499 trips/day**

## Catchment

- City population: **1,500,000**
- Anchor-weighted coverage: 58.0%
- Catchment population: **≈ 869,999** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 12 | 400 kW | 2500 kWh |
| Standard | 35 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **81** | **36,800 kW** | **239,000 kWh** |

Aggregate station-rail charging power: **48,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 600 kWh | 37.5 km average line length |
| Onboard battery coverage | 0.8× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.7 kWh/stop | 524 kW average charger across stops |
| Stops to refill one trainset pack | 55 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 184 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 239 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (203.7 km @ $3.0 M/km) | $611 M |
| Elevated (18.5 km @ $12.0 M/km) | $222 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$878 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 13 | $600 k | $7.8 M |
| `standard` | 35 | $2.50 M | $88 M |
| `major` | 12 | $4.50 M | $54 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
| `interchange-elevated` | 22 | $12.0 M | $264 M |
| **Stations subtotal** | | | **$475 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 303 | $5.60 M | $1.70 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1212 | $100 k | $121 M |
| High sensitivity check | 1212 | $200 k | $242 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 225.1 km × $0.050 M/km | $11 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $41 M |
| EPC integration + project management (7%) | on subtotal | $228 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $878 M |
| Stations | $475 M |
| Depots | $30 M |
| Rolling stock | $1.70 bn |
| Railway production plant | $121 M |
| Residual train-control wayside + charging microgrids | $52 M |
| EPC overhead (7%) | $228 M |
| **CAPEX total** | **$3.48 bn** |
| Per-route-km | $15 M / km |
| Per-capita (city pop) | $2,321 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh vijayawada`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$104 M / yr** | $70 |
| Steady-state, low-ridership (year 6+) | **$114 M / yr** | $76 |
| Steady-state, high-ridership (year 6+) | **$75 M / yr** | $50 |
| Steady-state, operating-neutral revenue case | **$70 M / yr** | $46 |
| Lifecycle envelope (yr 1–40, low scenario) | **$4.52 bn cumulative** | $3,016 |
| Lifecycle envelope (yr 1–40, high scenario) | **$3.16 bn cumulative** | $2,107 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.96 bn cumulative** | $1,973 |

_Population basis: 1,500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $45 M / yr → $5.8 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.39 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $1.74 bn | 2.0% | 40 y, 5 y grace | $70 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 7.2% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $348 M | — | — | — |
| **Total** | **100%** | **$3.48 bn** | | | **$70 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $35 M / yr + fallback bonds $0 k / yr = **$35 M / yr** total. The $1.39 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($70 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $68 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $28 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $556 k |
| Traction energy (854.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,363 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $5.3 M |
| **OPEX subtotal** | | **$101 M / yr** |

_Annual fleet utilisation: 272 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 53.4 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.61 |
| Day pass (3 trips) | $1.56 (15 % bulk discount) |
| Monthly unlimited pass | $18.40 (~8 % of median monthly income) |
| Annual pass | $202.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (921,600 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 217,499 | 391,499 | 417,232 |
| Daily paid trips / catchment | 25% | 45% | 48% |
| Daily paid trips / city population | 14% | 26% | 28% |
| Annual paid trips | 79.4 M | 142.9 M | 152.3 M |
| Farebox revenue | $49 M / yr | $88 M / yr | $93 M / yr |
| Station shop leases | $3.1 M / yr | $3.1 M / yr | $3.1 M / yr |
| Advertising boards | $4.8 M / yr | $4.8 M / yr | $4.8 M / yr |
| **Total revenue** | **$57 M / yr** | **$96 M / yr** | **$101 M / yr** |
| Revenue / OPEX recovery | 56% | 94% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $114 M / yr | $75 M / yr | **$70 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $114 M / yr | $75 M / yr | **$70 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 15,992 m² of station shop/kiosk leases at $18/m²/month and 2,952 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`vijayawada.toml`](vijayawada.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`vijayawada-network-map.png`](vijayawada-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`vijayawada.corridor.geojson`](vijayawada.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`vijayawada.stations.json`](vijayawada.stations.json) | Machine-readable station list |
| [`vijayawada.design-quality.yaml`](vijayawada.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug vijayawada

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug vijayawada \
    --sidecar .cache/osr-pipeline/rasters/vijayawada.grid.json \
    --out-dir designs/.../Vijayawada

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../vijayawada.toml \
    --out designs/.../README.md
```

`scripts/regenerate-vijayawada.sh` chains steps 3 + drift tests into a single command.
