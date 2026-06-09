# Cuenca — Urban Rail Network

**Country:** EC · **Population:** 817,100

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Cuenca rail network on OpenStreetMap](cuenca-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`cuenca.corridor.geojson`](cuenca.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 48 |
| Interchange stations | 5 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 57.4% |
| Route length (double track) | 78.5 km |
| Revenue fleet | 113 × 3-car trainsets |
| Revenue fleet passenger capacity | 40,680 AW2 pax (54,240 AW3 crush) |
| Spare + cold-reserve | 12 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 26.5 km | 17 | 42 | E Mid ↔ W Outer |
| line-2 | 27.1 km | 16 | 43 | W Outer ↔ E Outer |
| line-3 | 24.9 km | 15 | 40 | NE Outer ↔ SW Mid |
| **Total** | **78.5 km** | **48 unique** | **125** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 40,680 AW2 pax (54,240 AW3 crush) |
| Total fleet capacity | 45,000 AW2 pax (60,000 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 113 × 360 = **40,680 AW2 passengers** (54,240 AW3 crush)
- **Total fleet passenger capacity:** 125 × 360 = **45,000 AW2 passengers** (60,000 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **234,506 – 345,600 paid trips/day** (117,253 – 172,800 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **817,100**
- Anchor-weighted coverage: 57.4%
- Catchment population: **≈ 469,015** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 5 | 500 kW | 3000 kWh |
| Major | 22 | 400 kW | 2500 kWh |
| Standard | 13 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **46** | **22,700 kW** | **151,000 kWh** |

Aggregate station-rail charging power: **26,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **92.1 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 314 kWh | 26.2 km average line length |
| Onboard battery coverage | 1.1× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.2 kWh/stop | 552 kW average charger across stops |
| Stops to refill one trainset pack | 39 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 114 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 514 MWh/day | 39,657 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 400 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 92.1 MW / 461 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 151 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (72.1 km @ $3.0 M/km) | $216 M |
| Elevated (4.9 km @ $12.0 M/km) | $58 M |
| Elevated-interchange premium (3 sites @ $4.50 M) | $14 M |
| **Civil subtotal** | **$288 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | $600 k | $1.2 M |
| `standard` | 13 | $2.50 M | $32 M |
| `major` | 22 | $4.50 M | $99 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 3 | $8.0 M | $24 M |
| `interchange-elevated` | 2 | $12.0 M | $24 M |
| **Stations subtotal** | | | **$208 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 125 | $4.20 M | $525 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 375 | $100 k | $38 M |
| High sensitivity check | 375 | $200 k | $75 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 92,104 kW @ $700/kW | $64 M |
| Grid interconnection / PPA tie-in | 92,104 kW @ $100/kW | $9.2 M |
| Annual generation proxy | 92.1 MW × 5.0 peak-sun-h/day × 365 d/yr | 168.1 GWh/yr |
| **Dedicated solar plant subtotal** | | **$74 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 78.5 km × $0.050 M/km | $3.8 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $21 M |
| EPC integration + project management (7%) | on subtotal | $77 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $288 M |
| Stations | $208 M |
| Depots | $22 M |
| Rolling stock | $525 M |
| Railway production plant | $38 M |
| Dedicated solar power plant | $74 M |
| Residual train-control wayside + charging microgrids | $25 M |
| EPC overhead (7%) | $77 M |
| **CAPEX total** | **$1.26 bn** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $1,538 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh cuenca`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$38 M / yr** | $46 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$25 M / yr** | $31 |
| Lifecycle envelope (yr 1–40, low scenario) | **$188 M cumulative** | $231 |
| Lifecycle envelope (yr 1–40, high scenario) | **$188 M cumulative** | $231 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.07 bn cumulative** | $1,307 |

_Population basis: 817,100 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $25 M / yr → $25 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $503 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $628 M | 2.0% | 40 y, 5 y grace | $25 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 9.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $126 M | — | — | — |
| **Total** | **100%** | **$1.26 bn** | | | **$25 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $13 M / yr + fallback bonds $0 k / yr = **$13 M / yr** total. The $503 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($25 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $21 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $10 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $192 k |
| Traction energy (187.6 GWh / yr) | 39,657 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 41.4 GWh/yr + dedicated solar plant 92.1 MW / 168.1 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $1.1 M |
| Labour (535 FTE) | driverless roster: OCC/remote 81, station/platform 185, passenger service 51, fleet maintenance 90, infrastructure/energy 92, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $3.7 M |
| **OPEX subtotal** | | **$36 M / yr** |

_Annual service work: 39,657 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 15.6 M train-km / yr (46.9 M car-km / yr). On-site PV covers 41.4 GWh/yr and the dedicated solar plant adds 168.1 GWh/yr against 187.6 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$410 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $1.09 |
| Day pass (3 trips) | $2.79 (15 % bulk discount) |
| Monthly unlimited pass | $32.80 (~8 % of median monthly income) |
| Annual pass | $360.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (345,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 117,253 | 172,800 | 36,359 |
| Daily active riders / catchment | 25% | 37% | 8% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 234,506 | 345,600 | 72,718 |
| Daily paid trips / city population | 29% | 42% | 9% |
| Annual paid trips | 85.6 M | 126.1 M | 26.5 M |
| Farebox revenue | $94 M / yr | $138 M / yr | $29 M / yr |
| Station shop leases | $2.8 M / yr | $2.8 M / yr | $2.8 M / yr |
| Advertising boards | $4.5 M / yr | $4.5 M / yr | $4.5 M / yr |
| **Total revenue** | **$101 M / yr** | **$145 M / yr** | **$36 M / yr** |
| Revenue / OPEX recovery | 278% | 400% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $25 M / yr | $25 M / yr | **$25 M / yr** |
| Operating surplus applied to debt support | -$25 M / yr | -$25 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$25 M / yr** |
| Operating surplus after OPEX (before debt support) | $65 M / yr | $109 M / yr | $0 / yr |

_Commercial-revenue assumptions: 8,208 m² of station shop/kiosk leases at $33/m²/month and 1,532 advertising boards at $287/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`cuenca.toml`](cuenca.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`cuenca-network-map.png`](cuenca-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`cuenca.corridor.geojson`](cuenca.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`cuenca.stations.json`](cuenca.stations.json) | Machine-readable station list |
| [`cuenca.design-quality.yaml`](cuenca.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug cuenca

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug cuenca \
    --sidecar .cache/osr-pipeline/rasters/cuenca.grid.json \
    --out-dir designs/.../Cuenca

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../cuenca.toml \
    --out designs/.../README.md
```

`scripts/regenerate-cuenca.sh` chains steps 3 + drift tests into a single command.
