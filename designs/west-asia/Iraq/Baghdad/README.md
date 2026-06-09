# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 9,780,429

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Baghdad rail network on OpenStreetMap](baghdad-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`baghdad.corridor.geojson`](baghdad.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 217 |
| Interchange stations | 37 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 44.9% |
| Route length (double track) | 509.5 km |
| Revenue fleet | 603 × 6-car trainsets |
| Revenue fleet passenger capacity | 434,160 AW2 pax (578,880 AW3 crush) |
| Spare + cold-reserve | 65 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 55.7 km | 23 | 73 | N Outer ↔ S Outer |
| line-2 | 52.0 km | 26 | 69 | SE Outer ↔ NW Outer |
| line-3 | 56.3 km | 23 | 74 | SW Outer ↔ NE Outer |
| line-4 | 56.8 km | 22 | 74 | SE Outer ↔ NW Mid |
| line-5 | 57.6 km | 24 | 75 | E Outer ↔ W Outer |
| line-6 | 41.9 km | 17 | 56 | W Mid ↔ E Mid |
| line-7 | 46.7 km | 21 | 62 | NE Mid ↔ SW Outer |
| line-8 | 42.9 km | 14 | 57 | NW Mid ↔ S Outer |
| line-9 | 99.7 km | 48 | 128 | NW Mid ↔ NW Mid |
| **Total** | **509.5 km** | **217 unique** | **668** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 434,160 AW2 pax (578,880 AW3 crush) |
| Total fleet capacity | 480,960 AW2 pax (641,280 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 603 × 720 = **434,160 AW2 passengers** (578,880 AW3 crush)
- **Total fleet passenger capacity:** 668 × 720 = **480,960 AW2 passengers** (641,280 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 14,400 = **259,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,592,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **2,073,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **378.4 – 605.5 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **9,780,429**
- Anchor-weighted coverage: 44.9%
- Catchment population: **≈ 4,391,412** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 37 | 500 kW | 3000 kWh |
| Major | 53 | 400 kW | 2500 kWh |
| Standard | 99 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **205** | **81,900 kW** | **526,500 kWh** |

Aggregate station-rail charging power: **113,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,439.7 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,359 kWh | 56.6 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.7 kWh/stop | 524 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 410 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 6,669 MWh/day | 257,287 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 6,259 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,439.7 MW / 7,198 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 526 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (476.2 km @ $3.0 M/km) | $1.43 bn |
| Elevated (31.4 km @ $12.0 M/km) | $377 M |
| Elevated-interchange premium (19 sites @ $4.50 M) | $86 M |
| **Civil subtotal** | **$1.89 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 13 | $600 k | $7.8 M |
| `standard` | 99 | $2.50 M | $248 M |
| `major` | 53 | $4.50 M | $238 M |
| `terminal` | 15 | $4.50 M | $68 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 37 | $12.0 M | $444 M |
| **Stations subtotal** | | | **$1.01 bn** |

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
| `metro-6car` (revenue + spare + cold reserve) | 668 | $8.40 M | $5.61 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 4008 | $100 k | $401 M |
| High sensitivity check | 4008 | $200 k | $802 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,439,658 kW @ $700/kW | $1.01 bn |
| Grid interconnection / PPA tie-in | 1,439,658 kW @ $100/kW | $144 M |
| Annual generation proxy | 1,439.7 MW × 5.0 peak-sun-h/day × 365 d/yr | 2,627.4 GWh/yr |
| **Dedicated solar plant subtotal** | | **$1.15 bn** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 509.5 km × $0.050 M/km | $25 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $90 M |
| EPC integration + project management (7%) | on subtotal | $635 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.89 bn |
| Stations | $1.01 bn |
| Depots | $42 M |
| Rolling stock | $5.61 bn |
| Railway production plant | $401 M |
| Dedicated solar power plant | $1.15 bn |
| Residual train-control wayside + charging microgrids | $115 M |
| EPC overhead (7%) | $635 M |
| **CAPEX total** | **$10.86 bn** |
| Per-route-km | $21 M / km |
| Per-capita (city pop) | $1,110 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh baghdad`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$608 M / yr** | $62 |
| Steady-state, low capacity-use (year 6+) | **$252 M / yr** | $26 |
| Steady-state, high capacity-use (year 6+) | **$22 M / yr** | $2 |
| Steady-state, operating-neutral revenue case | **$347 M / yr** | $36 |
| Lifecycle envelope (yr 1–40, low scenario) | **$11.88 bn cumulative** | $1,214 |
| Lifecycle envelope (yr 1–40, high scenario) | **$3.82 bn cumulative** | $391 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$15.20 bn cumulative** | $1,554 |

_Population basis: 9,780,429 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $95 M / yr → $325 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $8.69 bn | 2.0% | 40 y, 5 y grace | $347 M / yr |
| Government equity (no debt service) | 20% | $2.17 bn | — | — | — |
| **Total** | **100%** | **$10.86 bn** | | | **$347 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $174 M / yr = **$174 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($434 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $224 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $59 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $1.3 M |
| Traction energy (2434.1 GWh / yr) | 257,287 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 149.5 GWh/yr + dedicated solar plant 1439.7 MW / 2627.4 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $17 M |
| Labour (2,452 FTE) | driverless roster: OCC/remote 353, station/platform 795, passenger service 215, fleet maintenance 539, infrastructure/energy 472, admin/training 78; no train drivers × country median × 12 × engineer-premium 1.4 | $16 M |
| **OPEX subtotal** | | **$318 M / yr** |

_Annual service work: 257,287 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 101.4 M train-km / yr (608.5 M car-km / yr). On-site PV covers 149.5 GWh/yr and the dedicated solar plant adds 2627.4 GWh/yr against 2434.1 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.01 |
| Day pass (3 trips) | $2.58 (15 % bulk discount) |
| Monthly unlimited pass | $30.40 (~8 % of median monthly income) |
| Annual pass | $334.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (2,073,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 38% |
| Annual paid trips | 378.4 M | 605.5 M | 284.7 M |
| Annual paid trips / city resident | 39 | 62 | 29 |
| Farebox revenue | $383 M / yr | $614 M / yr | $289 M / yr |
| Station shop leases | $11 M / yr | $11 M / yr | $11 M / yr |
| Advertising boards | $18 M / yr | $18 M / yr | $18 M / yr |
| **Total revenue** | **$412 M / yr** | **$643 M / yr** | **$318 M / yr** |
| Revenue / OPEX recovery | 130% | 202% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $347 M / yr | $347 M / yr | **$347 M / yr** |
| Operating surplus applied to debt support | -$95 M / yr | -$325 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $252 M / yr | $22 M / yr | **$347 M / yr** |
| Operating surplus after OPEX (before debt support) | $95 M / yr | $325 M / yr | $0 / yr |

_Commercial-revenue assumptions: 35,040 m² of station shop/kiosk leases at $30/m²/month and 6,540 advertising boards at $266/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $111 M / yr | $177 M / yr | 16 min/trip × $1.10/h value-of-time proxy |
| Avoided road congestion | $109 M / yr | $174 M / yr | 1,362 M - 2,180 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $20 M / yr | $31 M / yr | 245.2–392.4 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $54 M / yr | $87 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $152 M / yr | $243 M / yr | 21% of paid trips × $1.90 local spend proxy |
| Entertainment / community activity supported | $76 M / yr | $122 M / yr | 11% of paid trips × $1.90 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$522 M / yr** | **$835 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 19 education anchors | 66,502 trips/school day; 14.6 M access-events/yr | 106,403 trips/school day; 23.4 M access-events/yr |
| Healthcare | 31 healthcare anchors | 93,971 trips/day; 34.3 M access-events/yr | 150,353 trips/day; 54.9 M access-events/yr |
| Commerce | 106 major/terminal/interchange nodes | 219,066 trips/trading day; 72.3 M access-events/yr | 350,505 trips/trading day; 115.7 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 109,901 trips/activity day; 33.0 M access-events/yr | 175,841 trips/activity day; 52.8 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $5.43 bn | 50% of $10.86 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $8.68 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $1.74 bn / yr | spread across 5 construction / grace years |
| Construction employment supported | 297,506 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 378.4 M - 605.5 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`baghdad.toml`](baghdad.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`baghdad-network-map.png`](baghdad-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`baghdad.corridor.geojson`](baghdad.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`baghdad.stations.json`](baghdad.stations.json) | Machine-readable station list |
| [`baghdad.design-quality.yaml`](baghdad.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug baghdad

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug baghdad \
    --sidecar .cache/osr-pipeline/rasters/baghdad.grid.json \
    --out-dir designs/.../Baghdad

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../baghdad.toml \
    --out designs/.../README.md
```

`scripts/regenerate-baghdad.sh` chains steps 3 + drift tests into a single command.
