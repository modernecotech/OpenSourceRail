# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`sanaa.corridor.geojson`](sanaa.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 126 |
| Interchange stations | 32 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 78.0% |
| Route length (double track) | 260.8 km |
| Revenue fleet | 319 × 6-car trainsets |
| Revenue fleet passenger capacity | 229,680 AW2 pax (306,240 AW3 crush) |
| Spare + cold-reserve | 38 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.2 km | 17 | 56 | SE Outer ↔ NW Outer |
| line-2 | 28.8 km | 15 | 39 | S Mid ↔ N Outer |
| line-3 | 22.1 km | 10 | 31 | N Mid ↔ SW Mid |
| line-4 | 27.1 km | 13 | 37 | N Mid ↔ S Mid |
| line-5 | 27.1 km | 10 | 37 | SE Outer ↔ SW Inner |
| line-6 | 24.5 km | 12 | 34 | E Inner ↔ W Outer |
| line-7 | 20.6 km | 9 | 29 | NW Mid ↔ E Mid |
| line-8 | 17.2 km | 11 | 25 | SW Mid ↔ NE Inner |
| line-9 | 52.3 km | 29 | 69 | NW Mid ↔ W Inner |
| **Total** | **260.8 km** | **126 unique** | **357** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 229,680 AW2 pax (306,240 AW3 crush) |
| Total fleet capacity | 257,040 AW2 pax (342,720 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 319 × 720 = **229,680 AW2 passengers** (306,240 AW3 crush)
- **Total fleet passenger capacity:** 357 × 720 = **257,040 AW2 passengers** (342,720 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 14,400 = **259,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,592,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **2,073,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **378.4 – 605.5 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **3,937,500**
- Anchor-weighted coverage: 78.0%
- Catchment population: **≈ 3,071,250** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 32 | 500 kW | 3000 kWh |
| Major | 34 | 400 kW | 2500 kWh |
| Standard | 36 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **118** | **52,900 kW** | **338,000 kWh** |

Aggregate station-rail charging power: **69,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **724.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 695 kWh | 29.0 km average line length |
| Onboard battery coverage | 1.0× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 548 kW average charger across stops |
| Stops to refill one trainset pack | 79 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 264 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 3,414 MWh/day | 131,726 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 3,150 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 724.5 MW / 3,622 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 338 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (239.4 km @ $3.0 M/km) | $718 M |
| Elevated (20.6 km @ $12.0 M/km) | $247 M |
| Elevated-interchange premium (19 sites @ $4.50 M) | $86 M |
| **Civil subtotal** | **$1.05 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 8 | $600 k | $4.8 M |
| `standard` | 36 | $2.50 M | $90 M |
| `major` | 34 | $4.50 M | $153 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 32 | $12.0 M | $384 M |
| **Stations subtotal** | | | **$704 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 357 | $8.40 M | $3.00 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 2142 | $100 k | $214 M |
| High sensitivity check | 2142 | $200 k | $428 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 724,460 kW @ $700/kW | $507 M |
| Grid interconnection / PPA tie-in | 724,460 kW @ $100/kW | $72 M |
| Annual generation proxy | 724.5 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,322.1 GWh/yr |
| **Dedicated solar plant subtotal** | | **$580 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 260.8 km × $0.050 M/km | $13 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $61 M |
| EPC integration + project management (7%) | on subtotal | $356 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.05 bn |
| Stations | $704 M |
| Depots | $42 M |
| Rolling stock | $3.00 bn |
| Railway production plant | $214 M |
| Dedicated solar power plant | $580 M |
| Residual train-control wayside + charging microgrids | $74 M |
| EPC overhead (7%) | $356 M |
| **CAPEX total** | **$6.02 bn** |
| Per-route-km | $23 M / km |
| Per-capita (city pop) | $1,529 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh sanaa`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$217 M / yr** | $55 |
| Steady-state, low capacity-use (year 11+) | **$296 M / yr** | $75 |
| Steady-state, high capacity-use (year 11+) | **$247 M / yr** | $63 |
| Steady-state, operating-neutral revenue case | **$215 M / yr** | $55 |
| Lifecycle envelope (yr 1–40, low scenario) | **$11.04 bn cumulative** | $2,803 |
| Lifecycle envelope (yr 1–40, high scenario) | **$9.58 bn cumulative** | $2,433 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$8.62 bn cumulative** | $2,188 |

_Population basis: 3,937,500 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $81 M / yr → $32 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $4.82 bn | 2.0% | 40 y, 10 y grace | $215 M / yr |
| Government equity (no debt service) | 20% | $1.20 bn | — | — | — |
| **Total** | **100%** | **$6.02 bn** | | | **$215 M / yr** |

_During the 10-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $96 M / yr = **$96 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($120 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $120 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $36 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $650 k |
| Traction energy (1246.2 GWh / yr) | 131,726 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 96.5 GWh/yr + dedicated solar plant 724.5 MW / 1322.1 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $8.7 M |
| Labour (1,604 FTE) | driverless roster: OCC/remote 207, station/platform 545, passenger service 215, fleet maintenance 281, infrastructure/energy 278, admin/training 78; no train drivers × country median × 12 × engineer-premium 1.4 | $2.2 M |
| **OPEX subtotal** | | **$167 M / yr** |

_Annual service work: 131,726 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 51.9 M train-km / yr (311.6 M car-km / yr). On-site PV covers 96.5 GWh/yr and the dedicated solar plant adds 1322.1 GWh/yr against 1246.2 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$80 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.21 |
| Day pass (3 trips) | $0.54 (15 % bulk discount) |
| Monthly unlimited pass | $6.40 (~8 % of median monthly income) |
| Annual pass | $70.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (2,073,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 100% |
| Annual paid trips | 378.4 M | 605.5 M | 756.2 M |
| Annual paid trips / city resident | 96 | 154 | 192 |
| Farebox revenue | $81 M / yr | $129 M / yr | $161 M / yr |
| Station shop leases | $2.6 M / yr | $2.6 M / yr | $2.6 M / yr |
| Advertising boards | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| **Total revenue** | **$87 M / yr** | **$135 M / yr** | **$167 M / yr** |
| Revenue / OPEX recovery | 52% | 81% | 100% |
| Country farebox-only policy target (diagnostic) | 25% | 25% | 25% |
| Gross repayable-debt service + residual OPEX subsidy | $296 M / yr | $247 M / yr | **$215 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $296 M / yr | $247 M / yr | **$215 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 24,744 m² of station shop/kiosk leases at $10/m²/month and 4,508 advertising boards at $75/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $23 M / yr | $37 M / yr | 16 min/trip × $0.23/h value-of-time proxy |
| Avoided road congestion | $109 M / yr | $174 M / yr | 1,362 M - 2,180 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $20 M / yr | $31 M / yr | 245.2–392.4 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $54 M / yr | $87 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $130 M / yr | $207 M / yr | 23% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $60 M / yr | $96 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$396 M / yr** | **$634 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 7 education anchors | 51,651 trips/school day; 11.4 M access-events/yr | 82,642 trips/school day; 18.2 M access-events/yr |
| Healthcare | 22 healthcare anchors | 87,091 trips/day; 31.8 M access-events/yr | 139,346 trips/day; 50.9 M access-events/yr |
| Commerce | 82 major/terminal/interchange nodes | 236,736 trips/trading day; 78.1 M access-events/yr | 378,778 trips/trading day; 125.0 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 109,901 trips/activity day; 33.0 M access-events/yr | 175,841 trips/activity day; 52.8 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $3.04 bn | 51% of $6.02 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $4.86 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $486 M / yr | spread across 10 construction / grace years |
| Construction employment supported | 791,774 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 378.4 M - 605.5 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`sanaa-network-map.png`](sanaa-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`sanaa.stations.json`](sanaa.stations.json) | Machine-readable station list |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug sanaa

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug sanaa \
    --sidecar .cache/osr-pipeline/rasters/sanaa.grid.json \
    --out-dir designs/.../Sanaa

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../sanaa.toml \
    --out designs/.../README.md
```

`scripts/regenerate-sanaa.sh` chains steps 3 + drift tests into a single command.
