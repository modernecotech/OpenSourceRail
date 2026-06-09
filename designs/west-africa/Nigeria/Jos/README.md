# Jos — Urban Rail Network

**Country:** NG · **Population:** 900,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Jos rail network on OpenStreetMap](jos-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`jos.corridor.geojson`](jos.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 40 |
| Interchange stations | 0 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 25.7% |
| Route length (double track) | 53.9 km |
| Revenue fleet | 80 × 3-car trainsets |
| Revenue fleet passenger capacity | 28,800 AW2 pax (38,400 AW3 crush) |
| Spare + cold-reserve | 10 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 22.5 km | 18 | 37 | N Outer ↔ S Outer |
| line-2 | 18.5 km | 13 | 30 | SE Outer ↔ NW Outer |
| line-3 | 12.9 km | 9 | 23 | E Outer ↔ N Mid |
| **Total** | **53.9 km** | **40 unique** | **90** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 28,800 AW2 pax (38,400 AW3 crush) |
| Total fleet capacity | 32,400 AW2 pax (43,200 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 80 × 360 = **28,800 AW2 passengers** (38,400 AW3 crush)
- **Total fleet passenger capacity:** 90 × 360 = **32,400 AW2 passengers** (43,200 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **63.1 – 100.9 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **900,000**
- Anchor-weighted coverage: 25.7%
- Catchment population: **≈ 231,300** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Major | 25 | 400 kW | 2500 kWh |
| Standard | 9 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **40** | **20,200 kW** | **135,500 kWh** |

Aggregate station-rail charging power: **23,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **57.9 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 216 kWh | 18.0 km average line length |
| Onboard battery coverage | 1.7× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.6 kWh/stop | 575 kW average charger across stops |
| Stops to refill one trainset pack | 38 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 101 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 353 MWh/day | 27,212 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 252 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 57.9 MW / 289 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 136 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (50.0 km @ $3.0 M/km) | $150 M |
| Elevated (3.4 km @ $12.0 M/km) | $40 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$195 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 9 | $2.50 M | $22 M |
| `major` | 25 | $4.50 M | $112 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| **Stations subtotal** | | | **$162 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 90 | $4.20 M | $378 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 270 | $100 k | $27 M |
| High sensitivity check | 270 | $200 k | $54 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 57,885 kW @ $700/kW | $41 M |
| Grid interconnection / PPA tie-in | 57,885 kW @ $100/kW | $5.8 M |
| Annual generation proxy | 57.9 MW × 5.0 peak-sun-h/day × 365 d/yr | 105.6 GWh/yr |
| **Dedicated solar plant subtotal** | | **$46 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 53.9 km × $0.050 M/km | $2.7 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $17 M |
| EPC integration + project management (7%) | on subtotal | $56 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $195 M |
| Stations | $162 M |
| Depots | $22 M |
| Rolling stock | $378 M |
| Railway production plant | $27 M |
| Dedicated solar power plant | $46 M |
| Residual train-control wayside + charging microgrids | $20 M |
| EPC overhead (7%) | $56 M |
| **CAPEX total** | **$906 M** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $1,007 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh jos`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$40 M / yr** | $45 |
| Steady-state, low capacity-use (year 8+) | **$23 M / yr** | $26 |
| Steady-state, high capacity-use (year 8+) | **$5.3 M / yr** | $6 |
| Steady-state, operating-neutral revenue case | **$30 M / yr** | $34 |
| Lifecycle envelope (yr 1–40, low scenario) | **$1.04 bn cumulative** | $1,157 |
| Lifecycle envelope (yr 1–40, high scenario) | **$459 M cumulative** | $510 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.28 bn cumulative** | $1,423 |

_Population basis: 900,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $7.2 M / yr → $25 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $725 M | 2.0% | 40 y, 7 y grace | $30 M / yr |
| Government equity (no debt service) | 20% | $181 M | — | — | — |
| **Total** | **100%** | **$906 M** | | | **$30 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $15 M / yr = **$15 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($26 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $15 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $7.6 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $133 k |
| Traction energy (128.7 GWh / yr) | 27,212 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 36.9 GWh/yr + dedicated solar plant 57.9 MW / 105.6 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $695 k |
| Labour (424 FTE) | driverless roster: OCC/remote 61, station/platform 146, passenger service 44, fleet maintenance 63, infrastructure/energy 74, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $1.2 M |
| **OPEX subtotal** | | **$25 M / yr** |

_Annual service work: 27,212 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 10.7 M train-km / yr (32.2 M car-km / yr). On-site PV covers 36.9 GWh/yr and the dedicated solar plant adds 105.6 GWh/yr against 128.7 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$175 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.47 |
| Day pass (3 trips) | $1.19 (15 % bulk discount) |
| Monthly unlimited pass | $14.00 (~8 % of median monthly income) |
| Annual pass | $154.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (345,600 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 38% |
| Annual paid trips | 63.1 M | 100.9 M | 47.6 M |
| Annual paid trips / city resident | 70 | 112 | 53 |
| Farebox revenue | $29 M / yr | $47 M / yr | $22 M / yr |
| Station shop leases | $995 k / yr | $995 k / yr | $995 k / yr |
| Advertising boards | $1.6 M / yr | $1.6 M / yr | $1.6 M / yr |
| **Total revenue** | **$32 M / yr** | **$50 M / yr** | **$25 M / yr** |
| Revenue / OPEX recovery | 129% | 200% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $30 M / yr | $30 M / yr | **$30 M / yr** |
| Operating surplus applied to debt support | -$7.2 M / yr | -$25 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $23 M / yr | $5.3 M / yr | **$30 M / yr** |
| Operating surplus after OPEX (before debt support) | $7.2 M / yr | $25 M / yr | $0 / yr |

_Commercial-revenue assumptions: 6,728 m² of station shop/kiosk leases at $14/m²/month and 1,272 advertising boards at $122/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $8.5 M / yr | $14 M / yr | 16 min/trip × $0.50/h value-of-time proxy |
| Avoided road congestion | $12 M / yr | $20 M / yr | 153 M - 245 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $2.2 M / yr | $3.5 M / yr | 27.5–44.1 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $6.1 M / yr | $9.8 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $23 M / yr | $37 M / yr | 24% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $10 M / yr | $16 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$62 M / yr** | **$99 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 4 education anchors | 10,305 trips/school day; 2.3 M access-events/yr | 16,488 trips/school day; 3.6 M access-events/yr |
| Healthcare | 16 healthcare anchors | 20,925 trips/day; 7.6 M access-events/yr | 33,479 trips/day; 12.2 M access-events/yr |
| Commerce | 31 major/terminal/interchange nodes | 41,710 trips/trading day; 13.8 M access-events/yr | 66,735 trips/trading day; 22.0 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 18,511 trips/activity day; 5.6 M access-events/yr | 29,618 trips/activity day; 8.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $481 M | 53% of $906 M CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $769 M | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $110 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 57,221 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 63.1 M - 100.9 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`jos.toml`](jos.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`jos-network-map.png`](jos-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`jos.corridor.geojson`](jos.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`jos.stations.json`](jos.stations.json) | Machine-readable station list |
| [`jos.design-quality.yaml`](jos.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug jos

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug jos \
    --sidecar .cache/osr-pipeline/rasters/jos.grid.json \
    --out-dir designs/.../Jos

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../jos.toml \
    --out designs/.../README.md
```

`scripts/regenerate-jos.sh` chains steps 3 + drift tests into a single command.
