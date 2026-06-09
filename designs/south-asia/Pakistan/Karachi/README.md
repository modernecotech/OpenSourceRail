# Karachi — Urban Rail Network

**Country:** PK · **Population:** 20,300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Karachi rail network on OpenStreetMap](karachi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`karachi.corridor.geojson`](karachi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 231 |
| Interchange stations | 33 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 48.4% |
| Route length (double track) | 472.3 km |
| Revenue fleet | 561 × 6-car trainsets |
| Revenue fleet passenger capacity | 403,920 AW2 pax (538,560 AW3 crush) |
| Spare + cold-reserve | 61 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 57.8 km | 27 | 76 | NW Outer ↔ E Outer |
| line-2 | 47.2 km | 25 | 62 | W Outer ↔ SE Mid |
| line-3 | 45.5 km | 23 | 61 | N Outer ↔ SW Mid |
| line-4 | 46.3 km | 21 | 61 | E Mid ↔ W Outer |
| line-5 | 46.2 km | 25 | 61 | NE Outer ↔ S Mid |
| line-6 | 46.1 km | 24 | 61 | N Outer ↔ S Mid |
| line-7 | 37.4 km | 19 | 50 | W Mid ↔ E Outer |
| line-8 | 41.7 km | 16 | 56 | NE Outer ↔ SE Mid |
| line-9 | 104.1 km | 51 | 134 | NW Mid ↔ NW Mid |
| **Total** | **472.3 km** | **231 unique** | **622** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 403,920 AW2 pax (538,560 AW3 crush) |
| Total fleet capacity | 447,840 AW2 pax (597,120 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 561 × 720 = **403,920 AW2 passengers** (538,560 AW3 crush)
- **Total fleet passenger capacity:** 622 × 720 = **447,840 AW2 passengers** (597,120 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 14,400 = **259,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,592,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **2,073,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **2,073,600 – 2,073,600 paid trips/day** (1,036,800 – 1,036,800 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **20,300,000**
- Anchor-weighted coverage: 48.4%
- Catchment population: **≈ 9,825,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 33 | 500 kW | 3000 kWh |
| Major | 94 | 400 kW | 2500 kWh |
| Standard | 83 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **226** | **91,500 kW** | **585,000 kWh** |

Aggregate station-rail charging power: **122,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,316.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,259 kWh | 52.5 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 529 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 458 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 6,182 MWh/day | 238,487 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 5,724 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,316.5 MW / 6,583 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 585 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (435.6 km @ $3.0 M/km) | $1.31 bn |
| Elevated (34.7 km @ $12.0 M/km) | $416 M |
| Elevated-interchange premium (25 sites @ $4.50 M) | $112 M |
| **Civil subtotal** | **$1.84 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 5 | $600 k | $3.0 M |
| `standard` | 83 | $2.50 M | $208 M |
| `major` | 94 | $4.50 M | $423 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 33 | $12.0 M | $396 M |
| **Stations subtotal** | | | **$1.10 bn** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 15 | $2.0 M | $30 M |
| **Depots subtotal** | | | **$42 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 622 | $8.40 M | $5.22 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 3732 | $100 k | $373 M |
| High sensitivity check | 3732 | $200 k | $746 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,316,536 kW @ $700/kW | $922 M |
| Grid interconnection / PPA tie-in | 1,316,536 kW @ $100/kW | $132 M |
| Annual generation proxy | 1,316.5 MW × 5.0 peak-sun-h/day × 365 d/yr | 2,402.7 GWh/yr |
| **Dedicated solar plant subtotal** | | **$1.05 bn** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 472.3 km × $0.050 M/km | $24 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $100 M |
| EPC integration + project management (7%) | on subtotal | $609 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.84 bn |
| Stations | $1.10 bn |
| Depots | $42 M |
| Rolling stock | $5.22 bn |
| Railway production plant | $373 M |
| Dedicated solar power plant | $1.05 bn |
| Residual train-control wayside + charging microgrids | $124 M |
| EPC overhead (7%) | $609 M |
| **CAPEX total** | **$10.36 bn** |
| Per-route-km | $22 M / km |
| Per-capita (city pop) | $511 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh karachi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$252 M / yr** | $12 |
| Steady-state, low-ridership (year 8+) | **$161 M / yr** | $8 |
| Steady-state, high-ridership (year 8+) | **$161 M / yr** | $8 |
| Steady-state, operating-neutral revenue case | **$216 M / yr** | $11 |
| Lifecycle envelope (yr 1–40, low scenario) | **$7.08 bn cumulative** | $349 |
| Lifecycle envelope (yr 1–40, high scenario) | **$7.08 bn cumulative** | $349 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$8.89 bn cumulative** | $438 |

_Population basis: 20,300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $55 M / yr → $55 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $4.15 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $5.18 bn | 2.0% | 40 y, 7 y grace | $216 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 16.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $1.04 bn | — | — | — |
| **Total** | **100%** | **$10.36 bn** | | | **$216 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $104 M / yr + fallback bonds $0 k / yr = **$104 M / yr** total. The $4.15 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($148 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $209 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $60 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.2 M |
| Traction energy (2256.3 GWh / yr) | 238,487 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 167.0 GWh/yr + dedicated solar plant 1316.5 MW / 2402.7 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $16 M |
| Labour (2,507 FTE) | driverless roster: OCC/remote 333, station/platform 888, passenger service 256, fleet maintenance 500, infrastructure/energy 452, admin/training 78; no train drivers × country median × 12 × engineer-premium 1.4 | $6.9 M |
| **OPEX subtotal** | | **$293 M / yr** |

_Annual service work: 238,487 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 94.0 M train-km / yr (564.1 M car-km / yr). On-site PV covers 167.0 GWh/yr and the dedicated solar plant adds 2402.7 GWh/yr against 2256.3 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.44 |
| Day pass (3 trips) | $1.12 (15 % bulk discount) |
| Monthly unlimited pass | $13.20 (~8 % of median monthly income) |
| Annual pass | $145.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (2,073,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 1,036,800 | 1,036,800 | 865,708 |
| Daily active riders / catchment | 11% | 11% | 9% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 2,073,600 | 2,073,600 | 1,731,416 |
| Daily paid trips / city population | 10% | 10% | 9% |
| Annual paid trips | 756.9 M | 756.9 M | 632.0 M |
| Farebox revenue | $333 M / yr | $333 M / yr | $278 M / yr |
| Station shop leases | $5.6 M / yr | $5.6 M / yr | $5.6 M / yr |
| Advertising boards | $8.8 M / yr | $8.8 M / yr | $8.8 M / yr |
| **Total revenue** | **$347 M / yr** | **$347 M / yr** | **$293 M / yr** |
| Revenue / OPEX recovery | 119% | 119% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $216 M / yr | $216 M / yr | **$216 M / yr** |
| Operating surplus applied to debt support | -$55 M / yr | -$55 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $161 M / yr | $161 M / yr | **$216 M / yr** |
| Operating surplus after OPEX (before debt support) | $55 M / yr | $55 M / yr | $0 / yr |

_Commercial-revenue assumptions: 40,488 m² of station shop/kiosk leases at $13/m²/month and 7,472 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`karachi.toml`](karachi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`karachi-network-map.png`](karachi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`karachi.corridor.geojson`](karachi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`karachi.stations.json`](karachi.stations.json) | Machine-readable station list |
| [`karachi.design-quality.yaml`](karachi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug karachi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug karachi \
    --sidecar .cache/osr-pipeline/rasters/karachi.grid.json \
    --out-dir designs/.../Karachi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../karachi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-karachi.sh` chains steps 3 + drift tests into a single command.
