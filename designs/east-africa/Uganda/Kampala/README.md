# Kampala — Urban Rail Network

**Country:** UG · **Population:** 1,875,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kampala rail network on OpenStreetMap](kampala-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kampala.corridor.geojson`](kampala.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 98 |
| Interchange stations | 12 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 24.0% |
| Route length (double track) | 201.1 km |
| Revenue fleet | 240 × 4-car trainsets |
| Revenue fleet passenger capacity | 115,200 AW2 pax (153,600 AW3 crush) |
| Spare + cold-reserve | 26 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 39.8 km | 22 | 53 | W Outer ↔ E Outer |
| line-2 | 36.9 km | 21 | 50 | S Outer ↔ N Outer |
| line-3 | 34.6 km | 20 | 47 | S Outer ↔ N Outer |
| line-4 | 89.9 km | 36 | 116 | NW Outer ↔ NW Outer |
| **Total** | **201.1 km** | **98 unique** | **266** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 115,200 AW2 pax (153,600 AW3 crush) |
| Total fleet capacity | 127,680 AW2 pax (170,240 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 240 × 480 = **115,200 AW2 passengers** (153,600 AW3 crush)
- **Total fleet passenger capacity:** 266 × 480 = **127,680 AW2 passengers** (170,240 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 9,600 = **76,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **768,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **614,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **112,500 – 202,500 trips/day**

## Catchment

- City population: **1,875,000**
- Anchor-weighted coverage: 24.0%
- Catchment population: **≈ 450,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 12 | 500 kW | 3000 kWh |
| Major | 35 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **99** | **41,300 kW** | **270,500 kWh** |

Aggregate station-rail charging power: **52,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 804 kWh | 50.3 km average line length |
| Onboard battery coverage | 0.6× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 536 kW average charger across stops |
| Stops to refill one trainset pack | 54 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 206 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 270 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (192.0 km @ $3.0 M/km) | $576 M |
| Elevated (8.2 km @ $12.0 M/km) | $99 M |
| Elevated-interchange premium (7 sites @ $4.50 M) | $32 M |
| **Civil subtotal** | **$706 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 46 | $2.50 M | $115 M |
| `major` | 35 | $4.50 M | $158 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 12 | $12.0 M | $144 M |
| **Stations subtotal** | | | **$444 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 266 | $5.60 M | $1.49 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1064 | $100 k | $106 M |
| High sensitivity check | 1064 | $200 k | $213 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 201.1 km × $0.050 M/km | $10 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $41 M |
| EPC integration + project management (7%) | on subtotal | $197 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $706 M |
| Stations | $444 M |
| Depots | $22 M |
| Rolling stock | $1.49 bn |
| Railway production plant | $106 M |
| Residual train-control wayside + charging microgrids | $51 M |
| EPC overhead (7%) | $197 M |
| **CAPEX total** | **$3.02 bn** |
| Per-route-km | $15 M / km |
| Per-capita (city pop) | $1,609 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kampala`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$73 M / yr** | $39 |
| Steady-state, low-ridership (year 8+) | **$128 M / yr** | $69 |
| Steady-state, high-ridership (year 8+) | **$116 M / yr** | $62 |
| Steady-state, operating-neutral revenue case | **$63 M / yr** | $34 |
| Lifecycle envelope (yr 1–40, low scenario) | **$4.75 bn cumulative** | $2,534 |
| Lifecycle envelope (yr 1–40, high scenario) | **$4.33 bn cumulative** | $2,310 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.59 bn cumulative** | $1,380 |

_Population basis: 1,875,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $66 M / yr → $53 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.21 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $1.51 bn | 2.0% | 40 y, 7 y grace | $63 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 14.0% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $302 M | — | — | — |
| **Total** | **100%** | **$3.02 bn** | | | **$63 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $30 M / yr + fallback bonds $0 k / yr = **$30 M / yr** total. The $1.21 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($43 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $60 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $23 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $501 k |
| Traction energy (754.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,219 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $3.0 M |
| **OPEX subtotal** | | **$86 M / yr** |

_Annual fleet utilisation: 240 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 47.1 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$145 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.39 |
| Day pass (3 trips) | $0.99 (15 % bulk discount) |
| Monthly unlimited pass | $11.60 (~8 % of median monthly income) |
| Annual pass | $127.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (614,400 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 112,500 | 202,500 | 577,058 |
| Daily paid trips / catchment | 25% | 45% | 128% |
| Daily paid trips / city population | 6% | 11% | 31% |
| Annual paid trips | 41.1 M | 73.9 M | 210.6 M |
| Farebox revenue | $16 M / yr | $29 M / yr | $81 M / yr |
| Station shop leases | $2.0 M / yr | $2.0 M / yr | $2.0 M / yr |
| Advertising boards | $3.1 M / yr | $3.1 M / yr | $3.1 M / yr |
| **Total revenue** | **$21 M / yr** | **$34 M / yr** | **$86 M / yr** |
| Revenue / OPEX recovery | 24% | 39% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $128 M / yr | $116 M / yr | **$63 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $128 M / yr | $116 M / yr | **$63 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 16,000 m² of station shop/kiosk leases at $12/m²/month and 2,992 advertising boards at $102/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kampala.toml`](kampala.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kampala-network-map.png`](kampala-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kampala.corridor.geojson`](kampala.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kampala.stations.json`](kampala.stations.json) | Machine-readable station list |
| [`kampala.design-quality.yaml`](kampala.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kampala

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kampala \
    --sidecar .cache/osr-pipeline/rasters/kampala.grid.json \
    --out-dir designs/.../Kampala

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kampala.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kampala.sh` chains steps 3 + drift tests into a single command.
