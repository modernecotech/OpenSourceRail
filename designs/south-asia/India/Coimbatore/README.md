# Coimbatore — Urban Rail Network

**Country:** IN · **Population:** 3,084,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Coimbatore rail network on OpenStreetMap](coimbatore-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`coimbatore.corridor.geojson`](coimbatore.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 120 |
| Interchange stations | 22 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 31.2% |
| Route length (double track) | 267.8 km |
| Revenue fleet | 318 × 6-car trainsets |
| Revenue fleet passenger capacity | 228,960 AW2 pax (305,280 AW3 crush) |
| Spare + cold-reserve | 34 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 52.2 km | 20 | 69 | NE Outer ↔ SW Outer |
| line-2 | 47.9 km | 23 | 63 | N Outer ↔ S Outer |
| line-3 | 36.9 km | 20 | 50 | W Mid ↔ E Outer |
| line-4 | 37.3 km | 19 | 50 | N Outer ↔ S Mid |
| line-5 | 93.4 km | 39 | 120 | W Mid ↔ W Mid |
| **Total** | **267.8 km** | **120 unique** | **352** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 228,960 AW2 pax (305,280 AW3 crush) |
| Total fleet capacity | 253,440 AW2 pax (337,920 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 318 × 720 = **228,960 AW2 passengers** (305,280 AW3 crush)
- **Total fleet passenger capacity:** 352 × 720 = **253,440 AW2 passengers** (337,920 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 14,400 = **144,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,440,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,152,000 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **481,104 – 865,986 paid trips/day** (240,552 – 432,993 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **3,084,000**
- Anchor-weighted coverage: 31.2%
- Catchment population: **≈ 962,208** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 22 | 500 kW | 3000 kWh |
| Major | 24 | 400 kW | 2500 kWh |
| Standard | 67 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **121** | **49,200 kW** | **321,000 kWh** |

Aggregate station-rail charging power: **64,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **749.6 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,285 kWh | 53.6 km average line length |
| Onboard battery coverage | 0.6× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 9.0 kWh/stop | 538 kW average charger across stops |
| Stops to refill one trainset pack | 80 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 246 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 3,505 MWh/day | 135,223 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 3,259 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 749.6 MW / 3,748 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 321 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (241.8 km @ $3.0 M/km) | $725 M |
| Elevated (25.2 km @ $12.0 M/km) | $302 M |
| Elevated-interchange premium (11 sites @ $4.50 M) | $50 M |
| **Civil subtotal** | **$1.08 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 67 | $2.50 M | $168 M |
| `major` | 24 | $4.50 M | $108 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 22 | $12.0 M | $264 M |
| **Stations subtotal** | | | **$576 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 352 | $8.40 M | $2.96 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 2112 | $100 k | $211 M |
| High sensitivity check | 2112 | $200 k | $422 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 749,564 kW @ $700/kW | $525 M |
| Grid interconnection / PPA tie-in | 749,564 kW @ $100/kW | $75 M |
| Annual generation proxy | 749.6 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,368.0 GWh/yr |
| **Dedicated solar plant subtotal** | | **$600 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 267.8 km × $0.050 M/km | $13 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $51 M |
| EPC integration + project management (7%) | on subtotal | $344 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.08 bn |
| Stations | $576 M |
| Depots | $26 M |
| Rolling stock | $2.96 bn |
| Railway production plant | $211 M |
| Dedicated solar power plant | $600 M |
| Residual train-control wayside + charging microgrids | $64 M |
| EPC overhead (7%) | $344 M |
| **CAPEX total** | **$5.85 bn** |
| Per-route-km | $22 M / km |
| Per-capita (city pop) | $1,898 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh coimbatore`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$176 M / yr** | $57 |
| Steady-state, low-ridership (year 6+) | **$166 M / yr** | $54 |
| Steady-state, high-ridership (year 6+) | **$80 M / yr** | $26 |
| Steady-state, operating-neutral revenue case | **$117 M / yr** | $38 |
| Lifecycle envelope (yr 1–40, low scenario) | **$6.70 bn cumulative** | $2,171 |
| Lifecycle envelope (yr 1–40, high scenario) | **$3.68 bn cumulative** | $1,194 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$4.98 bn cumulative** | $1,614 |

_Population basis: 3,084,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $49 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $37 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $2.34 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $2.93 bn | 2.0% | 40 y, 5 y grace | $117 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 7.2% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $585 M | — | — | — |
| **Total** | **100%** | **$5.85 bn** | | | **$117 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $59 M / yr + fallback bonds $0 k / yr = **$59 M / yr** total. The $2.34 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($117 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $118 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $34 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $667 k |
| Traction energy (1279.3 GWh / yr) | 135,223 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 89.8 GWh/yr + dedicated solar plant 749.6 MW / 1368.0 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $9.0 M |
| Labour (1,330 FTE) | driverless roster: OCC/remote 191, station/platform 446, passenger service 114, fleet maintenance 284, infrastructure/energy 249, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $5.1 M |
| **OPEX subtotal** | | **$167 M / yr** |

_Annual service work: 135,223 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 53.3 M train-km / yr (319.8 M car-km / yr). On-site PV covers 89.8 GWh/yr and the dedicated solar plant adds 1368.0 GWh/yr against 1279.3 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.61 |
| Day pass (3 trips) | $1.56 (15 % bulk discount) |
| Monthly unlimited pass | $18.40 (~8 % of median monthly income) |
| Annual pass | $202.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (1,152,000 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 240,552 | 432,993 | 350,327 |
| Daily active riders / catchment | 25% | 45% | 36% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 481,104 | 865,986 | 700,655 |
| Daily paid trips / city population | 16% | 28% | 23% |
| Annual paid trips | 175.6 M | 316.1 M | 255.7 M |
| Farebox revenue | $108 M / yr | $194 M / yr | $157 M / yr |
| Station shop leases | $3.8 M / yr | $3.8 M / yr | $3.8 M / yr |
| Advertising boards | $6.0 M / yr | $6.0 M / yr | $6.0 M / yr |
| **Total revenue** | **$117 M / yr** | **$204 M / yr** | **$167 M / yr** |
| Revenue / OPEX recovery | 71% | 122% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $166 M / yr | $117 M / yr | **$117 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$37 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $166 M / yr | $80 M / yr | **$117 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $37 M / yr | $0 / yr |

_Commercial-revenue assumptions: 19,536 m² of station shop/kiosk leases at $18/m²/month and 3,652 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`coimbatore.toml`](coimbatore.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`coimbatore-network-map.png`](coimbatore-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`coimbatore.corridor.geojson`](coimbatore.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`coimbatore.stations.json`](coimbatore.stations.json) | Machine-readable station list |
| [`coimbatore.design-quality.yaml`](coimbatore.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug coimbatore

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug coimbatore \
    --sidecar .cache/osr-pipeline/rasters/coimbatore.grid.json \
    --out-dir designs/.../Coimbatore

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../coimbatore.toml \
    --out designs/.../README.md
```

`scripts/regenerate-coimbatore.sh` chains steps 3 + drift tests into a single command.
