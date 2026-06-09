# Lucknow — Urban Rail Network

**Country:** IN · **Population:** 3,500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Lucknow rail network on OpenStreetMap](lucknow-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`lucknow.corridor.geojson`](lucknow.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 163 |
| Interchange stations | 18 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 31.3% |
| Route length (double track) | 375.5 km |
| Revenue fleet | 443 × 6-car trainsets |
| Revenue fleet passenger capacity | 318,960 AW2 pax (425,280 AW3 crush) |
| Spare + cold-reserve | 48 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 55.9 km | 25 | 73 | W Mid ↔ E Outer |
| line-2 | 44.5 km | 23 | 59 | S Mid ↔ N Mid |
| line-3 | 52.0 km | 21 | 69 | NE Outer ↔ S Mid |
| line-4 | 51.4 km | 23 | 68 | SW Outer ↔ NE Mid |
| line-5 | 53.3 km | 24 | 70 | SE Mid ↔ W Outer |
| line-6 | 118.5 km | 48 | 152 | W Mid ↔ W Mid |
| **Total** | **375.5 km** | **163 unique** | **491** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 318,960 AW2 pax (425,280 AW3 crush) |
| Total fleet capacity | 353,520 AW2 pax (471,360 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 443 × 720 = **318,960 AW2 passengers** (425,280 AW3 crush)
- **Total fleet passenger capacity:** 491 × 720 = **353,520 AW2 passengers** (471,360 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 14,400 = **172,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,728,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,382,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **547,750 – 985,950 paid trips/day** (273,875 – 492,975 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **3,500,000**
- Anchor-weighted coverage: 31.3%
- Catchment population: **≈ 1,095,500** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 18 | 500 kW | 3000 kWh |
| Major | 46 | 400 kW | 2500 kWh |
| Standard | 88 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **162** | **63,300 kW** | **412,000 kWh** |

Aggregate station-rail charging power: **86,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **1,057.7 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 1,502 kWh | 62.6 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 531 kW average charger across stops |
| Stops to refill one trainset pack | 81 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 316 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 4,915 MWh/day | 189,624 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 4,599 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 1,057.7 MW / 5,288 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 412 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (352.1 km @ $3.0 M/km) | $1.06 bn |
| Elevated (22.1 km @ $12.0 M/km) | $265 M |
| Elevated-interchange premium (10 sites @ $4.50 M) | $45 M |
| **Civil subtotal** | **$1.37 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | $600 k | $1.2 M |
| `standard` | 88 | $2.50 M | $220 M |
| `major` | 46 | $4.50 M | $207 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 18 | $12.0 M | $216 M |
| **Stations subtotal** | | | **$690 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 491 | $8.40 M | $4.12 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 2946 | $100 k | $295 M |
| High sensitivity check | 2946 | $200 k | $589 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 1,057,669 kW @ $700/kW | $740 M |
| Grid interconnection / PPA tie-in | 1,057,669 kW @ $100/kW | $106 M |
| Annual generation proxy | 1,057.7 MW × 5.0 peak-sun-h/day × 365 d/yr | 1,930.2 GWh/yr |
| **Dedicated solar plant subtotal** | | **$846 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 375.5 km × $0.050 M/km | $19 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $64 M |
| EPC integration + project management (7%) | on subtotal | $461 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.37 bn |
| Stations | $690 M |
| Depots | $30 M |
| Rolling stock | $4.12 bn |
| Railway production plant | $295 M |
| Dedicated solar power plant | $846 M |
| Residual train-control wayside + charging microgrids | $82 M |
| EPC overhead (7%) | $461 M |
| **CAPEX total** | **$7.89 bn** |
| Per-route-km | $21 M / km |
| Per-capita (city pop) | $2,256 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh lucknow`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$237 M / yr** | $68 |
| Steady-state, low-ridership (year 6+) | **$250 M / yr** | $71 |
| Steady-state, high-ridership (year 6+) | **$152 M / yr** | $43 |
| Steady-state, operating-neutral revenue case | **$158 M / yr** | $45 |
| Lifecycle envelope (yr 1–40, low scenario) | **$9.94 bn cumulative** | $2,839 |
| Lifecycle envelope (yr 1–40, high scenario) | **$6.50 bn cumulative** | $1,858 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$6.71 bn cumulative** | $1,917 |

_Population basis: 3,500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $92 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $6.0 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $3.16 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $3.95 bn | 2.0% | 40 y, 5 y grace | $158 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 7.2% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $789 M | — | — | — |
| **Total** | **100%** | **$7.89 bn** | | | **$158 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $79 M / yr + fallback bonds $0 k / yr = **$79 M / yr** total. The $3.16 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($158 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $165 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $42 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $935 k |
| Traction energy (1794.0 GWh / yr) | 189,624 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 6 cars × 4.0 kWh/car-km; on-site PV 115.5 GWh/yr + dedicated solar plant 1057.7 MW / 1930.2 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $13 M |
| Labour (1,739 FTE) | driverless roster: OCC/remote 260, station/platform 555, passenger service 131, fleet maintenance 397, infrastructure/energy 342, admin/training 54; no train drivers × country median × 12 × engineer-premium 1.4 | $6.7 M |
| **OPEX subtotal** | | **$227 M / yr** |

_Annual service work: 189,624 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 74.7 M train-km / yr (448.5 M car-km / yr). On-site PV covers 115.5 GWh/yr and the dedicated solar plant adds 1930.2 GWh/yr against 1794.0 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.61 |
| Day pass (3 trips) | $1.56 (15 % bulk discount) |
| Monthly unlimited pass | $18.40 (~8 % of median monthly income) |
| Annual pass | $202.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (1,382,400 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 273,875 | 492,975 | 479,633 |
| Daily active riders / catchment | 25% | 45% | 44% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 547,750 | 985,950 | 959,266 |
| Daily paid trips / city population | 16% | 28% | 27% |
| Annual paid trips | 199.9 M | 359.9 M | 350.1 M |
| Farebox revenue | $123 M / yr | $221 M / yr | $215 M / yr |
| Station shop leases | $4.7 M / yr | $4.7 M / yr | $4.7 M / yr |
| Advertising boards | $7.6 M / yr | $7.6 M / yr | $7.6 M / yr |
| **Total revenue** | **$135 M / yr** | **$233 M / yr** | **$227 M / yr** |
| Revenue / OPEX recovery | 59% | 103% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Gross repayable-debt service + residual OPEX subsidy | $250 M / yr | $158 M / yr | **$158 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$6.0 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $250 M / yr | $152 M / yr | **$158 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $6.0 M / yr | $0 / yr |

_Commercial-revenue assumptions: 24,312 m² of station shop/kiosk leases at $18/m²/month and 4,612 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`lucknow.toml`](lucknow.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`lucknow-network-map.png`](lucknow-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`lucknow.corridor.geojson`](lucknow.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`lucknow.stations.json`](lucknow.stations.json) | Machine-readable station list |
| [`lucknow.design-quality.yaml`](lucknow.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug lucknow

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug lucknow \
    --sidecar .cache/osr-pipeline/rasters/lucknow.grid.json \
    --out-dir designs/.../Lucknow

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../lucknow.toml \
    --out designs/.../README.md
```

`scripts/regenerate-lucknow.sh` chains steps 3 + drift tests into a single command.
