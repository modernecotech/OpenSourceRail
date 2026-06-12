# Samawah — Urban Rail Network

**Country:** IQ · **Population:** 373,770

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Samawah rail network on OpenStreetMap](samawah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`samawah.corridor.geojson`](samawah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 31 |
| Interchange-class stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.6% |
| Route length (double track) | 58.4 km |
| Revenue fleet | 86 × 3-car trainsets |
| Revenue fleet passenger capacity | 30,960 AW2 pax (41,280 AW3 crush) |
| Spare + cold-reserve | 10 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 25.6 km | 13 | 41 | SW Outer ↔ N Mid |
| line-2 | 21.8 km | 10 | 36 | SE Mid ↔ NW Outer |
| line-3 | 11.0 km | 8 | 19 | W Inner ↔ SE Mid |
| **Total** | **58.4 km** | **31 unique** | **96** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 30,960 AW2 pax (41,280 AW3 crush) |
| Total fleet capacity | 34,560 AW2 pax (46,080 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 86 × 360 = **30,960 AW2 passengers** (41,280 AW3 crush)
- **Total fleet passenger capacity:** 96 × 360 = **34,560 AW2 passengers** (46,080 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Scheduled one-way train journeys:** **1,515/day**
- **Daily theoretical capacity from timetable:** 1,515 scheduled one-way train journeys/day × 360 AW2 pax = **545,400 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **436,320 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **79.6 – 127.4 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **373,770**
- Anchor-weighted coverage: 56.6%
- Catchment population: **≈ 211,553** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 11 | 400 kW | 2500 kWh |
| Standard | 9 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **29** | **16,100 kW** | **109,500 kWh** |

Aggregate station-rail charging power: **18,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **69.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 234 kWh | 19.5 km average line length |
| Longest one-way line energy | 307 kWh | 25.6 km longest line × 12.0 kWh/km |
| Onboard battery adequacy | 1.2× longest line run | Fail: 288 kWh after 20% reserve, 19 kWh short on the longest line |
| Average 60 s dwell charge | 9.7 kWh/stop | 581 kW average charger across stops |
| Stops to refill one trainset pack | 37 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 80 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled one-way train journeys | 1,515 / day | Train departures across both directions and all lines |
| Scheduled train journey-km | 29,515 train-km/day | One-way train journeys × route length |
| Annual service work | 11.6 M train-km/yr | Includes 108% depot/deadhead factor |
| Scheduled traction demand | 383 MWh/day | 34.9 M car-km/yr × 4.0 kWh/car-km |
| On-site PV shortfall before solar plant | 302 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 69.5 MW / 347 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 110 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **locally built rolling stock at about $0.8 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line includes direct material, local production labour, shop overhead, nominal per-train QA/acceptance, and modest local handover logistics. Fixtures, tooling, and production-readiness live in the separate railway production-plant setup line at $100 k per vehicle/car module, with $200 k retained as the high sensitivity check; warranty, spares, and routine commissioning support are OPEX rather than repeated train CAPEX. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (55.9 km @ $3.0 M/km) | $168 M |
| Elevated (2.3 km @ $12.0 M/km) | $28 M |
| Elevated-interchange premium (2 sites @ $4.50 M) | $9.0 M |
| **Civil subtotal** | **$205 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | $600 k | $1.2 M |
| `standard` | 9 | $2.50 M | $22 M |
| `major` | 11 | $4.50 M | $50 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$137 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 5 | $2.0 M | $10 M |
| **Depots subtotal** | | | **$22 M** |

### Rolling stock

Rolling stock is costed at the **local-owner production planning unit: $0.8 M per self-contained car**. The raw 3-car light-metro BOM floor remains 592,840 USD direct material plus 35 % assembly allowance = 800,334 USD per consist. City CAPEX then adds local production labour and shop overhead, plus small per-train QA/acceptance and handover allowances. Fixtures, tooling, and production-readiness are carried in the railway production plant line below. Warranty, initial spares, and routine commissioning support are treated as operating costs. Motors, sensors, train-control computers, onboard batteries, roof PV, and charge hardware appear here ONLY — never re-billed elsewhere in the city cost stack.

| Per-car cost bucket | Basis | Cost |
|---|---|---|
| Direct material BOM floor | Welded frame, panels, glazing, doors, bogies, traction, batteries, HVAC, electronics, interiors | $267 k |
| Production labour + shop overhead | Cut/bend/weld, fit-out, harnessing, paint, factory supervision, utilities, rework reserve | $420 k |
| Per-train QA + acceptance evidence | Dimensional QA, weld records, functional test logs, acceptance run dossier | $50 k |
| Local handover logistics | Local movement, manuals/training handover, site test support; warranty/spares stay in OPEX | $63 k |
| **Total per car** | Local-owner production planning unit | **$800 k** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `light-metro-3car` (revenue + spare + cold reserve) | 96 | $2.40 M | $230 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, fixtures, plant services, production-readiness, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 288 | $100 k | $29 M |
| High sensitivity check | 288 | $200 k | $58 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 69,463 kW @ $700/kW | $49 M |
| Grid interconnection / PPA tie-in | 69,463 kW @ $100/kW | $6.9 M |
| Annual generation proxy | 69.5 MW × 5.0 peak-sun-h/day × 365 d/yr | 126.8 GWh/yr |
| **Dedicated solar plant subtotal** | | **$56 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 58.4 km × $0.050 M/km | $2.9 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $13 M |
| EPC integration + project management (7%) | on subtotal | $45 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $205 M |
| Stations | $137 M |
| Depots | $22 M |
| Rolling stock | $230 M |
| Railway production plant | $29 M |
| Dedicated solar power plant | $56 M |
| Residual train-control wayside + charging microgrids | $16 M |
| EPC overhead (7%) | $45 M |
| **CAPEX total** | **$739 M** |
| Per-route-km | $13 M / km |
| Per-capita (city pop) | $1,978 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh samawah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$41 M / yr** | $111 |
| Steady-state, low capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$24 M / yr** | $63 |
| Lifecycle envelope (yr 1–40, low scenario) | **$207 M cumulative** | $554 |
| Lifecycle envelope (yr 1–40, high scenario) | **$207 M cumulative** | $554 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.04 bn cumulative** | $2,770 |

_Population basis: 373,770 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $24 M / yr → $24 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Candidate climate/MDB concessional debt (unconfirmed) | 80% | $592 M | 2.0% | 40 y, 5 y grace | $24 M / yr |
| Government equity (no debt service) | 20% | $148 M | — | — | — |
| **Total** | **100%** | **$739 M** | | | **$24 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — candidate climate/MDB debt $12 M / yr = **$12 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($30 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

_Loan availability note: this is a finance placeholder, not a committed lender offer. Plausible providers would be a national government borrowing through an MDB or a climate fund accredited entity, such as the World Bank/IBRD, Islamic Development Bank, Climate Investment Funds, or Green Climate Fund channels. Official GCF policy allows grants and concessional loans, and World Bank/CIF material documents below-market climate finance, but this project still needs a lender mandate, eligibility screen, and signed term sheet before the 2.0% / 40-year assumption can be treated as real. Evidence anchors: [GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), [GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), [World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), [CIF funding instruments](https://www.cif.org/cif-funding), and [IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $9.2 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $7.3 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $146 k |
| Traction energy (139.6 GWh / yr) | 29,515 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 29.4 GWh/yr + dedicated solar plant 69.5 MW / 126.8 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $834 k |
| Labour (410 FTE) | driverless roster: OCC/remote 65, station/platform 116, passenger service 52, fleet maintenance 68, infrastructure/energy 73, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $2.6 M |
| **OPEX subtotal** | | **$20 M / yr** |

_Annual service work: 29,515 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 11.6 M train-km / yr (34.9 M car-km / yr). On-site PV covers 29.4 GWh/yr and the dedicated solar plant adds 126.8 GWh/yr against 139.6 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.01 |
| Day pass (3 trips) | $2.58 (15 % bulk discount) |
| Monthly unlimited pass | $30.40 (~8 % of median monthly income) |
| Annual pass | $334.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (436,320 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 10% |
| Annual paid trips | 79.6 M | 127.4 M | 15.6 M |
| Annual paid trips / city resident | 213 | 341 | 42 |
| Farebox revenue | $81 M / yr | $129 M / yr | $16 M / yr |
| Station shop leases | $1.6 M / yr | $1.6 M / yr | $1.6 M / yr |
| Advertising boards | $2.6 M / yr | $2.6 M / yr | $2.6 M / yr |
| **Total revenue** | **$85 M / yr** | **$133 M / yr** | **$20 M / yr** |
| Revenue / OPEX recovery | 423% | 664% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $24 M / yr | $24 M / yr | **$24 M / yr** |
| Operating surplus applied to debt support | -$24 M / yr | -$24 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$24 M / yr** |
| Operating surplus after OPEX (before debt support) | $65 M / yr | $113 M / yr | $0 / yr |

_Commercial-revenue assumptions: 5,096 m² of station shop/kiosk leases at $30/m²/month and 968 advertising boards at $266/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $23 M / yr | $37 M / yr | 16 min/trip × $1.10/h value-of-time proxy |
| Avoided road congestion | $17 M / yr | $27 M / yr | 209 M - 335 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $3.0 M / yr | $4.8 M / yr | 37.7–60.3 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $8.4 M / yr | $13 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $34 M / yr | $55 M / yr | 23% of paid trips × $1.90 local spend proxy |
| Entertainment / community activity supported | $16 M / yr | $26 M / yr | 11% of paid trips × $1.90 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$102 M / yr** | **$163 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 2 education anchors | 10,775 trips/school day; 2.4 M access-events/yr | 17,240 trips/school day; 3.8 M access-events/yr |
| Healthcare | 3 healthcare anchors | 15,480 trips/day; 5.7 M access-events/yr | 24,768 trips/day; 9.0 M access-events/yr |
| Commerce | 20 major/terminal/interchange nodes | 49,684 trips/trading day; 16.4 M access-events/yr | 79,495 trips/trading day; 26.2 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 23,125 trips/activity day; 6.9 M access-events/yr | 37,000 trips/activity day; 11.1 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $402 M | 54% of $739 M CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $642 M | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $128 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 22,014 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 79.6 M - 127.4 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`samawah.toml`](samawah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`samawah-network-map.png`](samawah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`samawah.corridor.geojson`](samawah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`samawah.stations.json`](samawah.stations.json) | Machine-readable station list |
| [`samawah.design-quality.yaml`](samawah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug samawah

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug samawah \
    --sidecar .cache/osr-pipeline/rasters/samawah.grid.json \
    --out-dir designs/.../Samawah

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../samawah.toml \
    --out designs/.../README.md
```

`scripts/regenerate-samawah.sh` chains steps 3 + drift tests into a single command.
