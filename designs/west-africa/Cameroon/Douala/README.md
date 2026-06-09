# Douala — Urban Rail Network

**Country:** CM · **Population:** 3,900,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Douala rail network on OpenStreetMap](douala-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`douala.corridor.geojson`](douala.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 128 |
| Interchange stations | 15 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 37.0% |
| Route length (double track) | 228.0 km |
| Revenue fleet | 273 × 6-car trainsets |
| Revenue fleet passenger capacity | 196,560 AW2 pax (262,080 AW3 crush) |
| Spare + cold-reserve | 31 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.8 km | 23 | 56 | SE Mid ↔ NW Outer |
| line-2 | 39.7 km | 21 | 53 | SE Mid ↔ NW Outer |
| line-3 | 42.1 km | 22 | 57 | NE Mid ↔ SW Outer |
| line-4 | 25.8 km | 15 | 36 | NW Mid ↔ E Inner |
| line-5 | 78.6 km | 48 | 102 | NW Mid ↔ NW Mid |
| **Total** | **228.0 km** | **128 unique** | **304** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 196,560 AW2 pax (262,080 AW3 crush) |
| Total fleet capacity | 218,880 AW2 pax (291,840 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 273 × 720 = **196,560 AW2 passengers** (262,080 AW3 crush)
- **Total fleet passenger capacity:** 304 × 720 = **218,880 AW2 passengers** (291,840 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 14,400 = **144,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,440,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,152,000 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **210.2 – 336.4 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **3,900,000**
- Anchor-weighted coverage: 37.0%
- Catchment population: **≈ 1,443,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 15 | 500 kW | 3000 kWh |
| Major | 79 | 400 kW | 2500 kWh |
| Standard | 24 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **126** | **54,800 kW** | **351,500 kWh** |

Aggregate station-rail charging power: **67,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **623.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,094 kWh | 45.6 km average line length |
| Onboard battery coverage | 0.7× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 529 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 274 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 2,985 MWh/day | 115,159 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 2,711 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 623.5 MW / 3,118 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 352 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (193.3 km @ $3.0 M/km) | $580 M |
| Elevated (31.4 km @ $12.0 M/km) | $377 M |
| Elevated-interchange premium (5 sites @ $4.50 M) | $22 M |
| **Civil subtotal** | **$979 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $600 k | $1.8 M |
| `standard` | 24 | $2.50 M | $60 M |
| `major` | 79 | $4.50 M | $356 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 15 | $12.0 M | $180 M |
| **Stations subtotal** | | | **$634 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 304 | $8.40 M | $2.55 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1824 | $100 k | $182 M |
| High sensitivity check | 1824 | $200 k | $365 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 623,512 kW @ $700/kW | $436 M |
| Grid interconnection / PPA tie-in | 623,512 kW @ $100/kW | $62 M |
| Annual generation proxy | 623.5 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,137.9 GWh/yr |
| **Dedicated solar plant subtotal** | | **$499 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 228.0 km × $0.050 M/km | $11 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $59 M |
| EPC integration + project management (7%) | on subtotal | $311 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $979 M |
| Stations | $634 M |
| Depots | $26 M |
| Rolling stock | $2.55 bn |
| Railway production plant | $182 M |
| Dedicated solar power plant | $499 M |
| Residual train-control wayside + charging microgrids | $70 M |
| EPC overhead (7%) | $311 M |
| **CAPEX total** | **$5.25 bn** |
| Per-route-km | $23 M / km |
| Per-capita (city pop) | $1,347 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh douala`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$234 M / yr** | $60 |
| Steady-state, low capacity-use (year 8+) | **$212 M / yr** | $54 |
| Steady-state, high capacity-use (year 8+) | **$151 M / yr** | $39 |
| Steady-state, operating-neutral revenue case | **$175 M / yr** | $45 |
| Lifecycle envelope (yr 1–40, low scenario) | **$8.63 bn cumulative** | $2,212 |
| Lifecycle envelope (yr 1–40, high scenario) | **$6.63 bn cumulative** | $1,700 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$7.42 bn cumulative** | $1,903 |

_Population basis: 3,900,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $37 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $24 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $4.20 bn | 2.0% | 40 y, 7 y grace | $175 M / yr |
| Government equity (no debt service) | 20% | $1.05 bn | — | — | — |
| **Total** | **100%** | **$5.25 bn** | | | **$175 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $84 M / yr = **$84 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($150 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $102 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $33 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $562 k |
| Traction energy (1089.5 GWh / yr) | 115,159 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 100.0 GWh/yr + dedicated solar plant 623.5 MW / 1137.9 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $7.5 M |
| Labour (1,333 FTE) | driverless roster: OCC/remote 171, station/platform 528, passenger service 120, fleet maintenance 243, infrastructure/energy 225, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $4.0 M |
| **OPEX subtotal** | | **$147 M / yr** |

_Annual service work: 115,159 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 45.4 M train-km / yr (272.4 M car-km / yr). On-site PV covers 100.0 GWh/yr and the dedicated solar plant adds 1137.9 GWh/yr against 1089.5 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$180 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.48 |
| Day pass (3 trips) | $1.22 (15 % bulk discount) |
| Monthly unlimited pass | $14.40 (~8 % of median monthly income) |
| Annual pass | $158.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (1,152,000 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 68% |
| Annual paid trips | 210.2 M | 336.4 M | 286.3 M |
| Annual paid trips / city resident | 54 | 86 | 73 |
| Farebox revenue | $101 M / yr | $161 M / yr | $137 M / yr |
| Station shop leases | $3.8 M / yr | $3.8 M / yr | $3.8 M / yr |
| Advertising boards | $5.8 M / yr | $5.8 M / yr | $5.8 M / yr |
| **Total revenue** | **$110 M / yr** | **$171 M / yr** | **$147 M / yr** |
| Revenue / OPEX recovery | 75% | 116% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $212 M / yr | $175 M / yr | **$175 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$24 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $212 M / yr | $151 M / yr | **$175 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $24 M / yr | $0 / yr |

_Commercial-revenue assumptions: 24,776 m² of station shop/kiosk leases at $14/m²/month and 4,508 advertising boards at $126/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $29 M / yr | $47 M / yr | 16 min/trip × $0.52/h value-of-time proxy |
| Avoided road congestion | $61 M / yr | $97 M / yr | 757 M - 1,211 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $11 M / yr | $17 M / yr | 136.2–218.0 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $30 M / yr | $48 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $77 M / yr | $123 M / yr | 24% of paid trips × $1.50 local spend proxy |
| Entertainment / community activity supported | $34 M / yr | $54 M / yr | 11% of paid trips × $1.50 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$242 M / yr** | **$387 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 3 education anchors | 27,592 trips/school day; 6.1 M access-events/yr | 44,147 trips/school day; 9.7 M access-events/yr |
| Healthcare | 6 healthcare anchors | 41,641 trips/day; 15.2 M access-events/yr | 66,625 trips/day; 24.3 M access-events/yr |
| Commerce | 102 major/terminal/interchange nodes | 140,355 trips/trading day; 46.3 M access-events/yr | 224,568 trips/trading day; 74.1 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 62,145 trips/activity day; 18.6 M access-events/yr | 99,432 trips/activity day; 29.8 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $2.67 bn | 51% of $5.25 bn CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $4.27 bn | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $610 M / yr | spread across 7 construction / grace years |
| Construction employment supported | 308,759 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 210.2 M - 336.4 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`douala.toml`](douala.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`douala-network-map.png`](douala-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`douala.corridor.geojson`](douala.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`douala.stations.json`](douala.stations.json) | Machine-readable station list |
| [`douala.design-quality.yaml`](douala.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug douala

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug douala \
    --sidecar .cache/osr-pipeline/rasters/douala.grid.json \
    --out-dir designs/.../Douala

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../douala.toml \
    --out designs/.../README.md
```

`scripts/regenerate-douala.sh` chains steps 3 + drift tests into a single command.
