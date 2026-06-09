# Najran — Urban Rail Network

**Country:** SA · **Population:** 500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Najran rail network on OpenStreetMap](najran-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`najran.corridor.geojson`](najran.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 33 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 46.5% |
| Route length (double track) | 56.7 km |
| Revenue fleet | 83 × 3-car trainsets |
| Revenue fleet passenger capacity | 29,880 AW2 pax (39,840 AW3 crush) |
| Spare + cold-reserve | 10 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 21.4 km | 13 | 35 | NE Mid ↔ SW Outer |
| line-2 | 20.0 km | 10 | 32 | SW Outer ↔ E Outer |
| line-3 | 15.3 km | 10 | 26 | N Outer ↔ SE Mid |
| **Total** | **56.7 km** | **33 unique** | **93** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 29,880 AW2 pax (39,840 AW3 crush) |
| Total fleet capacity | 33,480 AW2 pax (44,640 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 83 × 360 = **29,880 AW2 passengers** (39,840 AW3 crush)
- **Total fleet passenger capacity:** 93 × 360 = **33,480 AW2 passengers** (44,640 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **58,125 – 104,625 trips/day**

## Catchment

- City population: **500,000**
- Anchor-weighted coverage: 46.5%
- Catchment population: **≈ 232,500** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 9 | 400 kW | 2500 kWh |
| Standard | 16 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **33** | **16,900 kW** | **115,500 kWh** |

Aggregate station-rail charging power: **19,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 227 kWh | 18.9 km average line length |
| Onboard battery coverage | 1.6× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.8 kWh/stop | 591 kW average charger across stops |
| Stops to refill one trainset pack | 37 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 84 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 116 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (44.0 km @ $3.0 M/km) | $132 M |
| Elevated (12.4 km @ $12.0 M/km) | $149 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$286 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 16 | $2.50 M | $40 M |
| `major` | 9 | $4.50 M | $40 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 2 | $12.0 M | $24 M |
| **Stations subtotal** | | | **$132 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 93 | $4.20 M | $391 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 279 | $100 k | $28 M |
| High sensitivity check | 279 | $200 k | $56 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 56.7 km × $0.050 M/km | $2.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $13 M |
| EPC integration + project management (7%) | on subtotal | $61 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $286 M |
| Stations | $132 M |
| Depots | $22 M |
| Rolling stock | $391 M |
| Railway production plant | $28 M |
| Residual train-control wayside + charging microgrids | $16 M |
| EPC overhead (7%) | $61 M |
| **CAPEX total** | **$935 M** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $1,871 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh najran`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$28 M / yr** | $56 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$19 M / yr** | $37 |
| Lifecycle envelope (yr 1–40, low scenario) | **$140 M cumulative** | $281 |
| Lifecycle envelope (yr 1–40, high scenario) | **$140 M cumulative** | $281 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$795 M cumulative** | $1,590 |

_Population basis: 500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $19 M / yr → $19 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $374 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $468 M | 2.0% | 40 y, 5 y grace | $19 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 4.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $94 M | — | — | — |
| **Total** | **100%** | **$935 M** | | | **$19 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $9.4 M / yr + fallback bonds $0 k / yr = **$9.4 M / yr** total. The $374 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($19 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $16 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $8.8 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $141 k |
| Traction energy (167.7 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (352 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $10 M |
| **OPEX subtotal** | | **$35 M / yr** |

_Annual fleet utilisation: 83 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 14.0 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $4.53 |
| Day pass (3 trips) | $11.56 (15 % bulk discount) |
| Monthly unlimited pass | $136.00 (~8 % of median monthly income) |
| Annual pass | $1496.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (345,600 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 58,125 | 104,625 | 11,295 |
| Daily paid trips / catchment | 25% | 45% | 5% |
| Daily paid trips / city population | 12% | 21% | 2% |
| Annual paid trips | 21.2 M | 38.2 M | 4.1 M |
| Farebox revenue | $96 M / yr | $173 M / yr | $19 M / yr |
| Station shop leases | $4.6 M / yr | $4.6 M / yr | $4.6 M / yr |
| Advertising boards | $11 M / yr | $11 M / yr | $11 M / yr |
| **Total revenue** | **$112 M / yr** | **$189 M / yr** | **$35 M / yr** |
| Revenue / OPEX recovery | 324% | 546% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Gross repayable-debt service + residual OPEX subsidy | $19 M / yr | $19 M / yr | **$19 M / yr** |
| Operating surplus applied to debt support | -$19 M / yr | -$19 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$19 M / yr** |
| Operating surplus after OPEX (before debt support) | $77 M / yr | $154 M / yr | $0 / yr |

_Commercial-revenue assumptions: 4,800 m² of station shop/kiosk leases at $90/m²/month and 936 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`najran.toml`](najran.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`najran-network-map.png`](najran-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`najran.corridor.geojson`](najran.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`najran.stations.json`](najran.stations.json) | Machine-readable station list |
| [`najran.design-quality.yaml`](najran.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug najran

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug najran \
    --sidecar .cache/osr-pipeline/rasters/najran.grid.json \
    --out-dir designs/.../Najran

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../najran.toml \
    --out designs/.../README.md
```

`scripts/regenerate-najran.sh` chains steps 3 + drift tests into a single command.
