# Gazipur — Urban Rail Network

**Country:** BD · **Population:** 1,400,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Gazipur rail network on OpenStreetMap](gazipur-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`gazipur.corridor.geojson`](gazipur.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 127 |
| Interchange stations | 21 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 37.6% |
| Route length (double track) | 308.4 km |
| Revenue fleet | 368 × 4-car trainsets |
| Revenue fleet passenger capacity | 176,640 AW2 pax (235,520 AW3 crush) |
| Spare + cold-reserve | 40 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 46.1 km | 21 | 61 | N Outer ↔ S Mid |
| line-2 | 39.9 km | 19 | 53 | SE Outer ↔ NW Mid |
| line-3 | 51.4 km | 21 | 68 | NE Outer ↔ SW Outer |
| line-4 | 37.8 km | 15 | 51 | E Outer ↔ W Mid |
| line-5 | 35.9 km | 13 | 49 | NW Outer ↔ SE Mid |
| line-6 | 97.2 km | 38 | 126 | NW Mid ↔ W Mid |
| **Total** | **308.4 km** | **127 unique** | **408** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 176,640 AW2 pax (235,520 AW3 crush) |
| Total fleet capacity | 195,840 AW2 pax (261,120 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 368 × 480 = **176,640 AW2 passengers** (235,520 AW3 crush)
- **Total fleet passenger capacity:** 408 × 480 = **195,840 AW2 passengers** (261,120 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,152,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **921,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **168.2 – 269.1 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **1,400,000**
- Anchor-weighted coverage: 37.6%
- Catchment population: **≈ 526,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 21 | 500 kW | 3000 kWh |
| Major | 27 | 400 kW | 2500 kWh |
| Standard | 62 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **120** | **49,400 kW** | **321,500 kWh** |

Aggregate station-rail charging power: **66,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **562.1 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 822 kWh | 51.4 km average line length |
| Onboard battery coverage | 0.6× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 526 kW average charger across stops |
| Stops to refill one trainset pack | 55 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 247 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 2,691 MWh/day | 155,725 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 2,444 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 562.1 MW / 2,811 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 322 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (272.2 km @ $3.0 M/km) | $817 M |
| Elevated (32.4 km @ $12.0 M/km) | $389 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$1.25 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 7 | $600 k | $4.2 M |
| `standard` | 62 | $2.50 M | $155 M |
| `major` | 27 | $4.50 M | $122 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 21 | $12.0 M | $252 M |
| **Stations subtotal** | | | **$578 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 408 | $5.60 M | $2.28 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1632 | $100 k | $163 M |
| High sensitivity check | 1632 | $200 k | $326 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 562,103 kW @ $700/kW | $393 M |
| Grid interconnection / PPA tie-in | 562,103 kW @ $100/kW | $56 M |
| Annual generation proxy | 562.1 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,025.8 GWh/yr |
| **Dedicated solar plant subtotal** | | **$450 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 308.4 km × $0.050 M/km | $15 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $52 M |
| EPC integration + project management (7%) | on subtotal | $306 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.25 bn |
| Stations | $578 M |
| Depots | $30 M |
| Rolling stock | $2.28 bn |
| Railway production plant | $163 M |
| Dedicated solar power plant | $450 M |
| Residual train-control wayside + charging microgrids | $67 M |
| EPC overhead (7%) | $306 M |
| **CAPEX total** | **$5.13 bn** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $3,664 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh gazipur`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$229 M / yr** | $163 |
| Steady-state, low capacity-use (year 8+) | **$216 M / yr** | $154 |
| Steady-state, high capacity-use (year 8+) | **$163 M / yr** | $117 |
| Steady-state, operating-neutral revenue case | **$171 M / yr** | $122 |
| Lifecycle envelope (yr 1–40, low scenario) | **$8.73 bn cumulative** | $6,234 |
| Lifecycle envelope (yr 1–40, high scenario) | **$7.00 bn cumulative** | $4,997 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$7.25 bn cumulative** | $5,175 |

_Population basis: 1,400,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $45 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $7.6 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $4.10 bn | 2.0% | 40 y, 7 y grace | $171 M / yr |
| Government equity (no debt service) | 20% | $1.03 bn | — | — | — |
| **Total** | **100%** | **$5.13 bn** | | | **$171 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $82 M / yr = **$82 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($147 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $91 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $37 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $761 k |
| Traction energy (982.2 GWh / yr) | 155,725 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 90.2 GWh/yr + dedicated solar plant 562.1 MW / 1025.8 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $6.7 M |
| Labour (1,448 FTE) | driverless roster: OCC/remote 219, station/platform 455, passenger service 107, fleet maintenance 328, infrastructure/energy 285, admin/training 54; no train drivers × country median × 12 × engineer-premium 1.4 | $4.7 M |
| **OPEX subtotal** | | **$141 M / yr** |

_Annual service work: 155,725 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 61.4 M train-km / yr (245.5 M car-km / yr). On-site PV covers 90.2 GWh/yr and the dedicated solar plant adds 1025.8 GWh/yr against 982.2 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$195 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.52 |
| Day pass (3 trips) | $1.33 (15 % bulk discount) |
| Monthly unlimited pass | $15.60 (~8 % of median monthly income) |
| Annual pass | $171.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (921,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 76% |
| Annual paid trips | 168.2 M | 269.1 M | 254.5 M |
| Annual paid trips / city resident | 120 | 192 | 182 |
| Farebox revenue | $87 M / yr | $140 M / yr | $132 M / yr |
| Station shop leases | $3.3 M / yr | $3.3 M / yr | $3.3 M / yr |
| Advertising boards | $5.2 M / yr | $5.2 M / yr | $5.2 M / yr |
| **Total revenue** | **$96 M / yr** | **$148 M / yr** | **$141 M / yr** |
| Revenue / OPEX recovery | 68% | 105% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Gross repayable-debt service + residual OPEX subsidy | $216 M / yr | $171 M / yr | **$171 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$7.6 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $216 M / yr | $163 M / yr | **$171 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $7.6 M / yr | $0 / yr |

_Commercial-revenue assumptions: 19,832 m² of station shop/kiosk leases at $16/m²/month and 3,724 advertising boards at $136/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $25 M / yr | $40 M / yr | 16 min/trip × $0.56/h value-of-time proxy |
| Avoided road congestion | $48 M / yr | $78 M / yr | 605 M - 969 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $8.7 M / yr | $14 M / yr | 109.0–174.4 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $24 M / yr | $39 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $52 M / yr | $84 M / yr | 21% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $27 M / yr | $43 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$186 M / yr** | **$297 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 10 education anchors | 33,069 trips/school day; 7.3 M access-events/yr | 52,911 trips/school day; 11.6 M access-events/yr |
| Healthcare | 12 healthcare anchors | 41,309 trips/day; 15.1 M access-events/yr | 66,095 trips/day; 24.1 M access-events/yr |
| Commerce | 58 major/terminal/interchange nodes | 95,825 trips/trading day; 31.6 M access-events/yr | 153,319 trips/trading day; 50.6 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 48,845 trips/activity day; 14.7 M access-events/yr | 78,152 trips/activity day; 23.4 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $2.66 bn | 52% of $5.13 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $4.25 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $608 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 283,968 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 168.2 M - 269.1 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`gazipur.toml`](gazipur.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`gazipur-network-map.png`](gazipur-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`gazipur.corridor.geojson`](gazipur.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`gazipur.stations.json`](gazipur.stations.json) | Machine-readable station list |
| [`gazipur.design-quality.yaml`](gazipur.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug gazipur

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug gazipur \
    --sidecar .cache/osr-pipeline/rasters/gazipur.grid.json \
    --out-dir designs/.../Gazipur

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../gazipur.toml \
    --out designs/.../README.md
```

`scripts/regenerate-gazipur.sh` chains steps 3 + drift tests into a single command.
