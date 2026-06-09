# Sulaymaniyah — Urban Rail Network

**Country:** IQ · **Population:** 2,150,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Sulaymaniyah rail network on OpenStreetMap](sulaymaniyah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`sulaymaniyah.corridor.geojson`](sulaymaniyah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 47 |
| Interchange stations | 10 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 67.1% |
| Route length (double track) | 117.4 km |
| Revenue fleet | 144 × 4-car trainsets |
| Revenue fleet passenger capacity | 69,120 AW2 pax (92,160 AW3 crush) |
| Spare + cold-reserve | 18 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 15.5 km | 9 | 23 | W Mid ↔ E Inner |
| line-2 | 15.1 km | 7 | 23 | W Mid ↔ SE Mid |
| line-3 | 27.7 km | 9 | 38 | SW Mid ↔ NE Outer |
| line-4 | 59.1 km | 23 | 78 | W Mid ↔ W Mid |
| **Total** | **117.4 km** | **47 unique** | **162** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 69,120 AW2 pax (92,160 AW3 crush) |
| Total fleet capacity | 77,760 AW2 pax (103,680 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 144 × 480 = **69,120 AW2 passengers** (92,160 AW3 crush)
- **Total fleet passenger capacity:** 162 × 480 = **77,760 AW2 passengers** (103,680 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 9,600 = **76,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **768,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **614,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment (capped by practical service capacity)): ≈ **360,662 – 614,400 trips/day**

## Catchment

- City population: **2,150,000**
- Anchor-weighted coverage: 67.1%
- Catchment population: **≈ 1,442,650** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 10 | 500 kW | 3000 kWh |
| Major | 4 | 400 kW | 2500 kWh |
| Standard | 26 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **46** | **21,900 kW** | **147,000 kWh** |

Aggregate station-rail charging power: **26,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 470 kWh | 29.4 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.4 kWh/stop | 564 kW average charger across stops |
| Stops to refill one trainset pack | 51 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 110 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 147 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (105.4 km @ $3.0 M/km) | $316 M |
| Elevated (11.5 km @ $12.0 M/km) | $139 M |
| Elevated-interchange premium (6 sites @ $4.50 M) | $27 M |
| **Civil subtotal** | **$482 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | $600 k | $1.2 M |
| `standard` | 26 | $2.50 M | $65 M |
| `major` | 4 | $4.50 M | $18 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 10 | $12.0 M | $120 M |
| **Stations subtotal** | | | **$232 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 162 | $5.60 M | $907 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 648 | $100 k | $65 M |
| High sensitivity check | 648 | $200 k | $130 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 117.4 km × $0.050 M/km | $5.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $21 M |
| EPC integration + project management (7%) | on subtotal | $121 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $482 M |
| Stations | $232 M |
| Depots | $22 M |
| Rolling stock | $907 M |
| Railway production plant | $65 M |
| Residual train-control wayside + charging microgrids | $26 M |
| EPC overhead (7%) | $121 M |
| **CAPEX total** | **$1.86 bn** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $863 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh sulaymaniyah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$56 M / yr** | $26 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$37 M / yr** | $17 |
| Lifecycle envelope (yr 1–40, low scenario) | **$278 M cumulative** | $129 |
| Lifecycle envelope (yr 1–40, high scenario) | **$278 M cumulative** | $129 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.58 bn cumulative** | $734 |

_Population basis: 2,150,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $37 M / yr → $37 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $742 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $928 M | 2.0% | 40 y, 5 y grace | $37 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 8.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $186 M | — | — | — |
| **Total** | **100%** | **$1.86 bn** | | | **$37 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $19 M / yr + fallback bonds $0 k / yr = **$19 M / yr** total. The $742 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($37 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $36 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $15 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $292 k |
| Traction energy (452.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (716 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $4.6 M |
| **OPEX subtotal** | | **$56 M / yr** |

_Annual fleet utilisation: 144 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 28.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.01 |
| Day pass (3 trips) | $2.58 (15 % bulk discount) |
| Monthly unlimited pass | $30.40 (~8 % of median monthly income) |
| Annual pass | $334.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (614,400 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 360,662 | 614,400 | 133,894 |
| Daily paid trips / catchment | 25% | 43% | 9% |
| Daily paid trips / city population | 17% | 29% | 6% |
| Annual paid trips | 131.6 M | 224.3 M | 48.9 M |
| Farebox revenue | $133 M / yr | $227 M / yr | $50 M / yr |
| Station shop leases | $2.4 M / yr | $2.4 M / yr | $2.4 M / yr |
| Advertising boards | $3.9 M / yr | $3.9 M / yr | $3.9 M / yr |
| **Total revenue** | **$140 M / yr** | **$234 M / yr** | **$56 M / yr** |
| Revenue / OPEX recovery | 250% | 418% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $37 M / yr | $37 M / yr | **$37 M / yr** |
| Operating surplus applied to debt support | -$37 M / yr | -$37 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$37 M / yr** |
| Operating surplus after OPEX (before debt support) | $84 M / yr | $178 M / yr | $0 / yr |

_Commercial-revenue assumptions: 7,608 m² of station shop/kiosk leases at $30/m²/month and 1,436 advertising boards at $266/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`sulaymaniyah.toml`](sulaymaniyah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`sulaymaniyah-network-map.png`](sulaymaniyah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`sulaymaniyah.corridor.geojson`](sulaymaniyah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`sulaymaniyah.stations.json`](sulaymaniyah.stations.json) | Machine-readable station list |
| [`sulaymaniyah.design-quality.yaml`](sulaymaniyah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug sulaymaniyah

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug sulaymaniyah \
    --sidecar .cache/osr-pipeline/rasters/sulaymaniyah.grid.json \
    --out-dir designs/.../Sulaymaniyah

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../sulaymaniyah.toml \
    --out designs/.../README.md
```

`scripts/regenerate-sulaymaniyah.sh` chains steps 3 + drift tests into a single command.
