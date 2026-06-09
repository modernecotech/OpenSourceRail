# Faisalabad — Urban Rail Network

**Country:** PK · **Population:** 3,556,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Faisalabad rail network on OpenStreetMap](faisalabad-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`faisalabad.corridor.geojson`](faisalabad.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 92 |
| Interchange stations | 19 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 51.8% |
| Route length (double track) | 166.0 km |
| Revenue fleet | 202 × 6-car trainsets |
| Revenue fleet passenger capacity | 145,440 AW2 pax (193,920 AW3 crush) |
| Spare + cold-reserve | 22 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 31.8 km | 17 | 43 | NE Mid ↔ SW Outer |
| line-2 | 27.2 km | 17 | 38 | N Mid ↔ SE Mid |
| line-3 | 23.5 km | 13 | 32 | E Mid ↔ W Mid |
| line-4 | 31.1 km | 15 | 42 | NE Outer ↔ W Mid |
| line-5 | 52.4 km | 31 | 69 | W Mid ↔ W Mid |
| **Total** | **166.0 km** | **92 unique** | **224** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 145,440 AW2 pax (193,920 AW3 crush) |
| Total fleet capacity | 161,280 AW2 pax (215,040 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 202 × 720 = **145,440 AW2 passengers** (193,920 AW3 crush)
- **Total fleet passenger capacity:** 224 × 720 = **161,280 AW2 passengers** (215,040 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 14,400 = **144,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,440,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,152,000 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **210.2 – 336.4 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **3,556,000**
- Anchor-weighted coverage: 51.8%
- Catchment population: **≈ 1,842,008** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 19 | 500 kW | 3000 kWh |
| Major | 38 | 400 kW | 2500 kWh |
| Standard | 27 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **92** | **41,300 kW** | **267,000 kWh** |

Aggregate station-rail charging power: **50,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **452.2 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 797 kWh | 33.2 km average line length |
| Onboard battery coverage | 0.9× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.1 kWh/stop | 546 kW average charger across stops |
| Stops to refill one trainset pack | 79 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 206 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 2,172 MWh/day | 83,811 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,966 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 452.2 MW / 2,261 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 267 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (148.0 km @ $3.0 M/km) | $444 M |
| Elevated (17.2 km @ $12.0 M/km) | $206 M |
| Elevated-interchange premium (9 sites @ $4.50 M) | $40 M |
| **Civil subtotal** | **$691 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 27 | $2.50 M | $68 M |
| `major` | 38 | $4.50 M | $171 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 19 | $12.0 M | $228 M |
| **Stations subtotal** | | | **$504 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 224 | $8.40 M | $1.88 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1344 | $100 k | $134 M |
| High sensitivity check | 1344 | $200 k | $269 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 452,155 kW @ $700/kW | $317 M |
| Grid interconnection / PPA tie-in | 452,155 kW @ $100/kW | $45 M |
| Annual generation proxy | 452.2 MW × 5.0 peak-sun-h/day × 365 d/yr | 825.2 GWh/yr |
| **Dedicated solar plant subtotal** | | **$362 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 166.0 km × $0.050 M/km | $8.3 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $45 M |
| EPC integration + project management (7%) | on subtotal | $230 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $691 M |
| Stations | $504 M |
| Depots | $26 M |
| Rolling stock | $1.88 bn |
| Railway production plant | $134 M |
| Dedicated solar power plant | $362 M |
| Residual train-control wayside + charging microgrids | $53 M |
| EPC overhead (7%) | $230 M |
| **CAPEX total** | **$3.88 bn** |
| Per-route-km | $23 M / km |
| Per-capita (city pop) | $1,091 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh faisalabad`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$173 M / yr** | $49 |
| Steady-state, low capacity-use (year 8+) | **$139 M / yr** | $39 |
| Steady-state, high capacity-use (year 8+) | **$83 M / yr** | $23 |
| Steady-state, operating-neutral revenue case | **$129 M / yr** | $36 |
| Lifecycle envelope (yr 1–40, low scenario) | **$5.79 bn cumulative** | $1,629 |
| Lifecycle envelope (yr 1–40, high scenario) | **$3.96 bn cumulative** | $1,114 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$5.48 bn cumulative** | $1,542 |

_Population basis: 3,556,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $9.4 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $46 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $3.11 bn | 2.0% | 40 y, 7 y grace | $129 M / yr |
| Government equity (no debt service) | 20% | $776 M | — | — | — |
| **Total** | **100%** | **$3.88 bn** | | | **$129 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $62 M / yr = **$62 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($111 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $75 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $24 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $413 k |
| Traction energy (792.9 GWh / yr) | 83,811 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 75.4 GWh/yr + dedicated solar plant 452.2 MW / 825.2 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $5.4 M |
| Labour (1,049 FTE) | driverless roster: OCC/remote 134, station/platform 398, passenger service 120, fleet maintenance 178, infrastructure/energy 173, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $2.9 M |
| **OPEX subtotal** | | **$108 M / yr** |

_Annual service work: 83,811 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 33.0 M train-km / yr (198.2 M car-km / yr). On-site PV covers 75.4 GWh/yr and the dedicated solar plant adds 825.2 GWh/yr against 792.9 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.44 |
| Day pass (3 trips) | $1.12 (15 % bulk discount) |
| Monthly unlimited pass | $13.20 (~8 % of median monthly income) |
| Annual pass | $145.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (1,152,000 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 55% |
| Annual paid trips | 210.2 M | 336.4 M | 231.7 M |
| Annual paid trips / city resident | 59 | 95 | 65 |
| Farebox revenue | $93 M / yr | $148 M / yr | $102 M / yr |
| Station shop leases | $2.6 M / yr | $2.6 M / yr | $2.6 M / yr |
| Advertising boards | $3.9 M / yr | $3.9 M / yr | $3.9 M / yr |
| **Total revenue** | **$99 M / yr** | **$154 M / yr** | **$108 M / yr** |
| Revenue / OPEX recovery | 91% | 142% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $139 M / yr | $129 M / yr | **$129 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$46 M / yr | **-$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $139 M / yr | $83 M / yr | **$129 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $46 M / yr | $0 / yr |

_Commercial-revenue assumptions: 18,312 m² of station shop/kiosk leases at $13/m²/month and 3,328 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $27 M / yr | $43 M / yr | 16 min/trip × $0.48/h value-of-time proxy |
| Avoided road congestion | $61 M / yr | $97 M / yr | 757 M - 1,211 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $11 M / yr | $17 M / yr | 136.2–218.0 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $30 M / yr | $48 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $74 M / yr | $118 M / yr | 23% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $33 M / yr | $53 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$236 M / yr** | **$377 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 12 education anchors | 36,864 trips/school day; 8.1 M access-events/yr | 58,982 trips/school day; 13.0 M access-events/yr |
| Healthcare | 19 healthcare anchors | 51,584 trips/day; 18.8 M access-events/yr | 82,534 trips/day; 30.1 M access-events/yr |
| Commerce | 65 major/terminal/interchange nodes | 134,890 trips/trading day; 44.5 M access-events/yr | 215,825 trips/trading day; 71.2 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 61,056 trips/activity day; 18.3 M access-events/yr | 97,690 trips/activity day; 29.3 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $1.97 bn | 51% of $3.88 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $3.15 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $451 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 248,889 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 210.2 M - 336.4 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`faisalabad.toml`](faisalabad.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`faisalabad-network-map.png`](faisalabad-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`faisalabad.corridor.geojson`](faisalabad.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`faisalabad.stations.json`](faisalabad.stations.json) | Machine-readable station list |
| [`faisalabad.design-quality.yaml`](faisalabad.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug faisalabad

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug faisalabad \
    --sidecar .cache/osr-pipeline/rasters/faisalabad.grid.json \
    --out-dir designs/.../Faisalabad

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../faisalabad.toml \
    --out designs/.../README.md
```

`scripts/regenerate-faisalabad.sh` chains steps 3 + drift tests into a single command.
