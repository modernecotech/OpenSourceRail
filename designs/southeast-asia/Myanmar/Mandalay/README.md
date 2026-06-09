# Mandalay — Urban Rail Network

**Country:** MM · **Population:** 1,726,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Mandalay rail network on OpenStreetMap](mandalay-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`mandalay.corridor.geojson`](mandalay.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 87 |
| Interchange stations | 23 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 60.1% |
| Route length (double track) | 187.0 km |
| Revenue fleet | 227 × 4-car trainsets |
| Revenue fleet passenger capacity | 108,960 AW2 pax (145,280 AW3 crush) |
| Spare + cold-reserve | 27 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 42.7 km | 18 | 57 | N Outer ↔ S Mid |
| line-2 | 33.6 km | 14 | 46 | NE Mid ↔ SW Outer |
| line-3 | 25.4 km | 11 | 35 | N Mid ↔ SE Mid |
| line-4 | 27.9 km | 13 | 38 | E Mid ↔ SW Mid |
| line-5 | 19.0 km | 11 | 27 | SE Mid ↔ W Inner |
| line-6 | 38.4 km | 21 | 51 | NE Inner ↔ NE Inner |
| **Total** | **187.0 km** | **87 unique** | **254** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 108,960 AW2 pax (145,280 AW3 crush) |
| Total fleet capacity | 121,920 AW2 pax (162,560 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 227 × 480 = **108,960 AW2 passengers** (145,280 AW3 crush)
- **Total fleet passenger capacity:** 254 × 480 = **121,920 AW2 passengers** (162,560 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,152,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **921,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **168.2 – 269.1 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **1,726,000**
- Anchor-weighted coverage: 60.1%
- Catchment population: **≈ 1,037,326** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 23 | 500 kW | 3000 kWh |
| Major | 18 | 400 kW | 2500 kWh |
| Standard | 31 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **82** | **37,500 kW** | **243,000 kWh** |

Aggregate station-rail charging power: **47,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **332.1 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 499 kWh | 31.2 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 546 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 188 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,631 MWh/day | 94,413 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,444 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 332.1 MW / 1,661 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 243 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (170.8 km @ $3.0 M/km) | $512 M |
| Elevated (14.7 km @ $12.0 M/km) | $176 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$734 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 6 | $600 k | $3.6 M |
| `standard` | 31 | $2.50 M | $78 M |
| `major` | 18 | $4.50 M | $81 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 23 | $12.0 M | $276 M |
| **Stations subtotal** | | | **$484 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 254 | $5.60 M | $1.42 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1016 | $100 k | $102 M |
| High sensitivity check | 1016 | $200 k | $203 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 332,110 kW @ $700/kW | $232 M |
| Grid interconnection / PPA tie-in | 332,110 kW @ $100/kW | $33 M |
| Annual generation proxy | 332.1 MW × 5.0 peak-sun-h/day × 365 d/yr | 606.1 GWh/yr |
| **Dedicated solar plant subtotal** | | **$266 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 187.0 km × $0.050 M/km | $9.3 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $42 M |
| EPC integration + project management (7%) | on subtotal | $198 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $734 M |
| Stations | $484 M |
| Depots | $30 M |
| Rolling stock | $1.42 bn |
| Railway production plant | $102 M |
| Dedicated solar power plant | $266 M |
| Residual train-control wayside + charging microgrids | $51 M |
| EPC overhead (7%) | $198 M |
| **CAPEX total** | **$3.29 bn** |
| Per-route-km | $18 M / km |
| Per-capita (city pop) | $1,903 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh mandalay`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$118 M / yr** | $69 |
| Steady-state, low capacity-use (year 11+) | **$143 M / yr** | $83 |
| Steady-state, high capacity-use (year 11+) | **$108 M / yr** | $63 |
| Steady-state, operating-neutral revenue case | **$117 M / yr** | $68 |
| Lifecycle envelope (yr 1–40, low scenario) | **$5.47 bn cumulative** | $3,172 |
| Lifecycle envelope (yr 1–40, high scenario) | **$4.42 bn cumulative** | $2,564 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$4.70 bn cumulative** | $2,725 |

_Population basis: 1,726,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $26 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $9.3 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $2.63 bn | 2.0% | 40 y, 10 y grace | $117 M / yr |
| Government equity (no debt service) | 20% | $657 M | — | — | — |
| **Total** | **100%** | **$3.29 bn** | | | **$117 M / yr** |

_During the 10-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $53 M / yr = **$53 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($66 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $57 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $25 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $464 k |
| Traction energy (595.5 GWh / yr) | 94,413 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 68.4 GWh/yr + dedicated solar plant 332.1 MW / 606.1 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $4.0 M |
| Labour (1,075 FTE) | driverless roster: OCC/remote 150, station/platform 371, passenger service 107, fleet maintenance 201, infrastructure/energy 192, admin/training 54; no train drivers × country median × 12 × engineer-premium 1.4 | $2.3 M |
| **OPEX subtotal** | | **$89 M / yr** |

_Annual service work: 94,413 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 37.2 M train-km / yr (148.9 M car-km / yr). On-site PV covers 68.4 GWh/yr and the dedicated solar plant adds 606.1 GWh/yr against 595.5 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$130 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.35 |
| Day pass (3 trips) | $0.88 (15 % bulk discount) |
| Monthly unlimited pass | $10.40 (~8 % of median monthly income) |
| Annual pass | $114.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (921,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 72% |
| Annual paid trips | 168.2 M | 269.1 M | 242.3 M |
| Annual paid trips / city resident | 97 | 156 | 140 |
| Farebox revenue | $58 M / yr | $93 M / yr | $84 M / yr |
| Station shop leases | $1.8 M / yr | $1.8 M / yr | $1.8 M / yr |
| Advertising boards | $2.8 M / yr | $2.8 M / yr | $2.8 M / yr |
| **Total revenue** | **$63 M / yr** | **$98 M / yr** | **$89 M / yr** |
| Revenue / OPEX recovery | 71% | 110% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $143 M / yr | $117 M / yr | **$117 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$9.3 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $143 M / yr | $108 M / yr | **$117 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $9.3 M / yr | $0 / yr |

_Commercial-revenue assumptions: 16,560 m² of station shop/kiosk leases at $10/m²/month and 3,028 advertising boards at $91/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $17 M / yr | $27 M / yr | 16 min/trip × $0.38/h value-of-time proxy |
| Avoided road congestion | $48 M / yr | $78 M / yr | 605 M - 969 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $8.7 M / yr | $14 M / yr | 109.0–174.4 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $24 M / yr | $39 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $56 M / yr | $89 M / yr | 22% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $27 M / yr | $43 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$181 M / yr** | **$289 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 7 education anchors | 27,141 trips/school day; 6.0 M access-events/yr | 43,426 trips/school day; 9.6 M access-events/yr |
| Healthcare | 9 healthcare anchors | 36,357 trips/day; 13.3 M access-events/yr | 58,171 trips/day; 21.2 M access-events/yr |
| Commerce | 51 major/terminal/interchange nodes | 102,091 trips/trading day; 33.7 M access-events/yr | 163,346 trips/trading day; 53.9 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 48,845 trips/activity day; 14.7 M access-events/yr | 78,152 trips/activity day; 23.4 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $1.71 bn | 52% of $3.29 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $2.74 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $274 M / yr | spread across 10 construction / grace years |
| Construction employment supported | 274,070 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 168.2 M - 269.1 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`mandalay.toml`](mandalay.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`mandalay-network-map.png`](mandalay-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`mandalay.corridor.geojson`](mandalay.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`mandalay.stations.json`](mandalay.stations.json) | Machine-readable station list |
| [`mandalay.design-quality.yaml`](mandalay.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug mandalay

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug mandalay \
    --sidecar .cache/osr-pipeline/rasters/mandalay.grid.json \
    --out-dir designs/.../Mandalay

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../mandalay.toml \
    --out designs/.../README.md
```

`scripts/regenerate-mandalay.sh` chains steps 3 + drift tests into a single command.
