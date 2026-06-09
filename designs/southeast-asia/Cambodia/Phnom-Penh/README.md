# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 106 |
| Interchange stations | 23 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 48.3% |
| Route length (double track) | 227.7 km |
| Revenue fleet | 276 × 4-car trainsets |
| Revenue fleet passenger capacity | 132,480 AW2 pax (176,640 AW3 crush) |
| Spare + cold-reserve | 31 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 38.6 km | 18 | 52 | SE Outer ↔ N Outer |
| line-2 | 31.4 km | 16 | 42 | E Outer ↔ W Mid |
| line-3 | 28.1 km | 11 | 39 | N Mid ↔ SW Mid |
| line-4 | 25.9 km | 15 | 36 | SW Mid ↔ NE Mid |
| line-5 | 41.2 km | 18 | 56 | NW Outer ↔ SE Outer |
| line-6 | 62.4 km | 29 | 82 | W Mid ↔ W Mid |
| **Total** | **227.7 km** | **106 unique** | **307** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 132,480 AW2 pax (176,640 AW3 crush) |
| Total fleet capacity | 147,360 AW2 pax (196,480 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 276 × 480 = **132,480 AW2 passengers** (176,640 AW3 crush)
- **Total fleet passenger capacity:** 307 × 480 = **147,360 AW2 passengers** (196,480 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,152,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **921,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **168.2 – 269.1 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **2,281,000**
- Anchor-weighted coverage: 48.3%
- Catchment population: **≈ 1,101,723** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 23 | 500 kW | 3000 kWh |
| Major | 25 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **104** | **44,800 kW** | **290,500 kWh** |

Aggregate station-rail charging power: **57,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **405.4 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 607 kWh | 37.9 km average line length |
| Onboard battery coverage | 0.8× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 545 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 224 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,987 MWh/day | 114,972 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,763 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 405.4 MW / 2,027 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 290 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (186.2 km @ $3.0 M/km) | $558 M |
| Elevated (40.2 km @ $12.0 M/km) | $483 M |
| Elevated-interchange premium (8 sites @ $4.50 M) | $36 M |
| **Civil subtotal** | **$1.08 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $600 k | $1.8 M |
| `standard` | 46 | $2.50 M | $115 M |
| `major` | 25 | $4.50 M | $112 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 10 | $8.0 M | $80 M |
| `interchange-elevated` | 13 | $12.0 M | $156 M |
| **Stations subtotal** | | | **$511 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 307 | $5.60 M | $1.72 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1228 | $100 k | $123 M |
| High sensitivity check | 1228 | $200 k | $246 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 405,424 kW @ $700/kW | $284 M |
| Grid interconnection / PPA tie-in | 405,424 kW @ $100/kW | $41 M |
| Annual generation proxy | 405.4 MW × 5.0 peak-sun-h/day × 365 d/yr | 739.9 GWh/yr |
| **Dedicated solar plant subtotal** | | **$324 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 227.7 km × $0.050 M/km | $11 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $47 M |
| EPC integration + project management (7%) | on subtotal | $246 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.08 bn |
| Stations | $511 M |
| Depots | $30 M |
| Rolling stock | $1.72 bn |
| Railway production plant | $123 M |
| Dedicated solar power plant | $324 M |
| Residual train-control wayside + charging microgrids | $58 M |
| EPC overhead (7%) | $246 M |
| **CAPEX total** | **$4.09 bn** |
| Per-route-km | $18 M / km |
| Per-capita (city pop) | $1,792 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh phnom-penh`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$182 M / yr** | $80 |
| Steady-state, low capacity-use (year 8+) | **$142 M / yr** | $62 |
| Steady-state, high capacity-use (year 8+) | **$84 M / yr** | $37 |
| Steady-state, operating-neutral revenue case | **$136 M / yr** | $60 |
| Lifecycle envelope (yr 1–40, low scenario) | **$5.97 bn cumulative** | $2,618 |
| Lifecycle envelope (yr 1–40, high scenario) | **$4.06 bn cumulative** | $1,781 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$5.78 bn cumulative** | $2,532 |

_Population basis: 2,281,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $6.0 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $52 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $3.27 bn | 2.0% | 40 y, 7 y grace | $136 M / yr |
| Government equity (no debt service) | 20% | $818 M | — | — | — |
| **Total** | **100%** | **$4.09 bn** | | | **$136 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $65 M / yr = **$65 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($117 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $69 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $32 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $566 k |
| Traction energy (725.2 GWh / yr) | 114,972 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 81.8 GWh/yr + dedicated solar plant 405.4 MW / 739.9 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $4.9 M |
| Labour (1,233 FTE) | driverless roster: OCC/remote 175, station/platform 427, passenger service 107, fleet maintenance 244, infrastructure/energy 226, admin/training 54; no train drivers × country median × 12 × engineer-premium 1.4 | $4.5 M |
| **OPEX subtotal** | | **$111 M / yr** |

_Annual service work: 114,972 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 45.3 M train-km / yr (181.3 M car-km / yr). On-site PV covers 81.8 GWh/yr and the dedicated solar plant adds 739.9 GWh/yr against 725.2 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$215 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.57 |
| Day pass (3 trips) | $1.46 (15 % bulk discount) |
| Monthly unlimited pass | $17.20 (~8 % of median monthly income) |
| Annual pass | $189.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (921,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 53% |
| Annual paid trips | 168.2 M | 269.1 M | 178.6 M |
| Annual paid trips / city resident | 74 | 118 | 78 |
| Farebox revenue | $96 M / yr | $154 M / yr | $102 M / yr |
| Station shop leases | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| Advertising boards | $5.3 M / yr | $5.3 M / yr | $5.3 M / yr |
| **Total revenue** | **$105 M / yr** | **$163 M / yr** | **$111 M / yr** |
| Revenue / OPEX recovery | 95% | 147% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $142 M / yr | $136 M / yr | **$136 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$52 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $142 M / yr | $84 M / yr | **$136 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $52 M / yr | $0 / yr |

_Commercial-revenue assumptions: 18,536 m² of station shop/kiosk leases at $17/m²/month and 3,428 advertising boards at $150/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $28 M / yr | $45 M / yr | 16 min/trip × $0.62/h value-of-time proxy |
| Avoided road congestion | $48 M / yr | $78 M / yr | 605 M - 969 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $8.7 M / yr | $14 M / yr | 109.0–174.4 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $24 M / yr | $39 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $55 M / yr | $88 M / yr | 22% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $27 M / yr | $43 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$191 M / yr** | **$305 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 11 education anchors | 28,960 trips/school day; 6.4 M access-events/yr | 46,335 trips/school day; 10.2 M access-events/yr |
| Healthcare | 13 healthcare anchors | 37,325 trips/day; 13.6 M access-events/yr | 59,720 trips/day; 21.8 M access-events/yr |
| Commerce | 58 major/terminal/interchange nodes | 100,202 trips/trading day; 33.1 M access-events/yr | 160,324 trips/trading day; 52.9 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 48,845 trips/activity day; 14.7 M access-events/yr | 78,152 trips/activity day; 23.4 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $2.15 bn | 52% of $4.09 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $3.43 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $491 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 207,988 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 168.2 M - 269.1 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`phnom-penh-network-map.png`](phnom-penh-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`phnom-penh.stations.json`](phnom-penh.stations.json) | Machine-readable station list |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug phnom-penh

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug phnom-penh \
    --sidecar .cache/osr-pipeline/rasters/phnom-penh.grid.json \
    --out-dir designs/.../Phnom-Penh

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../phnom-penh.toml \
    --out designs/.../README.md
```

`scripts/regenerate-phnom-penh.sh` chains steps 3 + drift tests into a single command.
