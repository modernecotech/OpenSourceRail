# Aqaba — Urban Rail Network

**Country:** JO · **Population:** 250,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Aqaba rail network on OpenStreetMap](aqaba-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`aqaba.corridor.geojson`](aqaba.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 23 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.7% |
| Route length (double track) | 34.4 km |
| Revenue fleet | 69 × 2-car trainsets |
| Revenue fleet passenger capacity | 16,560 AW2 pax (22,080 AW3 crush) |
| Spare + cold-reserve | 9 × 2-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 15.2 km | 10 | 34 | E Outer ↔ W Outer |
| line-2 |  8.7 km | 7 | 20 | NE Outer ↔ SE Mid |
| line-3 | 10.4 km | 6 | 24 | SE Mid ↔ W Outer |
| **Total** | **34.4 km** | **23 unique** | **78** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 240 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 320 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 16,560 AW2 pax (22,080 AW3 crush) |
| Total fleet capacity | 18,720 AW2 pax (24,960 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 240 AW2 passengers (`tram-2car`)
- **Revenue fleet simultaneous capacity:** 69 × 240 = **16,560 AW2 passengers** (22,080 AW3 crush)
- **Total fleet passenger capacity:** 78 × 240 = **18,720 AW2 passengers** (24,960 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 240 × 20 = **4,800 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 4,800 = **28,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **288,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **230,400 passenger-trips/day**
- **Planning annual paid-trip scenario** (capacity-led): ≈ **42.0 – 67.3 M paid trips/year** at 50%–80% practical capacity utilisation

## Catchment

- City population: **250,000**
- Anchor-weighted coverage: 56.7%
- Catchment population: **≈ 141,750** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 6 | 400 kW | 2500 kWh |
| Standard | 8 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **23** | **13,800 kW** | **95,000 kWh** |

Aggregate station-rail charging power: **14,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **18.6 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 92 kWh | 11.5 km average line length |
| Onboard battery coverage | 2.6× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 10.5 kWh/stop | 630 kW average charger across stops |
| Stops to refill one trainset pack | 23 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 69 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 150 MWh/day | 17,350 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 81 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 18.6 MW / 93 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 95 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (34.2 km @ $3.0 M/km) | $103 M |
| **Civil subtotal** | **$103 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 8 | $2.50 M | $20 M |
| `major` | 6 | $4.50 M | $27 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 3 | $8.0 M | $24 M |
| **Stations subtotal** | | | **$98 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 78 | $2.80 M | $218 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 156 | $100 k | $16 M |
| High sensitivity check | 156 | $200 k | $31 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 18,607 kW @ $700/kW | $13 M |
| Grid interconnection / PPA tie-in | 18,607 kW @ $100/kW | $1.9 M |
| Annual generation proxy | 18.6 MW × 5.0 peak-sun-h/day × 365 d/yr | 34.0 GWh/yr |
| **Dedicated solar plant subtotal** | | **$15 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 34.4 km × $0.050 M/km | $1.7 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $10 M |
| EPC integration + project management (7%) | on subtotal | $33 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $103 M |
| Stations | $98 M |
| Depots | $22 M |
| Rolling stock | $218 M |
| Railway production plant | $16 M |
| Dedicated solar power plant | $15 M |
| Residual train-control wayside + charging microgrids | $12 M |
| EPC overhead (7%) | $33 M |
| **CAPEX total** | **$517 M** |
| Per-route-km | $15 M / km |
| Per-capita (city pop) | $2,068 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh aqaba`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; no climate-development grant assumed); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$29 M / yr** | $116 |
| Steady-state, low capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high capacity-use (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$17 M / yr** | $66 |
| Lifecycle envelope (yr 1–40, low scenario) | **$145 M cumulative** | $579 |
| Lifecycle envelope (yr 1–40, high scenario) | **$145 M cumulative** | $579 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$724 M cumulative** | $2,895 |

_Population basis: 250,000 (city population per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $17 M / yr → $17 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Green concessional loan | 80% | $414 M | 2.0% | 40 y, 5 y grace | $17 M / yr |
| Government equity (no debt service) | 20% | $103 M | — | — | — |
| **Total** | **100%** | **$517 M** | | | **$17 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — green concessional loan $8.3 M / yr = **$8.3 M / yr** total. The base case assumes no climate-development grant. Government equity is drawn across construction ($21 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $8.7 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $4.5 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $86 k |
| Traction energy (54.7 GWh / yr) | 17,350 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 2 cars × 4.0 kWh/car-km; on-site PV 25.2 GWh/yr + dedicated solar plant 18.6 MW / 34.0 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $223 k |
| Labour (322 FTE) | driverless roster: OCC/remote 57, station/platform 92, passenger service 35, fleet maintenance 47, infrastructure/energy 55, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $3.1 M |
| **OPEX subtotal** | | **$17 M / yr** |

_Annual service work: 17,350 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 6.8 M train-km / yr (13.7 M car-km / yr). On-site PV covers 25.2 GWh/yr and the dedicated solar plant adds 34.0 GWh/yr against 54.7 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$580 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.55 |
| Day pass (3 trips) | $3.94 (15 % bulk discount) |
| Monthly unlimited pass | $46.40 (~8 % of median monthly income) |
| Annual pass | $510.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning revenue is capacity-led: annual paid trips are calculated from practical daily service capacity (230,400 trips/day) × 365 service-days × capacity utilisation. The low/high bracket uses 50%–80% of that practical capacity. The operating-neutral column solves the capacity utilisation needed so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Practical service capacity used | 50% | 80% | 9% |
| Annual paid trips | 42.0 M | 67.3 M | 7.6 M |
| Annual paid trips / city resident | 168 | 269 | 30 |
| Farebox revenue | $65 M / yr | $104 M / yr | $12 M / yr |
| Station shop leases | $1.9 M / yr | $1.9 M / yr | $1.9 M / yr |
| Advertising boards | $3.1 M / yr | $3.1 M / yr | $3.1 M / yr |
| **Total revenue** | **$70 M / yr** | **$109 M / yr** | **$17 M / yr** |
| Revenue / OPEX recovery | 420% | 655% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $17 M / yr | $17 M / yr | **$17 M / yr** |
| Operating surplus applied to debt support | -$17 M / yr | -$17 M / yr | **-$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$17 M / yr** |
| Operating surplus after OPEX (before debt support) | $53 M / yr | $92 M / yr | $0 / yr |

_Commercial-revenue assumptions: 3,864 m² of station shop/kiosk leases at $46/m²/month and 740 advertising boards at $406/board/month, with occupancy derates applied._

**Caveats:** The grant-free funding stack, the 8 % operating-neutral fare target, the 50%–80% capacity-utilisation bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Broad economic benefits (planning proxy)

This is a broad-benefit screen, not a bankable benefit-cost analysis. The rows quantify useful channels for discussion — travel time, road externalities, access to essential services, station-area activity, and local CAPEX recirculation — but some channels overlap and should not be treated as audited fiscal revenue. Assumptions are loaded from [`lib/templates/economic-benefits.toml`](../../../../lib/templates/economic-benefits.toml).

### Annual benefit / activity proxy

| Channel | Low scenario | High scenario | Basis |
|---|---:|---:|---|
| Travel time + reliability dividend | $19 M / yr | $30 M / yr | 16 min/trip × $1.67/h value-of-time proxy |
| Avoided road congestion | $5.2 M / yr | $8.3 M / yr | 65 M - 104 M vehicle-km/yr avoided × $0.08/vehicle-km |
| Avoided CO2e | $937 k / yr | $1.5 M / yr | 11.7–18.7 ktCO2e/yr after rail residual-grid emissions × $80/t |
| Local air / noise / safety externalities | $2.6 M / yr | $4.2 M / yr | avoided road vehicle-km × $0.04/vehicle-km |
| Station-area commerce turnover supported | $28 M / yr | $45 M / yr | 23% of paid trips × $2.90 local spend proxy |
| Entertainment / community activity supported | $13 M / yr | $21 M / yr | 11% of paid trips × $2.90 local spend proxy |
| **Annual quantified benefit / activity proxy** | **$68 M / yr** | **$109 M / yr** | sum of rows above; use as a screening envelope, not audited revenue |

### Access to education, healthcare, commerce, and entertainment

| Access channel | Anchored stations / signal | Low scenario | High scenario |
|---|---:|---:|---:|
| Education | 2 education anchors | 6,682 trips/school day; 1.5 M access-events/yr | 10,691 trips/school day; 2.4 M access-events/yr |
| Healthcare | 1 healthcare anchors | 7,718 trips/day; 2.8 M access-events/yr | 12,349 trips/day; 4.5 M access-events/yr |
| Commerce | 15 major/terminal/interchange nodes | 26,321 trips/trading day; 8.7 M access-events/yr | 42,113 trips/trading day; 13.9 M access-events/yr |
| Entertainment / community | 20.5 h/day service span | 12,211 trips/activity day; 3.7 M access-events/yr | 19,538 trips/activity day; 5.9 M access-events/yr |

### Local recirculation of initial CAPEX

| Channel | Value | Basis |
|---|---:|---|
| CAPEX retained in local procurement / payroll | $277 M | 53% of $517 M CAPEX using bucket local-content shares |
| Construction-phase local economic activity | $442 M | retained CAPEX × 1.6 local supplier / wage multiplier |
| Annualised during construction | $88 M / yr | spread across 5 construction / grace years |
| Construction employment supported | 9,933 job-years | retained CAPEX ÷ (4.0 × median annual income) |
| Annual paid-trip capacity used in revenue model | 42.0 M - 67.3 M trips/yr | 50%-80% of practical service capacity |

_Interpretation: the strongest fiscal result remains the farebox + commercial revenue table above. The broader rows here capture welfare, access, avoided external costs, and local supplier circulation that usually matter to a finance ministry, city authority, or development bank even when they do not appear as railway revenue._

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`aqaba.toml`](aqaba.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`aqaba-network-map.png`](aqaba-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`aqaba.corridor.geojson`](aqaba.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`aqaba.stations.json`](aqaba.stations.json) | Machine-readable station list |
| [`aqaba.design-quality.yaml`](aqaba.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug aqaba

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug aqaba \
    --sidecar .cache/osr-pipeline/rasters/aqaba.grid.json \
    --out-dir designs/.../Aqaba

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../aqaba.toml \
    --out designs/.../README.md
```

`scripts/regenerate-aqaba.sh` chains steps 3 + drift tests into a single command.
