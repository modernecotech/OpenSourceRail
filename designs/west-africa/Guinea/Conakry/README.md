# Conakry — Urban Rail Network

**Country:** GN · **Population:** 2,010,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Conakry rail network on OpenStreetMap](conakry-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`conakry.corridor.geojson`](conakry.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 54 |
| Interchange stations | 6 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 40.2% |
| Route length (double track) | 93.2 km |
| Revenue fleet | 114 × 4-car trainsets |
| Revenue fleet passenger capacity | 54,720 AW2 pax (72,960 AW3 crush) |
| Spare + cold-reserve | 13 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 30.1 km | 20 | 41 | NE Outer ↔ SW Outer |
| line-2 | 16.1 km | 12 | 24 | SW Inner ↔ NE Mid |
| line-3 | 46.9 km | 23 | 62 | NE Mid ↔ NE Mid |
| **Total** | **93.2 km** | **54 unique** | **127** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 54,720 AW2 pax (72,960 AW3 crush) |
| Total fleet capacity | 60,960 AW2 pax (81,280 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 114 × 480 = **54,720 AW2 passengers** (72,960 AW3 crush)
- **Total fleet passenger capacity:** 127 × 480 = **60,960 AW2 passengers** (81,280 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 9,600 = **57,600 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **576,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **460,800 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **84.1 – 134.6 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **2,010,000**
- Anchor-weighted coverage: 40.2%
- Catchment population: **≈ 808,020** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 6 | 500 kW | 3000 kWh |
| Major | 33 | 400 kW | 2500 kWh |
| Standard | 12 | 300 kW | 2000 kWh |
| Terminal | 3 | 500 kW | 3000 kWh |
| **Total installed** | **55** | **26,300 kW** | **173,500 kWh** |

Aggregate station-rail charging power: **29,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **156.8 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 497 kWh | 31.1 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 546 kW average charger across stops |
| Stops to refill one trainset pack | 53 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 132 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 813 MWh/day | 47,059 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 682 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 156.8 MW / 784 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 174 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (88.1 km @ $3.0 M/km) | $264 M |
| Elevated (3.5 km @ $12.0 M/km) | $42 M |
| Elevated-interchange premium (3 sites @ $4.50 M) | $14 M |
| **Civil subtotal** | **$320 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 12 | $2.50 M | $30 M |
| `major` | 33 | $4.50 M | $148 M |
| `terminal` | 3 | $4.50 M | $14 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 6 | $12.0 M | $72 M |
| **Stations subtotal** | | | **$269 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 3 | $2.0 M | $6.0 M |
| **Depots subtotal** | | | **$18 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 127 | $5.60 M | $711 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 508 | $100 k | $51 M |
| High sensitivity check | 508 | $200 k | $102 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 156,787 kW @ $700/kW | $110 M |
| Grid interconnection / PPA tie-in | 156,787 kW @ $100/kW | $16 M |
| Annual generation proxy | 156.8 MW × 5.0 peak-sun-h/day × 365 d/yr | 286.1 GWh/yr |
| **Dedicated solar plant subtotal** | | **$125 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 93.2 km × $0.050 M/km | $4.6 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $25 M |
| EPC integration + project management (7%) | on subtotal | $98 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $320 M |
| Stations | $269 M |
| Depots | $18 M |
| Rolling stock | $711 M |
| Railway production plant | $51 M |
| Dedicated solar power plant | $125 M |
| Residual train-control wayside + charging microgrids | $30 M |
| EPC overhead (7%) | $98 M |
| **CAPEX total** | **$1.62 bn** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $807 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh conakry`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$58 M / yr** | $29 |
| Steady-state, low capacity-use (year 11+) | **$70 M / yr** | $35 |
| Steady-state, high capacity-use (year 11+) | **$52 M / yr** | $26 |
| Steady-state, operating-neutral revenue case | **$58 M / yr** | $29 |
| Lifecycle envelope (yr 1–40, low scenario) | **$2.68 bn cumulative** | $1,333 |
| Lifecycle envelope (yr 1–40, high scenario) | **$2.15 bn cumulative** | $1,072 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.32 bn cumulative** | $1,155 |

_Population basis: 2,010,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $12 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $5.6 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $1.30 bn | 2.0% | 40 y, 10 y grace | $58 M / yr |
| Government equity (no debt service) | 20% | $324 M | — | — | — |
| **Total** | **100%** | **$1.62 bn** | | | **$58 M / yr** |

_During the 10-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $26 M / yr = **$26 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($32 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $28 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $12 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $229 k |
| Traction energy (296.8 GWh / yr) | 47,059 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 48.0 GWh/yr + dedicated solar plant 156.8 MW / 286.1 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $1.9 M |
| Labour (586 FTE) | driverless roster: OCC/remote 81, station/platform 225, passenger service 54, fleet maintenance 100, infrastructure/energy 96, admin/training 30; no train drivers × country median × 12 × engineer-premium 1.4 | $1.3 M |
| **OPEX subtotal** | | **$44 M / yr** |

_Annual service work: 47,059 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 18.6 M train-km / yr (74.2 M car-km / yr). On-site PV covers 48.0 GWh/yr and the dedicated solar plant adds 286.1 GWh/yr against 296.8 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$130 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.35 |
| Day pass (3 trips) | $0.88 (15 % bulk discount) |
| Monthly unlimited pass | $10.40 (~8 % of median monthly income) |
| Annual pass | $114.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (460,800 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 70% |
| Annual paid trips | 84.1 M | 134.6 M | 118.4 M |
| Annual paid trips / city resident | 42 | 67 | 59 |
| Farebox revenue | $29 M / yr | $47 M / yr | $41 M / yr |
| Station shop leases | $1.1 M / yr | $1.1 M / yr | $1.1 M / yr |
| Advertising boards | $1.8 M / yr | $1.8 M / yr | $1.8 M / yr |
| **Total revenue** | **$32 M / yr** | **$50 M / yr** | **$44 M / yr** |
| Revenue / OPEX recovery | 73% | 113% | 100% |
| Country farebox-only policy target (diagnostic) | 35% | 35% | 35% |
| Gross repayable-debt service + residual OPEX subsidy | $70 M / yr | $58 M / yr | **$58 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$5.6 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $70 M / yr | $52 M / yr | **$58 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $5.6 M / yr | $0 / yr |

_Commercial-revenue assumptions: 10,464 m² of station shop/kiosk leases at $10/m²/month and 1,912 advertising boards at $91/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $8.4 M / yr | $13 M / yr | 16 min/trip × $0.38/h value-of-time proxy |
| Avoided road congestion | $24 M / yr | $39 M / yr | 303 M - 484 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $4.4 M / yr | $7.0 M / yr | 54.5–87.2 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $12 M / yr | $19 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $31 M / yr | $49 M / yr | 24% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $14 M / yr | $22 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$93 M / yr** | **$149 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 12 education anchors | 20,275 trips/school day; 4.5 M access-events/yr | 32,440 trips/school day; 7.1 M access-events/yr |
| Healthcare | 2 healthcare anchors | 15,258 trips/day; 5.6 M access-events/yr | 24,412 trips/day; 8.9 M access-events/yr |
| Commerce | 43 major/terminal/interchange nodes | 56,128 trips/trading day; 18.5 M access-events/yr | 89,805 trips/trading day; 29.6 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 24,853 trips/activity day; 7.5 M access-events/yr | 39,765 trips/activity day; 11.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $842 M | 52% of $1.62 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $1.35 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $135 M / yr | spread across 10 construction / grace years |
| Construction employment supported | 134,958 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 84.1 M - 134.6 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`conakry.toml`](conakry.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`conakry-network-map.png`](conakry-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`conakry.corridor.geojson`](conakry.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`conakry.stations.json`](conakry.stations.json) | Machine-readable station list |
| [`conakry.design-quality.yaml`](conakry.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug conakry

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug conakry \
    --sidecar .cache/osr-pipeline/rasters/conakry.grid.json \
    --out-dir designs/.../Conakry

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../conakry.toml \
    --out designs/.../README.md
```

`scripts/regenerate-conakry.sh` chains steps 3 + drift tests into a single command.
