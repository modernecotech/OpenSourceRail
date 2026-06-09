# Dar-Es-Salaam — Urban Rail Network

**Country:** TZ · **Population:** 7,404,689

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Dar-Es-Salaam rail network on OpenStreetMap](dar-es-salaam-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 7 |
| Unique stations | 162 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 27.5% |
| Route length (double track) | 393.1 km |
| Revenue fleet | 466 × 6-car trainsets |
| Revenue fleet passenger capacity | 335,520 AW2 pax (447,360 AW3 crush) |
| Spare + cold-reserve | 51 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 55.8 km | 24 | 73 | NW Outer ↔ SE Mid |
| line-2 | 53.8 km | 21 | 71 | SW Outer ↔ N Mid |
| line-3 | 59.9 km | 26 | 79 | NW Mid ↔ E Outer |
| line-4 | 38.4 km | 16 | 51 | W Mid ↔ SE Mid |
| line-5 | 50.7 km | 21 | 67 | NW Outer ↔ SE Mid |
| line-6 | 35.6 km | 14 | 48 | SW Mid ↔ N Mid |
| line-7 | 99.0 km | 41 | 128 | W Inner ↔ W Inner |
| **Total** | **393.1 km** | **162 unique** | **517** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 335,520 AW2 pax (447,360 AW3 crush) |
| Total fleet capacity | 372,240 AW2 pax (496,320 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 466 × 720 = **335,520 AW2 passengers** (447,360 AW3 crush)
- **Total fleet passenger capacity:** 517 × 720 = **372,240 AW2 passengers** (496,320 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 7 lines × 2 directions × 14,400 = **201,600 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,016,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,612,800 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **1,018,144 – 1,612,800 paid trips/day** (509,072 – 806,400 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **7,404,689**
- Anchor-weighted coverage: 27.5%
- Catchment population: **≈ 2,036,289** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 21 | 400 kW | 2500 kWh |
| Standard | 101 | 300 kW | 2000 kWh |
| Terminal | 11 | 500 kW | 3000 kWh |
| **Total installed** | **158** | **61,200 kW** | **399,500 kWh** |

Aggregate station-rail charging power: **86,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,113.0 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,348 kWh | 56.2 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 532 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 306 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 5,145 MWh/day | 198,493 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 4,839 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,113.0 MW / 5,565 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 400 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (358.1 km @ $3.0 M/km) | $1.07 bn |
| Elevated (31.9 km @ $12.0 M/km) | $383 M |
| Elevated-interchange premium (11 sites @ $4.50 M) | $50 M |
| **Civil subtotal** | **$1.51 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | $600 k | $3.0 M |
| `standard` | 101 | $2.50 M | $252 M |
| `major` | 21 | $4.50 M | $94 M |
| `terminal` | 11 | $4.50 M | $50 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 24 | $12.0 M | $288 M |
| **Stations subtotal** | | | **$692 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 517 | $8.40 M | $4.34 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 3102 | $100 k | $310 M |
| High sensitivity check | 3102 | $200 k | $620 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,112,955 kW @ $700/kW | $779 M |
| Grid interconnection / PPA tie-in | 1,112,955 kW @ $100/kW | $111 M |
| Annual generation proxy | 1,113.0 MW × 5.0 peak-sun-h/day × 365 d/yr | 2,031.1 GWh/yr |
| **Dedicated solar plant subtotal** | | **$890 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 393.1 km × $0.050 M/km | $19 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $62 M |
| EPC integration + project management (7%) | on subtotal | $488 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.51 bn |
| Stations | $692 M |
| Depots | $34 M |
| Rolling stock | $4.34 bn |
| Railway production plant | $310 M |
| Dedicated solar power plant | $890 M |
| Residual train-control wayside + charging microgrids | $82 M |
| EPC overhead (7%) | $488 M |
| **CAPEX total** | **$8.35 bn** |
| Per-route-km | $21 M / km |
| Per-capita (city pop) | $1,127 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh dar-es-salaam`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$203 M / yr** | $27 |
| Steady-state, low-ridership (year 8+) | **$240 M / yr** | $32 |
| Steady-state, high-ridership (year 8+) | **$144 M / yr** | $20 |
| Steady-state, operating-neutral revenue case | **$174 M / yr** | $23 |
| Lifecycle envelope (yr 1–40, low scenario) | **$9.34 bn cumulative** | $1,261 |
| Lifecycle envelope (yr 1–40, high scenario) | **$6.18 bn cumulative** | $835 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$7.16 bn cumulative** | $967 |

_Population basis: 7,404,689 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $66 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $30 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $3.34 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $4.17 bn | 2.0% | 40 y, 7 y grace | $174 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 9.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $835 M | — | — | — |
| **Total** | **100%** | **$8.35 bn** | | | **$174 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $83 M / yr + fallback bonds $0 k / yr = **$83 M / yr** total. The $3.34 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($119 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $174 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $45 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $975 k |
| Traction energy (1877.9 GWh / yr) | 198,493 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 111.7 GWh/yr + dedicated solar plant 1113.0 MW / 2031.1 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $13 M |
| Labour (1,855 FTE) | driverless roster: OCC/remote 276, station/platform 540, passenger service 200, fleet maintenance 416, infrastructure/energy 361, admin/training 62; no train drivers × country median × 12 × engineer-premium 1.4 | $5.1 M |
| **OPEX subtotal** | | **$238 M / yr** |

_Annual service work: 198,493 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 78.2 M train-km / yr (469.5 M car-km / yr). On-site PV covers 111.7 GWh/yr and the dedicated solar plant adds 2031.1 GWh/yr against 1877.9 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.44 |
| Day pass (3 trips) | $1.12 (15 % bulk discount) |
| Monthly unlimited pass | $13.20 (~8 % of median monthly income) |
| Annual pass | $145.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (1,612,800 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 509,072 | 806,400 | 714,401 |
| Daily active riders / catchment | 25% | 40% | 35% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 1,018,144 | 1,612,800 | 1,428,802 |
| Daily paid trips / city population | 14% | 22% | 19% |
| Annual paid trips | 371.6 M | 588.7 M | 521.5 M |
| Farebox revenue | $164 M / yr | $259 M / yr | $229 M / yr |
| Station shop leases | $3.2 M / yr | $3.2 M / yr | $3.2 M / yr |
| Advertising boards | $5.2 M / yr | $5.2 M / yr | $5.2 M / yr |
| **Total revenue** | **$172 M / yr** | **$267 M / yr** | **$238 M / yr** |
| Revenue / OPEX recovery | 72% | 112% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $240 M / yr | $174 M / yr | **$174 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$30 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $240 M / yr | $144 M / yr | **$174 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $30 M / yr | $0 / yr |

_Commercial-revenue assumptions: 22,960 m² of station shop/kiosk leases at $13/m²/month and 4,396 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`dar-es-salaam.toml`](dar-es-salaam.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`dar-es-salaam-network-map.png`](dar-es-salaam-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`dar-es-salaam.stations.json`](dar-es-salaam.stations.json) | Machine-readable station list |
| [`dar-es-salaam.design-quality.yaml`](dar-es-salaam.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug dar-es-salaam

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug dar-es-salaam \
    --sidecar .cache/osr-pipeline/rasters/dar-es-salaam.grid.json \
    --out-dir designs/.../Dar-Es-Salaam

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../dar-es-salaam.toml \
    --out designs/.../README.md
```

`scripts/regenerate-dar-es-salaam.sh` chains steps 3 + drift tests into a single command.
