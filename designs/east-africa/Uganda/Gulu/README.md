# Gulu — Urban Rail Network

**Country:** UG · **Population:** 350,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Gulu rail network on OpenStreetMap](gulu-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`gulu.corridor.geojson`](gulu.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 36 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 50.4% |
| Route length (double track) | 63.7 km |
| Revenue fleet | 93 × 3-car trainsets |
| Revenue fleet passenger capacity | 33,480 AW2 pax (44,640 AW3 crush) |
| Spare + cold-reserve | 12 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 20.5 km | 13 | 34 | E Mid ↔ W Outer |
| line-2 | 15.2 km | 10 | 26 | NE Mid ↔ SW Mid |
| line-3 | 28.0 km | 13 | 45 | NW Outer ↔ SE Outer |
| **Total** | **63.7 km** | **36 unique** | **105** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 33,480 AW2 pax (44,640 AW3 crush) |
| Total fleet capacity | 37,800 AW2 pax (50,400 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 93 × 360 = **33,480 AW2 passengers** (44,640 AW3 crush)
- **Total fleet passenger capacity:** 105 × 360 = **37,800 AW2 passengers** (50,400 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **44,100 – 79,380 trips/day**

## Catchment

- City population: **350,000**
- Anchor-weighted coverage: 50.4%
- Catchment population: **≈ 176,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 10 | 400 kW | 2500 kWh |
| Standard | 16 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **35** | **17,800 kW** | **121,000 kWh** |

Aggregate station-rail charging power: **20,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 255 kWh | 21.2 km average line length |
| Onboard battery coverage | 1.4× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.6 kWh/stop | 576 kW average charger across stops |
| Stops to refill one trainset pack | 37 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 89 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 121 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (62.5 km @ $3.0 M/km) | $187 M |
| Elevated (1.2 km @ $12.0 M/km) | $14 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$206 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 16 | $2.50 M | $40 M |
| `major` | 10 | $4.50 M | $45 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$149 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 105 | $4.20 M | $441 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 315 | $100 k | $32 M |
| High sensitivity check | 315 | $200 k | $63 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 63.7 km × $0.050 M/km | $3.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $15 M |
| EPC integration + project management (7%) | on subtotal | $61 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $206 M |
| Stations | $149 M |
| Depots | $22 M |
| Rolling stock | $441 M |
| Railway production plant | $32 M |
| Residual train-control wayside + charging microgrids | $18 M |
| EPC overhead (7%) | $61 M |
| **CAPEX total** | **$929 M** |
| Per-route-km | $15 M / km |
| Per-capita (city pop) | $2,653 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh gulu`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$23 M / yr** | $64 |
| Steady-state, low-ridership (year 8+) | **$38 M / yr** | $108 |
| Steady-state, high-ridership (year 8+) | **$33 M / yr** | $93 |
| Steady-state, operating-neutral revenue case | **$19 M / yr** | $55 |
| Lifecycle envelope (yr 1–40, low scenario) | **$1.40 bn cumulative** | $4,006 |
| Lifecycle envelope (yr 1–40, high scenario) | **$1.24 bn cumulative** | $3,536 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$797 M cumulative** | $2,276 |

_Population basis: 350,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $18 M / yr → $13 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $371 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $464 M | 2.0% | 40 y, 7 y grace | $19 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 14.0% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $93 M | — | — | — |
| **Total** | **100%** | **$929 M** | | | **$19 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $9.3 M / yr + fallback bonds $0 k / yr = **$9.3 M / yr** total. The $371 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($13 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $18 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $7.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $159 k |
| Traction energy (187.9 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (394 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $960 k |
| **OPEX subtotal** | | **$26 M / yr** |

_Annual fleet utilisation: 93 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 15.7 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$145 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.39 |
| Day pass (3 trips) | $0.99 (15 % bulk discount) |
| Monthly unlimited pass | $11.60 (~8 % of median monthly income) |
| Annual pass | $127.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (345,600 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 44,100 | 79,380 | 174,103 |
| Daily paid trips / catchment | 25% | 45% | 99% |
| Daily paid trips / city population | 13% | 23% | 50% |
| Annual paid trips | 16.1 M | 29.0 M | 63.5 M |
| Farebox revenue | $6.2 M / yr | $11 M / yr | $25 M / yr |
| Station shop leases | $660 k / yr | $660 k / yr | $660 k / yr |
| Advertising boards | $1.1 M / yr | $1.1 M / yr | $1.1 M / yr |
| **Total revenue** | **$8.0 M / yr** | **$13 M / yr** | **$26 M / yr** |
| Revenue / OPEX recovery | 30% | 49% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $38 M / yr | $33 M / yr | **$19 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $38 M / yr | $33 M / yr | **$19 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 5,392 m² of station shop/kiosk leases at $12/m²/month and 1,040 advertising boards at $102/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`gulu.toml`](gulu.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`gulu-network-map.png`](gulu-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`gulu.corridor.geojson`](gulu.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`gulu.stations.json`](gulu.stations.json) | Machine-readable station list |
| [`gulu.design-quality.yaml`](gulu.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug gulu

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug gulu \
    --sidecar .cache/osr-pipeline/rasters/gulu.grid.json \
    --out-dir designs/.../Gulu

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../gulu.toml \
    --out designs/.../README.md
```

`scripts/regenerate-gulu.sh` chains steps 3 + drift tests into a single command.
