# Yaounde — Urban Rail Network

**Country:** CM · **Population:** 4,100,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Yaounde rail network on OpenStreetMap](yaounde-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`yaounde.corridor.geojson`](yaounde.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 8 |
| Unique stations | 135 |
| Interchange stations | 28 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 43.4% |
| Route length (double track) | 266.7 km |
| Revenue fleet | 325 × 6-car trainsets |
| Revenue fleet passenger capacity | 234,000 AW2 pax (312,000 AW3 crush) |
| Spare + cold-reserve | 37 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 39.9 km | 21 | 53 | SW Mid ↔ NE Outer |
| line-2 | 36.9 km | 14 | 50 | SW Mid ↔ NE Outer |
| line-3 | 22.6 km | 12 | 31 | S Mid ↔ NE Mid |
| line-4 | 28.2 km | 16 | 39 | SE Outer ↔ NW Inner |
| line-5 | 28.5 km | 15 | 39 | SE Mid ↔ W Mid |
| line-6 | 24.7 km | 11 | 35 | E Mid ↔ N Mid |
| line-7 | 35.6 km | 16 | 48 | NW Outer ↔ S Inner |
| line-8 | 50.2 km | 31 | 67 | W Inner ↔ W Inner |
| **Total** | **266.7 km** | **135 unique** | **362** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 234,000 AW2 pax (312,000 AW3 crush) |
| Total fleet capacity | 260,640 AW2 pax (347,520 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 325 × 720 = **234,000 AW2 passengers** (312,000 AW3 crush)
- **Total fleet passenger capacity:** 362 × 720 = **260,640 AW2 passengers** (347,520 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 8 lines × 2 directions × 14,400 = **230,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **2,304,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,843,200 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **336.4 – 538.2 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **4,100,000**
- Anchor-weighted coverage: 43.4%
- Catchment population: **≈ 1,779,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 28 | 500 kW | 3000 kWh |
| Major | 46 | 400 kW | 2500 kWh |
| Standard | 44 | 300 kW | 2000 kWh |
| Terminal | 13 | 500 kW | 3000 kWh |
| **Total installed** | **132** | **57,100 kW** | **366,000 kWh** |

Aggregate station-rail charging power: **74,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **737.1 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 800 kWh | 33.3 km average line length |
| Onboard battery coverage | 0.9× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 548 kW average charger across stops |
| Stops to refill one trainset pack | 79 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 286 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 3,490 MWh/day | 134,661 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 3,205 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 737.1 MW / 3,686 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 366 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (240.6 km @ $3.0 M/km) | $722 M |
| Elevated (20.8 km @ $12.0 M/km) | $250 M |
| Elevated-interchange premium (15 sites @ $4.50 M) | $68 M |
| **Civil subtotal** | **$1.04 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | $600 k | $2.4 M |
| `standard` | 44 | $2.50 M | $110 M |
| `major` | 46 | $4.50 M | $207 M |
| `terminal` | 13 | $4.50 M | $58 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 28 | $12.0 M | $336 M |
| **Stations subtotal** | | | **$719 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 13 | $2.0 M | $26 M |
| **Depots subtotal** | | | **$38 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 362 | $8.40 M | $3.04 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 2172 | $100 k | $217 M |
| High sensitivity check | 2172 | $200 k | $434 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 737,128 kW @ $700/kW | $516 M |
| Grid interconnection / PPA tie-in | 737,128 kW @ $100/kW | $74 M |
| Annual generation proxy | 737.1 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,345.3 GWh/yr |
| **Dedicated solar plant subtotal** | | **$590 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 266.7 km × $0.050 M/km | $13 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $63 M |
| EPC integration + project management (7%) | on subtotal | $359 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.04 bn |
| Stations | $719 M |
| Depots | $38 M |
| Rolling stock | $3.04 bn |
| Railway production plant | $217 M |
| Dedicated solar power plant | $590 M |
| Residual train-control wayside + charging microgrids | $77 M |
| EPC overhead (7%) | $359 M |
| **CAPEX total** | **$6.08 bn** |
| Per-route-km | $23 M / km |
| Per-capita (city pop) | $1,483 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh yaounde`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$271 M / yr** | $66 |
| Steady-state, low capacity-use (year 8+) | **$203 M / yr** | $50 |
| Steady-state, high capacity-use (year 8+) | **$106 M / yr** | $26 |
| Steady-state, operating-neutral revenue case | **$203 M / yr** | $49 |
| Lifecycle envelope (yr 1–40, low scenario) | **$8.60 bn cumulative** | $2,098 |
| Lifecycle envelope (yr 1–40, high scenario) | **$5.41 bn cumulative** | $1,318 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$8.59 bn cumulative** | $2,095 |

_Population basis: 4,100,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $439 k / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $96 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $4.86 bn | 2.0% | 40 y, 7 y grace | $203 M / yr |
| Government equity (no debt service) | 20% | $1.22 bn | — | — | — |
| **Total** | **100%** | **$6.08 bn** | | | **$203 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $97 M / yr = **$97 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($174 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $122 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $36 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $654 k |
| Traction energy (1274.0 GWh / yr) | 134,661 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 104.2 GWh/yr + dedicated solar plant 737.1 MW / 1345.3 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $8.8 M |
| Labour (1,596 FTE) | driverless roster: OCC/remote 207, station/platform 565, passenger service 191, fleet maintenance 286, infrastructure/energy 277, admin/training 70; no train drivers × country median × 12 × engineer-premium 1.4 | $4.8 M |
| **OPEX subtotal** | | **$172 M / yr** |

_Annual service work: 134,661 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 53.1 M train-km / yr (318.5 M car-km / yr). On-site PV covers 104.2 GWh/yr and the dedicated solar plant adds 1345.3 GWh/yr against 1274.0 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$180 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.48 |
| Day pass (3 trips) | $1.22 (15 % bulk discount) |
| Monthly unlimited pass | $14.40 (~8 % of median monthly income) |
| Annual pass | $158.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (1,843,200 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 50% |
| Annual paid trips | 336.4 M | 538.2 M | 337.3 M |
| Annual paid trips / city resident | 82 | 131 | 82 |
| Farebox revenue | $161 M / yr | $258 M / yr | $162 M / yr |
| Station shop leases | $3.9 M / yr | $3.9 M / yr | $3.9 M / yr |
| Advertising boards | $6.1 M / yr | $6.1 M / yr | $6.1 M / yr |
| **Total revenue** | **$171 M / yr** | **$268 M / yr** | **$172 M / yr** |
| Revenue / OPEX recovery | 100% | 156% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $203 M / yr | $203 M / yr | **$203 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$96 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $203 M / yr | $106 M / yr | **$203 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $96 M / yr | $0 / yr |

_Commercial-revenue assumptions: 25,768 m² of station shop/kiosk leases at $14/m²/month and 4,716 advertising boards at $126/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $47 M / yr | $75 M / yr | 16 min/trip × $0.52/h value-of-time proxy |
| Avoided road congestion | $97 M / yr | $155 M / yr | 1,211 M - 1,938 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $17 M / yr | $28 M / yr | 218.0–348.8 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $48 M / yr | $78 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $115 M / yr | $184 M / yr | 23% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $53 M / yr | $86 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$378 M / yr** | **$605 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 24 education anchors | 81,935 trips/school day; 18.0 M access-events/yr | 131,097 trips/school day; 28.8 M access-events/yr |
| Healthcare | 19 healthcare anchors | 83,048 trips/day; 30.3 M access-events/yr | 132,877 trips/day; 48.5 M access-events/yr |
| Commerce | 88 major/terminal/interchange nodes | 210,534 trips/trading day; 69.5 M access-events/yr | 336,855 trips/trading day; 111.2 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 97,690 trips/activity day; 29.3 M access-events/yr | 156,303 trips/activity day; 46.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $3.07 bn | 50% of $6.08 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $4.91 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $701 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 354,930 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 336.4 M - 538.2 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`yaounde.toml`](yaounde.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`yaounde-network-map.png`](yaounde-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`yaounde.corridor.geojson`](yaounde.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`yaounde.stations.json`](yaounde.stations.json) | Machine-readable station list |
| [`yaounde.design-quality.yaml`](yaounde.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug yaounde

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug yaounde \
    --sidecar .cache/osr-pipeline/rasters/yaounde.grid.json \
    --out-dir designs/.../Yaounde

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../yaounde.toml \
    --out designs/.../README.md
```

`scripts/regenerate-yaounde.sh` chains steps 3 + drift tests into a single command.
