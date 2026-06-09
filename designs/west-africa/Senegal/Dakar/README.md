# Dakar — Urban Rail Network

**Country:** SN · **Population:** 4,030,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Dakar rail network on OpenStreetMap](dakar-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`dakar.corridor.geojson`](dakar.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 106 |
| Interchange stations | 12 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 52.1% |
| Route length (double track) | 204.0 km |
| Revenue fleet | 245 × 6-car trainsets |
| Revenue fleet passenger capacity | 176,400 AW2 pax (235,200 AW3 crush) |
| Spare + cold-reserve | 27 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 42.2 km | 22 | 57 | E Outer ↔ W Outer |
| line-2 | 33.2 km | 18 | 45 | NE Outer ↔ W Outer |
| line-3 | 29.0 km | 16 | 40 | E Outer ↔ W Mid |
| line-4 | 23.4 km | 13 | 32 | NW Inner ↔ E Outer |
| line-5 | 76.1 km | 38 | 98 | W Outer ↔ W Outer |
| **Total** | **204.0 km** | **106 unique** | **272** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 176,400 AW2 pax (235,200 AW3 crush) |
| Total fleet capacity | 195,840 AW2 pax (261,120 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 245 × 720 = **176,400 AW2 passengers** (235,200 AW3 crush)
- **Total fleet passenger capacity:** 272 × 720 = **195,840 AW2 passengers** (261,120 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 14,400 = **144,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,440,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,152,000 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **1,049,814 – 1,152,000 paid trips/day** (524,907 – 576,000 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **4,030,000**
- Anchor-weighted coverage: 52.1%
- Catchment population: **≈ 2,099,630** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 12 | 500 kW | 3000 kWh |
| Major | 57 | 400 kW | 2500 kWh |
| Standard | 27 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **104** | **45,400 kW** | **293,500 kWh** |

Aggregate station-rail charging power: **56,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **561.9 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 979 kWh | 40.8 km average line length |
| Onboard battery coverage | 0.7× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 535 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 227 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 2,670 MWh/day | 103,008 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 2,443 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 561.9 MW / 2,809 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 294 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (192.4 km @ $3.0 M/km) | $577 M |
| Elevated (10.9 km @ $12.0 M/km) | $131 M |
| Elevated-interchange premium (9 sites @ $4.50 M) | $40 M |
| **Civil subtotal** | **$748 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $600 k | $1.8 M |
| `standard` | 27 | $2.50 M | $68 M |
| `major` | 57 | $4.50 M | $256 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 12 | $12.0 M | $144 M |
| **Stations subtotal** | | | **$506 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 272 | $8.40 M | $2.28 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1632 | $100 k | $163 M |
| High sensitivity check | 1632 | $200 k | $326 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 561,884 kW @ $700/kW | $393 M |
| Grid interconnection / PPA tie-in | 561,884 kW @ $100/kW | $56 M |
| Annual generation proxy | 561.9 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,025.4 GWh/yr |
| **Dedicated solar plant subtotal** | | **$450 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 204.0 km × $0.050 M/km | $10 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $47 M |
| EPC integration + project management (7%) | on subtotal | $265 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $748 M |
| Stations | $506 M |
| Depots | $26 M |
| Rolling stock | $2.28 bn |
| Railway production plant | $163 M |
| Dedicated solar power plant | $450 M |
| Residual train-control wayside + charging microgrids | $58 M |
| EPC overhead (7%) | $265 M |
| **CAPEX total** | **$4.50 bn** |
| Per-route-km | $22 M / km |
| Per-capita (city pop) | $1,117 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh dakar`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$109 M / yr** | $27 |
| Steady-state, low-ridership (year 8+) | **$35 M / yr** | $9 |
| Steady-state, high-ridership (year 8+) | **$18 M / yr** | $4 |
| Steady-state, operating-neutral revenue case | **$94 M / yr** | $23 |
| Lifecycle envelope (yr 1–40, low scenario) | **$1.93 bn cumulative** | $480 |
| Lifecycle envelope (yr 1–40, high scenario) | **$1.36 bn cumulative** | $337 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$3.86 bn cumulative** | $958 |

_Population basis: 4,030,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $58 M / yr → $76 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.80 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $2.25 bn | 2.0% | 40 y, 7 y grace | $94 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 8.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $450 M | — | — | — |
| **Total** | **100%** | **$4.50 bn** | | | **$94 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $45 M / yr + fallback bonds $0 k / yr = **$45 M / yr** total. The $1.80 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($64 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $91 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $26 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $508 k |
| Traction energy (974.5 GWh / yr) | 103,008 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 82.9 GWh/yr + dedicated solar plant 561.9 MW / 1025.4 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $6.7 M |
| Labour (1,183 FTE) | driverless roster: OCC/remote 154, station/platform 421, passenger service 143, fleet maintenance 217, infrastructure/energy 202, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $3.5 M |
| **OPEX subtotal** | | **$128 M / yr** |

_Annual service work: 103,008 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 40.6 M train-km / yr (243.6 M car-km / yr). On-site PV covers 82.9 GWh/yr and the dedicated solar plant adds 1025.4 GWh/yr against 974.5 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$175 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.47 |
| Day pass (3 trips) | $1.19 (15 % bulk discount) |
| Monthly unlimited pass | $14.00 (~8 % of median monthly income) |
| Annual pass | $154.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (1,152,000 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 524,907 | 576,000 | 353,408 |
| Daily active riders / catchment | 25% | 27% | 17% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 1,049,814 | 1,152,000 | 706,816 |
| Daily paid trips / city population | 26% | 29% | 18% |
| Annual paid trips | 383.2 M | 420.5 M | 258.0 M |
| Farebox revenue | $179 M / yr | $196 M / yr | $120 M / yr |
| Station shop leases | $2.9 M / yr | $2.9 M / yr | $2.9 M / yr |
| Advertising boards | $4.5 M / yr | $4.5 M / yr | $4.5 M / yr |
| **Total revenue** | **$186 M / yr** | **$204 M / yr** | **$128 M / yr** |
| Revenue / OPEX recovery | 146% | 159% | 100% |
| Country farebox-only policy target (diagnostic) | 40% | 40% | 40% |
| Gross repayable-debt service + residual OPEX subsidy | $94 M / yr | $94 M / yr | **$94 M / yr** |
| Operating surplus applied to debt support | -$58 M / yr | -$76 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $35 M / yr | $18 M / yr | **$94 M / yr** |
| Operating surplus after OPEX (before debt support) | $58 M / yr | $76 M / yr | $0 / yr |

_Commercial-revenue assumptions: 19,440 m² of station shop/kiosk leases at $14/m²/month and 3,572 advertising boards at $122/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`dakar.toml`](dakar.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`dakar-network-map.png`](dakar-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`dakar.corridor.geojson`](dakar.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`dakar.stations.json`](dakar.stations.json) | Machine-readable station list |
| [`dakar.design-quality.yaml`](dakar.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug dakar

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug dakar \
    --sidecar .cache/osr-pipeline/rasters/dakar.grid.json \
    --out-dir designs/.../Dakar

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../dakar.toml \
    --out designs/.../README.md
```

`scripts/regenerate-dakar.sh` chains steps 3 + drift tests into a single command.
