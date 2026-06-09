# San-Salvador — Urban Rail Network

**Country:** SV · **Population:** 1,800,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![San-Salvador rail network on OpenStreetMap](san-salvador-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`san-salvador.corridor.geojson`](san-salvador.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 120 |
| Interchange stations | 20 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 50.5% |
| Route length (double track) | 254.7 km |
| Revenue fleet | 305 × 4-car trainsets |
| Revenue fleet passenger capacity | 146,400 AW2 pax (195,200 AW3 crush) |
| Spare + cold-reserve | 34 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 37.3 km | 21 | 50 | E Outer ↔ W Outer |
| line-2 | 36.4 km | 19 | 49 | SW Outer ↔ N Outer |
| line-3 | 41.0 km | 19 | 54 | NW Outer ↔ SE Outer |
| line-4 | 24.3 km | 15 | 34 | E Mid ↔ SW Outer |
| line-5 | 42.4 km | 15 | 57 | NE Outer ↔ S Outer |
| line-6 | 73.3 km | 32 | 95 | NW Mid ↔ NW Mid |
| **Total** | **254.7 km** | **120 unique** | **339** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 146,400 AW2 pax (195,200 AW3 crush) |
| Total fleet capacity | 162,720 AW2 pax (216,960 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 305 × 480 = **146,400 AW2 passengers** (195,200 AW3 crush)
- **Total fleet passenger capacity:** 339 × 480 = **162,720 AW2 passengers** (216,960 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,152,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **921,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **454,500 – 818,100 paid trips/day** (227,250 – 409,050 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **1,800,000**
- Anchor-weighted coverage: 50.5%
- Catchment population: **≈ 909,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 20 | 500 kW | 3000 kWh |
| Major | 58 | 400 kW | 2500 kWh |
| Standard | 23 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **111** | **49,600 kW** | **318,000 kWh** |

Aggregate station-rail charging power: **63,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **454.1 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 679 kWh | 42.4 km average line length |
| Onboard battery coverage | 0.7× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 525 kW average charger across stops |
| Stops to refill one trainset pack | 55 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 248 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 2,222 MWh/day | 128,611 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,974 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 454.1 MW / 2,271 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 318 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (240.8 km @ $3.0 M/km) | $722 M |
| Elevated (12.6 km @ $12.0 M/km) | $152 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$919 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 10 | $600 k | $6.0 M |
| `standard` | 23 | $2.50 M | $58 M |
| `major` | 58 | $4.50 M | $261 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 20 | $12.0 M | $240 M |
| **Stations subtotal** | | | **$610 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 339 | $5.60 M | $1.90 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1356 | $100 k | $136 M |
| High sensitivity check | 1356 | $200 k | $271 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 454,112 kW @ $700/kW | $318 M |
| Grid interconnection / PPA tie-in | 454,112 kW @ $100/kW | $45 M |
| Annual generation proxy | 454.1 MW × 5.0 peak-sun-h/day × 365 d/yr | 828.8 GWh/yr |
| **Dedicated solar plant subtotal** | | **$363 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 254.7 km × $0.050 M/km | $13 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $56 M |
| EPC integration + project management (7%) | on subtotal | $256 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $919 M |
| Stations | $610 M |
| Depots | $30 M |
| Rolling stock | $1.90 bn |
| Railway production plant | $136 M |
| Dedicated solar power plant | $363 M |
| Residual train-control wayside + charging microgrids | $68 M |
| EPC overhead (7%) | $256 M |
| **CAPEX total** | **$4.28 bn** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $2,378 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh san-salvador`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$128 M / yr** | $71 |
| Steady-state, low-ridership (year 6+) | **$56 M / yr** | $31 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$86 M / yr** | $48 |
| Lifecycle envelope (yr 1–40, low scenario) | **$2.60 bn cumulative** | $1,446 |
| Lifecycle envelope (yr 1–40, high scenario) | **$642 M cumulative** | $357 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$3.64 bn cumulative** | $2,022 |

_Population basis: 1,800,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $30 M / yr → $86 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.71 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $2.14 bn | 2.0% | 40 y, 5 y grace | $86 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 11.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $428 M | — | — | — |
| **Total** | **100%** | **$4.28 bn** | | | **$86 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $43 M / yr + fallback bonds $0 k / yr = **$43 M / yr** total. The $1.71 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($86 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $76 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $31 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $634 k |
| Traction energy (811.2 GWh / yr) | 128,611 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 90.5 GWh/yr + dedicated solar plant 454.1 MW / 828.8 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $5.4 M |
| Labour (1,376 FTE) | driverless roster: OCC/remote 191, station/platform 497, passenger service 115, fleet maintenance 271, infrastructure/energy 248, admin/training 54; no train drivers × country median × 12 × engineer-premium 1.4 | $7.1 M |
| **OPEX subtotal** | | **$120 M / yr** |

_Annual service work: 128,611 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 50.7 M train-km / yr (202.8 M car-km / yr). On-site PV covers 90.5 GWh/yr and the dedicated solar plant adds 828.8 GWh/yr against 811.2 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$305 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.81 |
| Day pass (3 trips) | $2.07 (15 % bulk discount) |
| Monthly unlimited pass | $24.40 (~8 % of median monthly income) |
| Annual pass | $268.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (921,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 227,250 | 409,050 | 177,343 |
| Daily active riders / catchment | 25% | 45% | 20% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 454,500 | 818,100 | 354,686 |
| Daily paid trips / city population | 25% | 45% | 20% |
| Annual paid trips | 165.9 M | 298.6 M | 129.5 M |
| Farebox revenue | $135 M / yr | $243 M / yr | $105 M / yr |
| Station shop leases | $5.9 M / yr | $5.9 M / yr | $5.9 M / yr |
| Advertising boards | $9.1 M / yr | $9.1 M / yr | $9.1 M / yr |
| **Total revenue** | **$150 M / yr** | **$258 M / yr** | **$120 M / yr** |
| Revenue / OPEX recovery | 125% | 214% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $86 M / yr | $86 M / yr | **$86 M / yr** |
| Operating surplus applied to debt support | -$30 M / yr | -$86 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $56 M / yr | $0 k / yr | **$86 M / yr** |
| Operating surplus after OPEX (before debt support) | $30 M / yr | $138 M / yr | $0 / yr |

_Commercial-revenue assumptions: 22,864 m² of station shop/kiosk leases at $24/m²/month and 4,164 advertising boards at $214/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`san-salvador.toml`](san-salvador.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`san-salvador-network-map.png`](san-salvador-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`san-salvador.corridor.geojson`](san-salvador.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`san-salvador.stations.json`](san-salvador.stations.json) | Machine-readable station list |
| [`san-salvador.design-quality.yaml`](san-salvador.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug san-salvador

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug san-salvador \
    --sidecar .cache/osr-pipeline/rasters/san-salvador.grid.json \
    --out-dir designs/.../San-Salvador

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../san-salvador.toml \
    --out designs/.../README.md
```

`scripts/regenerate-san-salvador.sh` chains steps 3 + drift tests into a single command.
