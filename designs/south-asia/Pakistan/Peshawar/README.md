# Peshawar — Urban Rail Network

**Country:** PK · **Population:** 2,300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Peshawar rail network on OpenStreetMap](peshawar-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`peshawar.corridor.geojson`](peshawar.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 86 |
| Interchange stations | 10 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 32.8% |
| Route length (double track) | 196.7 km |
| Revenue fleet | 235 × 4-car trainsets |
| Revenue fleet passenger capacity | 112,800 AW2 pax (150,400 AW3 crush) |
| Spare + cold-reserve | 26 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 50.4 km | 22 | 67 | NE Outer ↔ SW Outer |
| line-2 | 33.5 km | 21 | 46 | W Mid ↔ E Outer |
| line-3 | 38.6 km | 15 | 52 | S Mid ↔ NW Outer |
| line-4 | 74.2 km | 29 | 96 | W Mid ↔ W Mid |
| **Total** | **196.7 km** | **86 unique** | **261** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 112,800 AW2 pax (150,400 AW3 crush) |
| Total fleet capacity | 125,280 AW2 pax (167,040 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 235 × 480 = **112,800 AW2 passengers** (150,400 AW3 crush)
- **Total fleet passenger capacity:** 261 × 480 = **125,280 AW2 passengers** (167,040 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 9,600 = **76,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **768,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **614,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **377,200 – 614,400 paid trips/day** (188,600 – 307,200 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **2,300,000**
- Anchor-weighted coverage: 32.8%
- Catchment population: **≈ 754,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 10 | 500 kW | 3000 kWh |
| Major | 27 | 400 kW | 2500 kWh |
| Standard | 41 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **84** | **35,600 kW** | **234,500 kWh** |

Aggregate station-rail charging power: **45,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **353.9 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 787 kWh | 49.2 km average line length |
| Onboard battery coverage | 0.6× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 532 kW average charger across stops |
| Stops to refill one trainset pack | 54 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 178 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,717 MWh/day | 99,349 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,539 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 353.9 MW / 1,770 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 234 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (167.1 km @ $3.0 M/km) | $501 M |
| Elevated (28.7 km @ $12.0 M/km) | $344 M |
| Elevated-interchange premium (6 sites @ $4.50 M) | $27 M |
| **Civil subtotal** | **$873 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $600 k | $1.8 M |
| `standard` | 41 | $2.50 M | $102 M |
| `major` | 27 | $4.50 M | $122 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 10 | $12.0 M | $120 M |
| **Stations subtotal** | | | **$373 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 261 | $5.60 M | $1.46 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1044 | $100 k | $104 M |
| High sensitivity check | 1044 | $200 k | $209 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 353,914 kW @ $700/kW | $248 M |
| Grid interconnection / PPA tie-in | 353,914 kW @ $100/kW | $35 M |
| Annual generation proxy | 353.9 MW × 5.0 peak-sun-h/day × 365 d/yr | 645.9 GWh/yr |
| **Dedicated solar plant subtotal** | | **$283 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 196.7 km × $0.050 M/km | $9.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $35 M |
| EPC integration + project management (7%) | on subtotal | $201 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $873 M |
| Stations | $373 M |
| Depots | $22 M |
| Rolling stock | $1.46 bn |
| Railway production plant | $104 M |
| Dedicated solar power plant | $283 M |
| Residual train-control wayside + charging microgrids | $45 M |
| EPC overhead (7%) | $201 M |
| **CAPEX total** | **$3.36 bn** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $1,462 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh peshawar`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$82 M / yr** | $36 |
| Steady-state, low-ridership (year 8+) | **$96 M / yr** | $42 |
| Steady-state, high-ridership (year 8+) | **$58 M / yr** | $25 |
| Steady-state, operating-neutral revenue case | **$70 M / yr** | $30 |
| Lifecycle envelope (yr 1–40, low scenario) | **$3.74 bn cumulative** | $1,625 |
| Lifecycle envelope (yr 1–40, high scenario) | **$2.48 bn cumulative** | $1,078 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.88 bn cumulative** | $1,254 |

_Population basis: 2,300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $26 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $12 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.35 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $1.68 bn | 2.0% | 40 y, 7 y grace | $70 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 16.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $336 M | — | — | — |
| **Total** | **100%** | **$3.36 bn** | | | **$70 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $34 M / yr + fallback bonds $0 k / yr = **$34 M / yr** total. The $1.35 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($48 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $58 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $25 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $489 k |
| Traction energy (626.6 GWh / yr) | 99,349 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 65.0 GWh/yr + dedicated solar plant 353.9 MW / 645.9 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $4.2 M |
| Labour (962 FTE) | driverless roster: OCC/remote 146, station/platform 303, passenger service 84, fleet maintenance 209, infrastructure/energy 182, admin/training 38; no train drivers × country median × 12 × engineer-premium 1.4 | $2.7 M |
| **OPEX subtotal** | | **$91 M / yr** |

_Annual service work: 99,349 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 39.2 M train-km / yr (156.7 M car-km / yr). On-site PV covers 65.0 GWh/yr and the dedicated solar plant adds 645.9 GWh/yr against 626.6 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.44 |
| Day pass (3 trips) | $1.12 (15 % bulk discount) |
| Monthly unlimited pass | $13.20 (~8 % of median monthly income) |
| Annual pass | $145.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (614,400 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 188,600 | 307,200 | 269,040 |
| Daily active riders / catchment | 25% | 41% | 36% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 377,200 | 614,400 | 538,080 |
| Daily paid trips / city population | 16% | 27% | 23% |
| Annual paid trips | 137.7 M | 224.3 M | 196.4 M |
| Farebox revenue | $61 M / yr | $99 M / yr | $86 M / yr |
| Station shop leases | $1.9 M / yr | $1.9 M / yr | $1.9 M / yr |
| Advertising boards | $3.0 M / yr | $3.0 M / yr | $3.0 M / yr |
| **Total revenue** | **$65 M / yr** | **$103 M / yr** | **$91 M / yr** |
| Revenue / OPEX recovery | 72% | 113% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $96 M / yr | $70 M / yr | **$70 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$12 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $96 M / yr | $58 M / yr | **$70 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $12 M / yr | $0 / yr |

_Commercial-revenue assumptions: 13,296 m² of station shop/kiosk leases at $13/m²/month and 2,508 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`peshawar.toml`](peshawar.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`peshawar-network-map.png`](peshawar-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`peshawar.corridor.geojson`](peshawar.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`peshawar.stations.json`](peshawar.stations.json) | Machine-readable station list |
| [`peshawar.design-quality.yaml`](peshawar.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug peshawar

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug peshawar \
    --sidecar .cache/osr-pipeline/rasters/peshawar.grid.json \
    --out-dir designs/.../Peshawar

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../peshawar.toml \
    --out designs/.../README.md
```

`scripts/regenerate-peshawar.sh` chains steps 3 + drift tests into a single command.
