# Quetta — Urban Rail Network

**Country:** PK · **Population:** 1,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Quetta rail network on OpenStreetMap](quetta-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`quetta.corridor.geojson`](quetta.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 77 |
| Interchange stations | 18 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 53.5% |
| Route length (double track) | 140.1 km |
| Revenue fleet | 173 × 4-car trainsets |
| Revenue fleet passenger capacity | 83,040 AW2 pax (110,720 AW3 crush) |
| Spare + cold-reserve | 21 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 31.0 km | 15 | 42 | NW Outer ↔ S Outer |
| line-2 | 26.0 km | 15 | 36 | NE Mid ↔ SW Outer |
| line-3 | 16.3 km | 11 | 24 | N Mid ↔ S Inner |
| line-4 | 15.9 km | 7 | 24 | NE Outer ↔ SE Inner |
| line-5 | 50.8 km | 30 | 68 | NW Mid ↔ NW Mid |
| **Total** | **140.1 km** | **77 unique** | **194** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 83,040 AW2 pax (110,720 AW3 crush) |
| Total fleet capacity | 93,120 AW2 pax (124,160 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 173 × 480 = **83,040 AW2 passengers** (110,720 AW3 crush)
- **Total fleet passenger capacity:** 194 × 480 = **93,120 AW2 passengers** (124,160 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 9,600 = **96,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **960,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **768,000 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **140.2 – 224.3 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **1,200,000**
- Anchor-weighted coverage: 53.5%
- Catchment population: **≈ 642,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 18 | 500 kW | 3000 kWh |
| Major | 30 | 400 kW | 2500 kWh |
| Standard | 21 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **77** | **35,800 kW** | **232,000 kWh** |

Aggregate station-rail charging power: **42,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **240.0 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 448 kWh | 28.0 km average line length |
| Onboard battery coverage | 1.1× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.3 kWh/stop | 555 kW average charger across stops |
| Stops to refill one trainset pack | 52 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 179 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,222 MWh/day | 70,734 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,043 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 240.0 MW / 1,200 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 232 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (129.6 km @ $3.0 M/km) | $389 M |
| Elevated (10.0 km @ $12.0 M/km) | $120 M |
| Elevated-interchange premium (8 sites @ $4.50 M) | $36 M |
| **Civil subtotal** | **$545 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 21 | $2.50 M | $52 M |
| `major` | 30 | $4.50 M | $135 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 18 | $12.0 M | $216 M |
| **Stations subtotal** | | | **$441 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 194 | $5.60 M | $1.09 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 776 | $100 k | $78 M |
| High sensitivity check | 776 | $200 k | $155 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 239,954 kW @ $700/kW | $168 M |
| Grid interconnection / PPA tie-in | 239,954 kW @ $100/kW | $24 M |
| Annual generation proxy | 240.0 MW × 5.0 peak-sun-h/day × 365 d/yr | 437.9 GWh/yr |
| **Dedicated solar plant subtotal** | | **$192 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 140.1 km × $0.050 M/km | $7.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $39 M |
| EPC integration + project management (7%) | on subtotal | $156 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $545 M |
| Stations | $441 M |
| Depots | $26 M |
| Rolling stock | $1.09 bn |
| Railway production plant | $78 M |
| Dedicated solar power plant | $192 M |
| Residual train-control wayside + charging microgrids | $46 M |
| EPC overhead (7%) | $156 M |
| **CAPEX total** | **$2.57 bn** |
| Per-route-km | $18 M / km |
| Per-capita (city pop) | $2,141 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh quetta`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$115 M / yr** | $95 |
| Steady-state, low capacity-use (year 8+) | **$88 M / yr** | $73 |
| Steady-state, high capacity-use (year 8+) | **$51 M / yr** | $42 |
| Steady-state, operating-neutral revenue case | **$86 M / yr** | $71 |
| Lifecycle envelope (yr 1–40, low scenario) | **$3.70 bn cumulative** | $3,083 |
| Lifecycle envelope (yr 1–40, high scenario) | **$2.48 bn cumulative** | $2,065 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$3.63 bn cumulative** | $3,024 |

_Population basis: 1,200,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $2.1 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $35 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $2.06 bn | 2.0% | 40 y, 7 y grace | $86 M / yr |
| Government equity (no debt service) | 20% | $514 M | — | — | — |
| **Total** | **100%** | **$2.57 bn** | | | **$86 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $41 M / yr = **$41 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($73 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $43 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $20 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $349 k |
| Traction energy (446.1 GWh / yr) | 70,734 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 65.3 GWh/yr + dedicated solar plant 240.0 MW / 437.9 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $2.9 M |
| Labour (902 FTE) | driverless roster: OCC/remote 118, station/platform 346, passenger service 89, fleet maintenance 152, infrastructure/energy 151, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $2.5 M |
| **OPEX subtotal** | | **$69 M / yr** |

_Annual service work: 70,734 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 27.9 M train-km / yr (111.5 M car-km / yr). On-site PV covers 65.3 GWh/yr and the dedicated solar plant adds 437.9 GWh/yr against 446.1 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$165 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.44 |
| Day pass (3 trips) | $1.12 (15 % bulk discount) |
| Monthly unlimited pass | $13.20 (~8 % of median monthly income) |
| Annual pass | $145.20 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (768,000 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 52% |
| Annual paid trips | 140.2 M | 224.3 M | 145.0 M |
| Annual paid trips / city resident | 117 | 187 | 121 |
| Farebox revenue | $62 M / yr | $99 M / yr | $64 M / yr |
| Station shop leases | $2.2 M / yr | $2.2 M / yr | $2.2 M / yr |
| Advertising boards | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| **Total revenue** | **$67 M / yr** | **$104 M / yr** | **$69 M / yr** |
| Revenue / OPEX recovery | 97% | 150% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $88 M / yr | $86 M / yr | **$86 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$35 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $88 M / yr | $51 M / yr | **$86 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $35 M / yr | $0 / yr |

_Commercial-revenue assumptions: 15,896 m² of station shop/kiosk leases at $13/m²/month and 2,880 advertising boards at $115/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $18 M / yr | $28 M / yr | 16 min/trip × $0.48/h value-of-time proxy |
| Avoided road congestion | $40 M / yr | $65 M / yr | 505 M - 807 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $7.3 M / yr | $12 M / yr | 90.8–145.3 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $20 M / yr | $32 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $50 M / yr | $80 M / yr | 24% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $22 M / yr | $36 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$158 M / yr** | **$252 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 3 education anchors | 20,337 trips/school day; 4.5 M access-events/yr | 32,539 trips/school day; 7.2 M access-events/yr |
| Healthcare | 4 healthcare anchors | 28,201 trips/day; 10.3 M access-events/yr | 45,122 trips/day; 16.5 M access-events/yr |
| Commerce | 56 major/terminal/interchange nodes | 90,764 trips/trading day; 30.0 M access-events/yr | 145,222 trips/trading day; 47.9 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 40,704 trips/activity day; 12.2 M access-events/yr | 65,126 trips/activity day; 19.5 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $1.34 bn | 52% of $2.57 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $2.15 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $307 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 169,615 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 140.2 M - 224.3 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`quetta.toml`](quetta.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`quetta-network-map.png`](quetta-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`quetta.corridor.geojson`](quetta.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`quetta.stations.json`](quetta.stations.json) | Machine-readable station list |
| [`quetta.design-quality.yaml`](quetta.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug quetta

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug quetta \
    --sidecar .cache/osr-pipeline/rasters/quetta.grid.json \
    --out-dir designs/.../Quetta

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../quetta.toml \
    --out designs/.../README.md
```

`scripts/regenerate-quetta.sh` chains steps 3 + drift tests into a single command.
