# Tangier — Urban Rail Network

**Country:** MA · **Population:** 1,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Tangier rail network on OpenStreetMap](tangier-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`tangier.corridor.geojson`](tangier.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 63 |
| Interchange stations | 10 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.7% |
| Route length (double track) | 153.3 km |
| Revenue fleet | 188 × 4-car trainsets |
| Revenue fleet passenger capacity | 90,240 AW2 pax (120,320 AW3 crush) |
| Spare + cold-reserve | 21 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 20.7 km | 9 | 29 | E Mid ↔ W Mid |
| line-2 | 23.2 km | 10 | 32 | W Mid ↔ NE Outer |
| line-3 | 20.5 km | 9 | 29 | SW Outer ↔ E Mid |
| line-4 | 29.2 km | 11 | 40 | SE Outer ↔ NW Mid |
| line-5 | 59.7 km | 25 | 79 | NW Mid ↔ NW Mid |
| **Total** | **153.3 km** | **63 unique** | **209** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 90,240 AW2 pax (120,320 AW3 crush) |
| Total fleet capacity | 100,320 AW2 pax (133,760 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 188 × 480 = **90,240 AW2 passengers** (120,320 AW3 crush)
- **Total fleet passenger capacity:** 209 × 480 = **100,320 AW2 passengers** (133,760 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 9,600 = **96,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **960,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **768,000 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **140.2 – 224.3 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **1,200,000**
- Anchor-weighted coverage: 56.7%
- Catchment population: **≈ 680,399** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 10 | 500 kW | 3000 kWh |
| Major | 5 | 400 kW | 2500 kWh |
| Standard | 38 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **61** | **26,900 kW** | **179,500 kWh** |

Aggregate station-rail charging power: **35,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **276.8 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 491 kWh | 30.7 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.3 kWh/stop | 560 kW average charger across stops |
| Stops to refill one trainset pack | 51 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 134 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,338 MWh/day | 77,426 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,203 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 276.8 MW / 1,384 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 180 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (145.9 km @ $3.0 M/km) | $438 M |
| Elevated (7.0 km @ $12.0 M/km) | $84 M |
| Elevated-interchange premium (6 sites @ $4.50 M) | $27 M |
| **Civil subtotal** | **$549 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $600 k | $1.8 M |
| `standard` | 38 | $2.50 M | $95 M |
| `major` | 5 | $4.50 M | $22 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 10 | $12.0 M | $120 M |
| **Stations subtotal** | | | **$276 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 7 | $2.0 M | $14 M |
| **Depots subtotal** | | | **$26 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 209 | $5.60 M | $1.17 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 836 | $100 k | $84 M |
| High sensitivity check | 836 | $200 k | $167 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 276,786 kW @ $700/kW | $194 M |
| Grid interconnection / PPA tie-in | 276,786 kW @ $100/kW | $28 M |
| Annual generation proxy | 276.8 MW × 5.0 peak-sun-h/day × 365 d/yr | 505.1 GWh/yr |
| **Dedicated solar plant subtotal** | | **$221 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 153.3 km × $0.050 M/km | $7.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $25 M |
| EPC integration + project management (7%) | on subtotal | $150 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $549 M |
| Stations | $276 M |
| Depots | $26 M |
| Rolling stock | $1.17 bn |
| Railway production plant | $84 M |
| Dedicated solar power plant | $221 M |
| Residual train-control wayside + charging microgrids | $33 M |
| EPC overhead (7%) | $150 M |
| **CAPEX total** | **$2.51 bn** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $2,090 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh tangier`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$140 M / yr** | $117 |
| Steady-state, low capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$80 M / yr** | $67 |
| Lifecycle envelope (yr 1–40, low scenario) | **$702 M cumulative** | $585 |
| Lifecycle envelope (yr 1–40, high scenario) | **$702 M cumulative** | $585 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$3.51 bn cumulative** | $2,926 |

_Population basis: 1,200,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $80 M / yr → $80 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $2.01 bn | 2.0% | 40 y, 5 y grace | $80 M / yr |
| Government equity (no debt service) | 20% | $502 M | — | — | — |
| **Total** | **100%** | **$2.51 bn** | | | **$80 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $40 M / yr = **$40 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($100 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $47 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $17 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $382 k |
| Traction energy (488.3 GWh / yr) | 77,426 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 49.1 GWh/yr + dedicated solar plant 276.8 MW / 505.1 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $3.3 M |
| Labour (796 FTE) | driverless roster: OCC/remote 126, station/platform 216, passenger service 89, fleet maintenance 165, infrastructure/energy 154, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $5.5 M |
| **OPEX subtotal** | | **$73 M / yr** |

_Annual service work: 77,426 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 30.5 M train-km / yr (122.1 M car-km / yr). On-site PV covers 49.1 GWh/yr and the dedicated solar plant adds 505.1 GWh/yr against 488.3 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$410 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.09 |
| Day pass (3 trips) | $2.79 (15 % bulk discount) |
| Monthly unlimited pass | $32.80 (~8 % of median monthly income) |
| Annual pass | $360.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (768,000 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 21% |
| Annual paid trips | 140.2 M | 224.3 M | 59.2 M |
| Annual paid trips / city resident | 117 | 187 | 49 |
| Farebox revenue | $153 M / yr | $245 M / yr | $65 M / yr |
| Station shop leases | $3.1 M / yr | $3.1 M / yr | $3.1 M / yr |
| Advertising boards | $5.1 M / yr | $5.1 M / yr | $5.1 M / yr |
| **Total revenue** | **$161 M / yr** | **$253 M / yr** | **$73 M / yr** |
| Revenue / OPEX recovery | 221% | 347% | 100% |
| Country farebox-only policy target (diagnostic) | 60% | 60% | 60% |
| Gross repayable-debt service + residual OPEX subsidy | $80 M / yr | $80 M / yr | **$80 M / yr** |
| Operating surplus applied to debt support | -$80 M / yr | -$80 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$80 M / yr** |
| Operating surplus after OPEX (before debt support) | $88 M / yr | $180 M / yr | $0 / yr |

_Commercial-revenue assumptions: 9,064 m² of station shop/kiosk leases at $33/m²/month and 1,748 advertising boards at $287/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $44 M / yr | $71 M / yr | 16 min/trip × $1.18/h value-of-time proxy |
| Avoided road congestion | $40 M / yr | $65 M / yr | 505 M - 807 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $7.3 M / yr | $12 M / yr | 90.8–145.3 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $20 M / yr | $32 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $57 M / yr | $91 M / yr | 20% of paid trips × $2.05 local spend proxy |
| Entertainment / community activity supported | $30 M / yr | $49 M / yr | 11% of paid trips × $2.05 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$199 M / yr** | **$319 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 2 education anchors | 19,507 trips/school day; 4.3 M access-events/yr | 31,212 trips/school day; 6.9 M access-events/yr |
| Healthcare | 4 healthcare anchors | 29,491 trips/day; 10.8 M access-events/yr | 47,186 trips/day; 17.2 M access-events/yr |
| Commerce | 23 major/terminal/interchange nodes | 76,160 trips/trading day; 25.1 M access-events/yr | 121,856 trips/trading day; 40.2 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 40,704 trips/activity day; 12.2 M access-events/yr | 65,126 trips/activity day; 19.5 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $1.29 bn | 51% of $2.51 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $2.06 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $412 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 65,479 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 140.2 M - 224.3 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`tangier.toml`](tangier.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`tangier-network-map.png`](tangier-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`tangier.corridor.geojson`](tangier.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`tangier.stations.json`](tangier.stations.json) | Machine-readable station list |
| [`tangier.design-quality.yaml`](tangier.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug tangier

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug tangier \
    --sidecar .cache/osr-pipeline/rasters/tangier.grid.json \
    --out-dir designs/.../Tangier

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../tangier.toml \
    --out designs/.../README.md
```

`scripts/regenerate-tangier.sh` chains steps 3 + drift tests into a single command.
