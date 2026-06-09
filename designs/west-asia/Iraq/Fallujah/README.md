# Fallujah — Urban Rail Network

**Country:** IQ · **Population:** 360,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Fallujah rail network on OpenStreetMap](fallujah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`fallujah.corridor.geojson`](fallujah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 28 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 57.0% |
| Route length (double track) | 45.9 km |
| Revenue fleet | 69 × 3-car trainsets |
| Revenue fleet passenger capacity | 24,840 AW2 pax (33,120 AW3 crush) |
| Spare + cold-reserve | 9 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 20.5 km | 10 | 34 | SE Mid ↔ NW Outer |
| line-2 | 15.0 km | 10 | 26 | E Mid ↔ W Mid |
| line-3 | 10.4 km | 8 | 18 | W Inner ↔ SE Mid |
| **Total** | **45.9 km** | **28 unique** | **78** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 24,840 AW2 pax (33,120 AW3 crush) |
| Total fleet capacity | 28,080 AW2 pax (37,440 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 69 × 360 = **24,840 AW2 passengers** (33,120 AW3 crush)
- **Total fleet passenger capacity:** 78 × 360 = **28,080 AW2 passengers** (37,440 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **63.1 – 100.9 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **360,000**
- Anchor-weighted coverage: 57.0%
- Catchment population: **≈ 205,199** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 12 | 400 kW | 2500 kWh |
| Standard | 6 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **27** | **15,600 kW** | **106,000 kWh** |

Aggregate station-rail charging power: **16,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **51.2 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 184 kWh | 15.3 km average line length |
| Onboard battery coverage | 2.0× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 10.0 kWh/stop | 598 kW average charger across stops |
| Stops to refill one trainset pack | 36 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 78 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 301 MWh/day | 23,193 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 223 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 51.2 MW / 256 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 106 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (42.5 km @ $3.0 M/km) | $127 M |
| Elevated (3.3 km @ $12.0 M/km) | $40 M |
| Elevated-interchange premium (2 sites @ $4.50 M) | $9.0 M |
| **Civil subtotal** | **$176 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 6 | $2.50 M | $15 M |
| `major` | 12 | $4.50 M | $54 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$133 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 78 | $4.20 M | $328 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 234 | $100 k | $23 M |
| High sensitivity check | 234 | $200 k | $47 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 51,193 kW @ $700/kW | $36 M |
| Grid interconnection / PPA tie-in | 51,193 kW @ $100/kW | $5.1 M |
| Annual generation proxy | 51.2 MW × 5.0 peak-sun-h/day × 365 d/yr | 93.4 GWh/yr |
| **Dedicated solar plant subtotal** | | **$41 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 45.9 km × $0.050 M/km | $2.3 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $13 M |
| EPC integration + project management (7%) | on subtotal | $49 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $176 M |
| Stations | $133 M |
| Depots | $22 M |
| Rolling stock | $328 M |
| Railway production plant | $23 M |
| Dedicated solar power plant | $41 M |
| Residual train-control wayside + charging microgrids | $15 M |
| EPC overhead (7%) | $49 M |
| **CAPEX total** | **$788 M** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $2,188 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh fallujah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$44 M / yr** | $123 |
| Steady-state, low capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$25 M / yr** | $70 |
| Lifecycle envelope (yr 1–40, low scenario) | **$221 M cumulative** | $613 |
| Lifecycle envelope (yr 1–40, high scenario) | **$221 M cumulative** | $613 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.10 bn cumulative** | $3,064 |

_Population basis: 360,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $25 M / yr → $25 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $630 M | 2.0% | 40 y, 5 y grace | $25 M / yr |
| Government equity (no debt service) | 20% | $158 M | — | — | — |
| **Total** | **100%** | **$788 M** | | | **$25 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $13 M / yr = **$13 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($32 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $13 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $6.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $115 k |
| Traction energy (109.7 GWh / yr) | 23,193 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 28.5 GWh/yr + dedicated solar plant 51.2 MW / 93.4 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $614 k |
| Labour (368 FTE) | driverless roster: OCC/remote 57, station/platform 113, passenger service 44, fleet maintenance 54, infrastructure/energy 64, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $2.3 M |
| **OPEX subtotal** | | **$23 M / yr** |

_Annual service work: 23,193 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 9.1 M train-km / yr (27.4 M car-km / yr). On-site PV covers 28.5 GWh/yr and the dedicated solar plant adds 93.4 GWh/yr against 109.7 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.01 |
| Day pass (3 trips) | $2.58 (15 % bulk discount) |
| Monthly unlimited pass | $30.40 (~8 % of median monthly income) |
| Annual pass | $334.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (345,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 15% |
| Annual paid trips | 63.1 M | 100.9 M | 18.4 M |
| Annual paid trips / city resident | 175 | 280 | 51 |
| Farebox revenue | $64 M / yr | $102 M / yr | $19 M / yr |
| Station shop leases | $1.6 M / yr | $1.6 M / yr | $1.6 M / yr |
| Advertising boards | $2.6 M / yr | $2.6 M / yr | $2.6 M / yr |
| **Total revenue** | **$68 M / yr** | **$106 M / yr** | **$23 M / yr** |
| Revenue / OPEX recovery | 299% | 467% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $25 M / yr | $25 M / yr | **$25 M / yr** |
| Operating surplus applied to debt support | -$25 M / yr | -$25 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$25 M / yr** |
| Operating surplus after OPEX (before debt support) | $45 M / yr | $84 M / yr | $0 / yr |

_Commercial-revenue assumptions: 5,072 m² of station shop/kiosk leases at $30/m²/month and 952 advertising boards at $266/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $18 M / yr | $29 M / yr | 16 min/trip × $1.10/h value-of-time proxy |
| Avoided road congestion | $10 M / yr | $17 M / yr | 130 M - 208 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $1.9 M / yr | $3.0 M / yr | 23.4–37.5 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $5.2 M / yr | $8.3 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $29 M / yr | $46 M / yr | 24% of paid trips × $1.90 local spend proxy |
| Entertainment / community activity supported | $13 M / yr | $20 M / yr | 11% of paid trips × $1.90 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$77 M / yr** | **$124 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 2 education anchors | 10,022 trips/school day; 2.2 M access-events/yr | 16,036 trips/school day; 3.5 M access-events/yr |
| Healthcare | 5 healthcare anchors | 16,416 trips/day; 6.0 M access-events/yr | 26,266 trips/day; 9.6 M access-events/yr |
| Commerce | 21 major/terminal/interchange nodes | 41,256 trips/trading day; 13.6 M access-events/yr | 66,010 trips/trading day; 21.8 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 18,360 trips/activity day; 5.5 M access-events/yr | 29,376 trips/activity day; 8.8 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $418 M | 53% of $788 M CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $669 M | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $134 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 22,929 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 63.1 M - 100.9 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`fallujah.toml`](fallujah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`fallujah-network-map.png`](fallujah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`fallujah.corridor.geojson`](fallujah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`fallujah.stations.json`](fallujah.stations.json) | Machine-readable station list |
| [`fallujah.design-quality.yaml`](fallujah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug fallujah

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug fallujah \
    --sidecar .cache/osr-pipeline/rasters/fallujah.grid.json \
    --out-dir designs/.../Fallujah

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../fallujah.toml \
    --out designs/.../README.md
```

`scripts/regenerate-fallujah.sh` chains steps 3 + drift tests into a single command.
