# Tunis — Urban Rail Network

**Country:** TN · **Population:** 2,900,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Tunis rail network on OpenStreetMap](tunis-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`tunis.corridor.geojson`](tunis.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 117 |
| Interchange stations | 20 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 47.8% |
| Route length (double track) | 240.3 km |
| Revenue fleet | 287 × 4-car trainsets |
| Revenue fleet passenger capacity | 137,760 AW2 pax (183,680 AW3 crush) |
| Spare + cold-reserve | 31 × 4-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 45.4 km | 22 | 60 | SE Outer ↔ W Mid |
| line-2 | 38.2 km | 20 | 51 | NE Outer ↔ W Outer |
| line-3 | 32.8 km | 18 | 45 | S Mid ↔ N Mid |
| line-4 | 40.6 km | 19 | 54 | NW Outer ↔ SE Outer |
| line-5 | 83.3 km | 39 | 108 | W Mid ↔ W Mid |
| **Total** | **240.3 km** | **117 unique** | **318** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 137,760 AW2 pax (183,680 AW3 crush) |
| Total fleet capacity | 152,640 AW2 pax (203,520 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Revenue fleet simultaneous capacity:** 287 × 480 = **137,760 AW2 passengers** (183,680 AW3 crush)
- **Total fleet passenger capacity:** 318 × 480 = **152,640 AW2 passengers** (203,520 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 480 × 20 = **9,600 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 9,600 = **96,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **960,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **768,000 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment (capped by practical service capacity)): ≈ **693,100 – 768,000 paid trips/day** (346,550 – 384,000 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **2,900,000**
- Anchor-weighted coverage: 47.8%
- Catchment population: **≈ 1,386,200** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 20 | 500 kW | 3000 kWh |
| Major | 43 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **117** | **49,500 kW** | **320,500 kWh** |

Aggregate station-rail charging power: **62,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **425.4 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 769 kWh | 48.1 km average line length |
| Onboard battery coverage | 0.6× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 8.9 kWh/stop | 536 kW average charger across stops |
| Stops to refill one trainset pack | 54 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 248 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 2,097 MWh/day | 121,352 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 1,849 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 425.4 MW / 2,127 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 320 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (226.3 km @ $3.0 M/km) | $679 M |
| Elevated (13.1 km @ $12.0 M/km) | $158 M |
| Elevated-interchange premium (11 sites @ $4.50 M) | $50 M |
| **Civil subtotal** | **$886 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 46 | $2.50 M | $115 M |
| `major` | 43 | $4.50 M | $194 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 20 | $12.0 M | $240 M |
| **Stations subtotal** | | | **$586 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 318 | $5.60 M | $1.78 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 1272 | $100 k | $127 M |
| High sensitivity check | 1272 | $200 k | $254 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 425,375 kW @ $700/kW | $298 M |
| Grid interconnection / PPA tie-in | 425,375 kW @ $100/kW | $43 M |
| Annual generation proxy | 425.4 MW × 5.0 peak-sun-h/day × 365 d/yr | 776.3 GWh/yr |
| **Dedicated solar plant subtotal** | | **$340 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 240.3 km × $0.050 M/km | $12 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $52 M |
| EPC integration + project management (7%) | on subtotal | $243 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $886 M |
| Stations | $586 M |
| Depots | $26 M |
| Rolling stock | $1.78 bn |
| Railway production plant | $127 M |
| Dedicated solar power plant | $340 M |
| Residual train-control wayside + charging microgrids | $64 M |
| EPC overhead (7%) | $243 M |
| **CAPEX total** | **$4.05 bn** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $1,398 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh tunis`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$122 M / yr** | $42 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$81 M / yr** | $28 |
| Lifecycle envelope (yr 1–40, low scenario) | **$608 M cumulative** | $210 |
| Lifecycle envelope (yr 1–40, high scenario) | **$608 M cumulative** | $210 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$3.45 bn cumulative** | $1,188 |

_Population basis: 2,900,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $81 M / yr → $81 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $1.62 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $2.03 bn | 2.0% | 40 y, 5 y grace | $81 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 9.0% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $405 M | — | — | — |
| **Total** | **100%** | **$4.05 bn** | | | **$81 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $41 M / yr + fallback bonds $0 k / yr = **$41 M / yr** total. The $1.62 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($81 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $71 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $30 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $599 k |
| Traction energy (765.4 GWh / yr) | 121,352 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 4 cars × 4.0 kWh/car-km; on-site PV 90.3 GWh/yr + dedicated solar plant 425.4 MW / 776.3 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $5.1 M |
| Labour (1,275 FTE) | driverless roster: OCC/remote 175, station/platform 465, passenger service 104, fleet maintenance 255, infrastructure/energy 230, admin/training 46; no train drivers × country median × 12 × engineer-premium 1.4 | $7.5 M |
| **OPEX subtotal** | | **$114 M / yr** |

_Annual service work: 121,352 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 47.8 M train-km / yr (191.3 M car-km / yr). On-site PV covers 90.3 GWh/yr and the dedicated solar plant adds 776.3 GWh/yr against 765.4 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$350 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.93 |
| Day pass (3 trips) | $2.38 (15 % bulk discount) |
| Monthly unlimited pass | $28.00 (~8 % of median monthly income) |
| Annual pass | $308.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (768,000 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 346,550 | 384,000 | 144,529 |
| Daily active riders / catchment | 25% | 28% | 10% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 693,100 | 768,000 | 289,058 |
| Daily paid trips / city population | 24% | 26% | 10% |
| Annual paid trips | 253.0 M | 280.3 M | 105.5 M |
| Farebox revenue | $236 M / yr | $262 M / yr | $98 M / yr |
| Station shop leases | $6.2 M / yr | $6.2 M / yr | $6.2 M / yr |
| Advertising boards | $9.7 M / yr | $9.7 M / yr | $9.7 M / yr |
| **Total revenue** | **$252 M / yr** | **$278 M / yr** | **$114 M / yr** |
| Revenue / OPEX recovery | 220% | 243% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Gross repayable-debt service + residual OPEX subsidy | $81 M / yr | $81 M / yr | **$81 M / yr** |
| Operating surplus applied to debt support | -$81 M / yr | -$81 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$81 M / yr** |
| Operating surplus after OPEX (before debt support) | $138 M / yr | $163 M / yr | $0 / yr |

_Commercial-revenue assumptions: 21,064 m² of station shop/kiosk leases at $28/m²/month and 3,876 advertising boards at $245/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`tunis.toml`](tunis.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`tunis-network-map.png`](tunis-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`tunis.corridor.geojson`](tunis.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`tunis.stations.json`](tunis.stations.json) | Machine-readable station list |
| [`tunis.design-quality.yaml`](tunis.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug tunis

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug tunis \
    --sidecar .cache/osr-pipeline/rasters/tunis.grid.json \
    --out-dir designs/.../Tunis

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../tunis.toml \
    --out designs/.../README.md
```

`scripts/regenerate-tunis.sh` chains steps 3 + drift tests into a single command.
