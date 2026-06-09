# Khulna — Urban Rail Network

**Country:** BD · **Population:** 1,500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Khulna rail network on OpenStreetMap](khulna-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`khulna.corridor.geojson`](khulna.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 81 |
| Interchange stations | 19 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.9% |
| Route length (double track) | 182.2 km |
| Revenue fleet | 224 × 4-car trainsets |
| Revenue fleet passenger capacity | 107,520 AW2 pax (143,360 AW3 crush) |
| Spare + cold-reserve | 25 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 42.4 km | 22 | 57 | SE Outer ↔ NW Outer |
| line-2 | 22.7 km | 10 | 31 | E Outer ↔ SW Mid |
| line-3 | 18.5 km | 9 | 27 | N Inner ↔ S Mid |
| line-4 | 37.6 km | 13 | 51 | NE Outer ↔ W Outer |
| line-5 | 14.2 km | 6 | 21 | SE Inner ↔ W Mid |
| line-6 | 46.9 km | 22 | 62 | NW Mid ↔ NW Mid |
| **Total** | **182.2 km** | **81 unique** | **249** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 107,520 AW2 pax (143,360 AW3 crush) |
| Total fleet capacity | 119,520 AW2 pax (159,360 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 224 × 480 = **107,520 AW2 passengers** (143,360 AW3 crush)
- **Total fleet passenger capacity:** 249 × 480 = **119,520 AW2 passengers** (159,360 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 9,600 = **115,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,152,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **921,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **426,748 – 768,148 paid trips/day** (213,374 – 384,074 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **1,500,000**
- Anchor-weighted coverage: 56.9%
- Catchment population: **≈ 853,499** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 19 | 500 kW | 3000 kWh |
| Major | 19 | 400 kW | 2500 kWh |
| Standard | 22 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **70** | **33,200 kW** | **215,500 kWh** |

Aggregate station-rail charging power: **43,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **327.6 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 486 kWh | 30.4 km average line length |
| Onboard battery coverage | 1.0× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 531 kW average charger across stops |
| Stops to refill one trainset pack | 54 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 166 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 1,590 MWh/day | 92,033 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,424 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 327.6 MW / 1,638 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 216 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (152.4 km @ $3.0 M/km) | $457 M |
| Elevated (26.9 km @ $12.0 M/km) | $323 M |
| Elevated-interchange premium (8 sites @ $4.50 M) | $36 M |
| **Civil subtotal** | **$816 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 12 | $600 k | $7.2 M |
| `standard` | 22 | $2.50 M | $55 M |
| `major` | 19 | $4.50 M | $86 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
| `interchange-elevated` | 17 | $12.0 M | $204 M |
| **Stations subtotal** | | | **$413 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 9 | $2.0 M | $18 M |
| **Depots subtotal** | | | **$30 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 249 | $5.60 M | $1.39 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 996 | $100 k | $100 M |
| High sensitivity check | 996 | $200 k | $199 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 327,595 kW @ $700/kW | $229 M |
| Grid interconnection / PPA tie-in | 327,595 kW @ $100/kW | $33 M |
| Annual generation proxy | 327.6 MW × 5.0 peak-sun-h/day × 365 d/yr | 597.9 GWh/yr |
| **Dedicated solar plant subtotal** | | **$262 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 182.2 km × $0.050 M/km | $9.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $37 M |
| EPC integration + project management (7%) | on subtotal | $196 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $816 M |
| Stations | $413 M |
| Depots | $30 M |
| Rolling stock | $1.39 bn |
| Railway production plant | $100 M |
| Dedicated solar power plant | $262 M |
| Residual train-control wayside + charging microgrids | $46 M |
| EPC overhead (7%) | $196 M |
| **CAPEX total** | **$3.26 bn** |
| Per-route-km | $18 M / km |
| Per-capita (city pop) | $2,171 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh khulna`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$79 M / yr** | $53 |
| Steady-state, low-ridership (year 8+) | **$69 M / yr** | $46 |
| Steady-state, high-ridership (year 8+) | **$4.7 M / yr** | $3 |
| Steady-state, operating-neutral revenue case | **$68 M / yr** | $45 |
| Lifecycle envelope (yr 1–40, low scenario) | **$2.85 bn cumulative** | $1,898 |
| Lifecycle envelope (yr 1–40, high scenario) | **$708 M cumulative** | $472 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$2.79 bn cumulative** | $1,863 |

_Population basis: 1,500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $1.6 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $63 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.30 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $1.63 bn | 2.0% | 40 y, 7 y grace | $68 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 8.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $326 M | — | — | — |
| **Total** | **100%** | **$3.26 bn** | | | **$68 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $33 M / yr + fallback bonds $0 k / yr = **$33 M / yr** total. The $1.30 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($47 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $56 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $25 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $448 k |
| Traction energy (580.5 GWh / yr) | 92,033 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 60.6 GWh/yr + dedicated solar plant 327.6 MW / 597.9 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $3.9 M |
| Labour (1,024 FTE) | driverless roster: OCC/remote 146, station/platform 331, passenger service 110, fleet maintenance 196, infrastructure/energy 187, admin/training 54; no train drivers × country median × 12 × engineer-premium 1.4 | $3.4 M |
| **OPEX subtotal** | | **$89 M / yr** |

_Annual service work: 92,033 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 36.3 M train-km / yr (145.1 M car-km / yr). On-site PV covers 60.6 GWh/yr and the dedicated solar plant adds 597.9 GWh/yr against 580.5 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$195 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.52 |
| Day pass (3 trips) | $1.33 (15 % bulk discount) |
| Monthly unlimited pass | $15.60 (~8 % of median monthly income) |
| Annual pass | $171.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (921,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 213,374 | 384,074 | 217,547 |
| Daily active riders / catchment | 25% | 45% | 25% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 426,748 | 768,148 | 435,095 |
| Daily paid trips / city population | 28% | 51% | 29% |
| Annual paid trips | 155.8 M | 280.4 M | 158.8 M |
| Farebox revenue | $81 M / yr | $146 M / yr | $83 M / yr |
| Station shop leases | $2.4 M / yr | $2.4 M / yr | $2.4 M / yr |
| Advertising boards | $3.7 M / yr | $3.7 M / yr | $3.7 M / yr |
| **Total revenue** | **$87 M / yr** | **$152 M / yr** | **$89 M / yr** |
| Revenue / OPEX recovery | 98% | 171% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Gross repayable-debt service + residual OPEX subsidy | $69 M / yr | $68 M / yr | **$68 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$63 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $69 M / yr | $4.7 M / yr | **$68 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $63 M / yr | $0 / yr |

_Commercial-revenue assumptions: 14,528 m² of station shop/kiosk leases at $16/m²/month and 2,672 advertising boards at $136/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`khulna.toml`](khulna.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`khulna-network-map.png`](khulna-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`khulna.corridor.geojson`](khulna.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`khulna.stations.json`](khulna.stations.json) | Machine-readable station list |
| [`khulna.design-quality.yaml`](khulna.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug khulna

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug khulna \
    --sidecar .cache/osr-pipeline/rasters/khulna.grid.json \
    --out-dir designs/.../Khulna

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../khulna.toml \
    --out designs/.../README.md
```

`scripts/regenerate-khulna.sh` chains steps 3 + drift tests into a single command.
