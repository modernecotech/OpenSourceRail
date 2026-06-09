# Latakia — Urban Rail Network

**Country:** SY · **Population:** 700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Latakia rail network on OpenStreetMap](latakia-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`latakia.corridor.geojson`](latakia.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 26 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 54.1% |
| Route length (double track) | 41.0 km |
| Revenue fleet | 62 × 3-car trainsets |
| Revenue fleet passenger capacity | 22,320 AW2 pax (29,760 AW3 crush) |
| Spare + cold-reserve | 8 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 15.9 km | 10 | 27 | NW Outer ↔ E Mid |
| line-2 | 17.1 km | 11 | 28 | E Outer ↔ SW Mid |
| line-3 |  8.0 km | 5 | 15 | SW Mid ↔ NW Mid |
| **Total** | **41.0 km** | **26 unique** | **70** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 22,320 AW2 pax (29,760 AW3 crush) |
| Total fleet capacity | 25,200 AW2 pax (33,600 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 62 × 360 = **22,320 AW2 passengers** (29,760 AW3 crush)
- **Total fleet passenger capacity:** 70 × 360 = **25,200 AW2 passengers** (33,600 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **94,675 – 170,415 trips/day**

## Catchment

- City population: **700,000**
- Anchor-weighted coverage: 54.1%
- Catchment population: **≈ 378,700** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 10 | 400 kW | 2500 kWh |
| Standard | 8 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **26** | **14,900 kW** | **102,000 kWh** |

Aggregate station-rail charging power: **16,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 164 kWh | 13.7 km average line length |
| Onboard battery coverage | 2.2× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 10.3 kWh/stop | 615 kW average charger across stops |
| Stops to refill one trainset pack | 35 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 74 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 102 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (40.8 km @ $3.0 M/km) | $123 M |
| **Civil subtotal** | **$123 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 8 | $2.50 M | $20 M |
| `major` | 10 | $4.50 M | $45 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
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
| `light-metro-3car` (revenue + spare + cold reserve) | 70 | $4.20 M | $294 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 210 | $100 k | $21 M |
| High sensitivity check | 210 | $200 k | $42 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 41.0 km × $0.050 M/km | $2.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $11 M |
| EPC integration + project management (7%) | on subtotal | $41 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $123 M |
| Stations | $108 M |
| Depots | $22 M |
| Rolling stock | $294 M |
| Railway production plant | $21 M |
| Residual train-control wayside + charging microgrids | $13 M |
| EPC overhead (7%) | $41 M |
| **CAPEX total** | **$622 M** |
| Per-route-km | $15 M / km |
| Per-capita (city pop) | $889 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh latakia`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$12 M / yr** | $18 |
| Steady-state, low-ridership (year 11+) | **$24 M / yr** | $34 |
| Steady-state, high-ridership (year 11+) | **$18 M / yr** | $26 |
| Steady-state, operating-neutral revenue case | **$14 M / yr** | $20 |
| Lifecycle envelope (yr 1–40, low scenario) | **$832 M cumulative** | $1,188 |
| Lifecycle envelope (yr 1–40, high scenario) | **$677 M cumulative** | $967 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$541 M cumulative** | $773 |

_Population basis: 700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $9.7 M / yr → $4.5 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $249 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $311 M | 2.0% | 40 y, 10 y grace | $14 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 20.0% | 40 y, 10 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $62 M | — | — | — |
| **Total** | **100%** | **$622 M** | | | **$14 M / yr** |

_During the 10-year grace period the public sponsor pays interest only on repayable debt — concessional loan $6.2 M / yr + fallback bonds $0 k / yr = **$6.2 M / yr** total. The $249 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($6.2 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $12 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $5.1 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $102 k |
| Traction energy (125.3 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (258 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $303 k |
| **OPEX subtotal** | | **$17 M / yr** |

_Annual fleet utilisation: 62 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 10.4 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$70 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.19 |
| Day pass (3 trips) | $0.48 (15 % bulk discount) |
| Monthly unlimited pass | $5.60 (~8 % of median monthly income) |
| Annual pass | $61.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (345,600 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 94,675 | 170,415 | 236,818 |
| Daily paid trips / catchment | 25% | 45% | 63% |
| Daily paid trips / city population | 14% | 24% | 34% |
| Annual paid trips | 34.6 M | 62.2 M | 86.4 M |
| Farebox revenue | $6.5 M / yr | $12 M / yr | $16 M / yr |
| Station shop leases | $457 k / yr | $457 k / yr | $457 k / yr |
| Advertising boards | $633 k / yr | $633 k / yr | $633 k / yr |
| **Total revenue** | **$7.5 M / yr** | **$13 M / yr** | **$17 M / yr** |
| Revenue / OPEX recovery | 44% | 74% | 100% |
| Country farebox-only policy target (diagnostic) | 30% | 30% | 30% |
| Gross repayable-debt service + residual OPEX subsidy | $24 M / yr | $18 M / yr | **$14 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **-$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $24 M / yr | $18 M / yr | **$14 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 4,328 m² of station shop/kiosk leases at $10/m²/month and 828 advertising boards at $75/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`latakia.toml`](latakia.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`latakia-network-map.png`](latakia-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`latakia.corridor.geojson`](latakia.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`latakia.stations.json`](latakia.stations.json) | Machine-readable station list |
| [`latakia.design-quality.yaml`](latakia.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug latakia

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug latakia \
    --sidecar .cache/osr-pipeline/rasters/latakia.grid.json \
    --out-dir designs/.../Latakia

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../latakia.toml \
    --out designs/.../README.md
```

`scripts/regenerate-latakia.sh` chains steps 3 + drift tests into a single command.
