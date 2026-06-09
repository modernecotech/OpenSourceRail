# Kinshasa — Urban Rail Network

**Country:** CD · **Population:** 17,178,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kinshasa rail network on OpenStreetMap](kinshasa-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kinshasa.corridor.geojson`](kinshasa.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 182 |
| Interchange stations | 35 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 49.4% |
| Route length (double track) | 384.8 km |
| Revenue fleet | 459 × 6-car trainsets |
| Revenue fleet passenger capacity | 330,480 AW2 pax (440,640 AW3 crush) |
| Spare + cold-reserve | 50 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 54.1 km | 27 | 71 | W Outer ↔ E Outer |
| line-2 | 37.3 km | 15 | 50 | W Mid ↔ SE Mid |
| line-3 | 35.6 km | 17 | 48 | NE Inner ↔ SW Mid |
| line-4 | 45.7 km | 20 | 61 | NW Outer ↔ SE Mid |
| line-5 | 57.3 km | 23 | 75 | SW Outer ↔ E Outer |
| line-6 | 35.1 km | 17 | 48 | S Mid ↔ N Mid |
| line-7 | 45.2 km | 21 | 60 | NW Outer ↔ SE Inner |
| line-8 | 74.3 km | 43 | 96 | NW Inner ↔ NW Inner |
| **Total** | **384.8 km** | **182 unique** | **509** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 330,480 AW2 pax (440,640 AW3 crush) |
| Total fleet capacity | 366,480 AW2 pax (488,640 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 459 × 720 = **330,480 AW2 passengers** (440,640 AW3 crush)
- **Total fleet passenger capacity:** 509 × 720 = **366,480 AW2 passengers** (488,640 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 14,400 = **230,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,304,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,843,200 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **1,843,200 – 1,843,200 paid trips/day** (921,600 – 921,600 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **17,178,000**
- Anchor-weighted coverage: 49.4%
- Catchment population: **≈ 8,485,932** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 35 | 500 kW | 3000 kWh |
| Major | 64 | 400 kW | 2500 kWh |
| Standard | 59 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **172** | **72,300 kW** | **462,000 kWh** |

Aggregate station-rail charging power: **95,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,075.4 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,154 kWh | 48.1 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 526 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 362 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 5,037 MWh/day | 194,328 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 4,675 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,075.4 MW / 5,377 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 462 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (355.8 km @ $3.0 M/km) | $1.07 bn |
| Elevated (22.9 km @ $12.0 M/km) | $275 M |
| Elevated-interchange premium (16 sites @ $4.50 M) | $72 M |
| **Civil subtotal** | **$1.41 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 11 | $600 k | $6.6 M |
| `standard` | 59 | $2.50 M | $148 M |
| `major` | 64 | $4.50 M | $288 M |
| `terminal` | 13 | $4.50 M | $58 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 3 | $8.0 M | $24 M |
| `interchange-elevated` | 32 | $12.0 M | $384 M |
| **Stations subtotal** | | | **$914 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 13 | $2.0 M | $26 M |
| **Depots subtotal** | | | **$38 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 509 | $8.40 M | $4.28 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 3054 | $100 k | $305 M |
| High sensitivity check | 3054 | $200 k | $611 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,075,361 kW @ $700/kW | $753 M |
| Grid interconnection / PPA tie-in | 1,075,361 kW @ $100/kW | $108 M |
| Annual generation proxy | 1,075.4 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,962.5 GWh/yr |
| **Dedicated solar plant subtotal** | | **$860 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 384.8 km × $0.050 M/km | $19 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $82 M |
| EPC integration + project management (7%) | on subtotal | $493 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.41 bn |
| Stations | $914 M |
| Depots | $38 M |
| Rolling stock | $4.28 bn |
| Railway production plant | $305 M |
| Dedicated solar power plant | $860 M |
| Residual train-control wayside + charging microgrids | $101 M |
| EPC overhead (7%) | $493 M |
| **CAPEX total** | **$8.40 bn** |
| Per-route-km | $22 M / km |
| Per-capita (city pop) | $489 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kinshasa`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$168 M / yr** | $10 |
| Steady-state, low-ridership (year 11+) | **$218 M / yr** | $13 |
| Steady-state, high-ridership (year 11+) | **$218 M / yr** | $13 |
| Steady-state, operating-neutral revenue case | **$188 M / yr** | $11 |
| Lifecycle envelope (yr 1–40, low scenario) | **$8.22 bn cumulative** | $479 |
| Lifecycle envelope (yr 1–40, high scenario) | **$8.22 bn cumulative** | $479 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$7.31 bn cumulative** | $425 |

_Population basis: 17,178,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $30 M / yr → $30 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $3.36 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $4.20 bn | 2.0% | 40 y, 10 y grace | $188 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 13.0% | 40 y, 10 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $840 M | — | — | — |
| **Total** | **100%** | **$8.40 bn** | | | **$188 M / yr** |

_During the 10-year grace period the public sponsor pays interest only on repayable debt — concessional loan $84 M / yr + fallback bonds $0 k / yr = **$84 M / yr** total. The $3.36 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($84 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $171 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $47 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $947 k |
| Traction energy (1838.5 GWh / yr) | 194,328 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 131.9 GWh/yr + dedicated solar plant 1075.4 MW / 1962.5 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $13 M |
| Labour (2,086 FTE) | driverless roster: OCC/remote 276, station/platform 733, passenger service 228, fleet maintenance 409, infrastructure/energy 370, admin/training 70; no train drivers × country median × 12 × engineer-premium 1.4 | $3.9 M |
| **OPEX subtotal** | | **$236 M / yr** |

_Annual service work: 194,328 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 76.6 M train-km / yr (459.6 M car-km / yr). On-site PV covers 131.9 GWh/yr and the dedicated solar plant adds 1962.5 GWh/yr against 1838.5 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$110 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.29 |
| Day pass (3 trips) | $0.75 (15 % bulk discount) |
| Monthly unlimited pass | $8.80 (~8 % of median monthly income) |
| Annual pass | $96.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (1,843,200 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 921,600 | 921,600 | 1,063,878 |
| Daily active riders / catchment | 11% | 11% | 13% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 1,843,200 | 1,843,200 | 2,127,756 |
| Daily paid trips / city population | 11% | 11% | 12% |
| Annual paid trips | 672.8 M | 672.8 M | 776.6 M |
| Farebox revenue | $197 M / yr | $197 M / yr | $228 M / yr |
| Station shop leases | $3.5 M / yr | $3.5 M / yr | $3.5 M / yr |
| Advertising boards | $4.8 M / yr | $4.8 M / yr | $4.8 M / yr |
| **Total revenue** | **$206 M / yr** | **$206 M / yr** | **$236 M / yr** |
| Revenue / OPEX recovery | 87% | 87% | 100% |
| Country farebox-only policy target (diagnostic) | 30% | 30% | 30% |
| Gross repayable-debt service + residual OPEX subsidy | $218 M / yr | $218 M / yr | **$188 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $218 M / yr | $218 M / yr | **$188 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 33,048 m² of station shop/kiosk leases at $10/m²/month and 6,056 advertising boards at $77/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kinshasa.toml`](kinshasa.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kinshasa-network-map.png`](kinshasa-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kinshasa.corridor.geojson`](kinshasa.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kinshasa.stations.json`](kinshasa.stations.json) | Machine-readable station list |
| [`kinshasa.design-quality.yaml`](kinshasa.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kinshasa

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kinshasa \
    --sidecar .cache/osr-pipeline/rasters/kinshasa.grid.json \
    --out-dir designs/.../Kinshasa

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kinshasa.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kinshasa.sh` chains steps 3 + drift tests into a single command.
