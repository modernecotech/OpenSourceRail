# Sulaymaniyah — Urban Rail Network

**Country:** IQ · **Population:** 2,150,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Sulaymaniyah rail network on OpenStreetMap](sulaymaniyah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`sulaymaniyah.corridor.geojson`](sulaymaniyah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 47 |
| Interchange stations | 10 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 67.1% |
| Route length (double track) | 117.4 km |
| Revenue fleet | 144 × 4-car trainsets |
| Revenue fleet passenger capacity | 69,120 AW2 pax (92,160 AW3 crush) |
| Spare + cold-reserve | 18 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 15.5 km | 9 | 23 | W Mid ↔ E Inner |
| line-2 | 15.1 km | 7 | 23 | W Mid ↔ SE Mid |
| line-3 | 27.7 km | 9 | 38 | SW Mid ↔ NE Outer |
| line-4 | 59.1 km | 23 | 78 | W Mid ↔ W Mid |
| **Total** | **117.4 km** | **47 unique** | **162** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 69,120 AW2 pax (92,160 AW3 crush) |
| Total fleet capacity | 77,760 AW2 pax (103,680 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 144 × 480 = **69,120 AW2 passengers** (92,160 AW3 crush)
- **Total fleet passenger capacity:** 162 × 480 = **77,760 AW2 passengers** (103,680 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 9,600 = **76,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **768,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **614,400 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **112.1 – 179.4 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **2,150,000**
- Anchor-weighted coverage: 67.1%
- Catchment population: **≈ 1,442,650** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 10 | 500 kW | 3000 kWh |
| Major | 4 | 400 kW | 2500 kWh |
| Standard | 26 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **46** | **21,900 kW** | **147,000 kWh** |

Aggregate station-rail charging power: **26,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **210.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 470 kWh | 29.4 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.4 kWh/stop | 564 kW average charger across stops |
| Stops to refill one trainset pack | 51 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 110 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,025 MWh/day | 59,305 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 915 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 210.5 MW / 1,053 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 147 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (105.4 km @ $3.0 M/km) | $316 M |
| Elevated (11.5 km @ $12.0 M/km) | $139 M |
| Elevated-interchange premium (6 sites @ $4.50 M) | $27 M |
| **Civil subtotal** | **$482 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | $600 k | $1.2 M |
| `standard` | 26 | $2.50 M | $65 M |
| `major` | 4 | $4.50 M | $18 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 10 | $12.0 M | $120 M |
| **Stations subtotal** | | | **$232 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 5 | $2.0 M | $10 M |
| **Depots subtotal** | | | **$22 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 162 | $5.60 M | $907 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 648 | $100 k | $65 M |
| High sensitivity check | 648 | $200 k | $130 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 210,516 kW @ $700/kW | $147 M |
| Grid interconnection / PPA tie-in | 210,516 kW @ $100/kW | $21 M |
| Annual generation proxy | 210.5 MW × 5.0 peak-sun-h/day × 365 d/yr | 384.2 GWh/yr |
| **Dedicated solar plant subtotal** | | **$168 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 117.4 km × $0.050 M/km | $5.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $21 M |
| EPC integration + project management (7%) | on subtotal | $121 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $482 M |
| Stations | $232 M |
| Depots | $22 M |
| Rolling stock | $907 M |
| Railway production plant | $65 M |
| Dedicated solar power plant | $168 M |
| Residual train-control wayside + charging microgrids | $26 M |
| EPC overhead (7%) | $121 M |
| **CAPEX total** | **$2.02 bn** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $941 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh sulaymaniyah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$113 M / yr** | $53 |
| Steady-state, low capacity-use (year 6+) | **$2.6 M / yr** | $1 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$65 M / yr** | $30 |
| Lifecycle envelope (yr 1–40, low scenario) | **$659 M cumulative** | $306 |
| Lifecycle envelope (yr 1–40, high scenario) | **$567 M cumulative** | $264 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.83 bn cumulative** | $1,318 |

_Population basis: 2,150,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $62 M / yr → $65 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $1.62 bn | 2.0% | 40 y, 5 y grace | $65 M / yr |
| Government equity (no debt service) | 20% | $405 M | — | — | — |
| **Total** | **100%** | **$2.02 bn** | | | **$65 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $32 M / yr = **$32 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($81 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $36 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $15 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $292 k |
| Traction energy (374.0 GWh / yr) | 59,305 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 40.0 GWh/yr + dedicated solar plant 210.5 MW / 384.2 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $2.5 M |
| Labour (630 FTE) | driverless roster: OCC/remote 98, station/platform 179, passenger service 71, fleet maintenance 127, infrastructure/energy 117, admin/training 38; no train drivers × country median × 12 × engineer-premium 1.4 | $4.0 M |
| **OPEX subtotal** | | **$58 M / yr** |

_Annual service work: 59,305 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 23.4 M train-km / yr (93.5 M car-km / yr). On-site PV covers 40.0 GWh/yr and the dedicated solar plant adds 384.2 GWh/yr against 374.0 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.01 |
| Day pass (3 trips) | $2.58 (15 % bulk discount) |
| Monthly unlimited pass | $30.40 (~8 % of median monthly income) |
| Annual pass | $334.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (614,400 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 23% |
| Annual paid trips | 112.1 M | 179.4 M | 50.8 M |
| Annual paid trips / city resident | 52 | 83 | 24 |
| Farebox revenue | $114 M / yr | $182 M / yr | $52 M / yr |
| Station shop leases | $2.4 M / yr | $2.4 M / yr | $2.4 M / yr |
| Advertising boards | $3.9 M / yr | $3.9 M / yr | $3.9 M / yr |
| **Total revenue** | **$120 M / yr** | **$188 M / yr** | **$58 M / yr** |
| Revenue / OPEX recovery | 207% | 325% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $65 M / yr | $65 M / yr | **$65 M / yr** |
| Operating surplus applied to debt support | -$62 M / yr | -$65 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $2.6 M / yr | $0 k / yr | **$65 M / yr** |
| Operating surplus after OPEX (before debt support) | $62 M / yr | $130 M / yr | $0 / yr |

_Commercial-revenue assumptions: 7,608 m² of station shop/kiosk leases at $30/m²/month and 1,436 advertising boards at $266/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $33 M / yr | $52 M / yr | 16 min/trip × $1.10/h value-of-time proxy |
| Avoided road congestion | $32 M / yr | $52 M / yr | 404 M - 646 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $5.8 M / yr | $9.3 M / yr | 72.7–116.3 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $16 M / yr | $26 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $44 M / yr | $70 M / yr | 20% of paid trips × $1.90 local spend proxy |
| Entertainment / community activity supported | $23 M / yr | $36 M / yr | 11% of paid trips × $1.90 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$153 M / yr** | **$245 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 4 education anchors | 17,596 trips/school day; 3.9 M access-events/yr | 28,154 trips/school day; 6.2 M access-events/yr |
| Healthcare | 8 healthcare anchors | 26,690 trips/day; 9.7 M access-events/yr | 42,703 trips/day; 15.6 M access-events/yr |
| Commerce | 20 major/terminal/interchange nodes | 62,878 trips/trading day; 20.7 M access-events/yr | 100,605 trips/trading day; 33.2 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 32,563 trips/activity day; 9.8 M access-events/yr | 52,101 trips/activity day; 15.6 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $1.05 bn | 52% of $2.02 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $1.68 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $336 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 57,562 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 112.1 M - 179.4 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`sulaymaniyah.toml`](sulaymaniyah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`sulaymaniyah-network-map.png`](sulaymaniyah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`sulaymaniyah.corridor.geojson`](sulaymaniyah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`sulaymaniyah.stations.json`](sulaymaniyah.stations.json) | Machine-readable station list |
| [`sulaymaniyah.design-quality.yaml`](sulaymaniyah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug sulaymaniyah

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug sulaymaniyah \
    --sidecar .cache/osr-pipeline/rasters/sulaymaniyah.grid.json \
    --out-dir designs/.../Sulaymaniyah

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../sulaymaniyah.toml \
    --out designs/.../README.md
```

`scripts/regenerate-sulaymaniyah.sh` chains steps 3 + drift tests into a single command.
