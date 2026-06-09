# Machakos — Urban Rail Network

**Country:** KE · **Population:** 300,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Machakos rail network on OpenStreetMap](machakos-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`machakos.corridor.geojson`](machakos.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 16 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 75.7% |
| Route length (double track) | 26.5 km |
| Revenue fleet | 57 × 2-car trainsets |
| Revenue fleet passenger capacity | 13,680 AW2 pax (18,240 AW3 crush) |
| Spare + cold-reserve | 7 × 2-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 12.2 km | 6 | 28 | S Mid ↔ N Outer |
| line-2 |  7.7 km | 5 | 19 | W Mid ↔ N Inner |
| line-3 |  6.7 km | 5 | 17 | W Mid ↔ SE Mid |
| **Total** | **26.5 km** | **16 unique** | **64** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 2-car, 39 m |
| Max speed | 70 km/h |
| Onboard battery | 240 kWh per trainset |
| Seats | 40 longitudinal seats |
| Nominal capacity (AW2) | 240 pax (seated + standing, `tram-2car` per RFC 0008 §1) |
| Crush capacity (AW3) | 320 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 13,680 AW2 pax (18,240 AW3 crush) |
| Total fleet capacity | 15,360 AW2 pax (20,480 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 240 AW2 passengers (`tram-2car`)
- **Revenue fleet simultaneous capacity:** 57 × 240 = **13,680 AW2 passengers** (18,240 AW3 crush)
- **Total fleet passenger capacity:** 64 × 240 = **15,360 AW2 passengers** (20,480 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 240 × 20 = **4,800 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 4,800 = **28,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **288,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **230,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **113,550 – 204,390 paid trips/day** (56,775 – 102,195 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **300,000**
- Anchor-weighted coverage: 75.7%
- Catchment population: **≈ 227,100** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 3 | 400 kW | 2500 kWh |
| Standard | 4 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **16** | **11,400 kW** | **79,500 kWh** |

Aggregate station-rail charging power: **11,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 240 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **13.5 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 8.0 kWh/km | 2 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 71 kWh | 8.8 km average line length |
| Onboard battery coverage | 3.4× average line run | 240 kWh usable pack |
| Average 60 s dwell charge | 11.5 kWh/stop | 688 kW average charger across stops |
| Stops to refill one trainset pack | 21 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 57 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 116 MWh/day | 13,401 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 59 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 13.5 MW / 68 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 80 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (25.2 km @ $3.0 M/km) | $76 M |
| Elevated (1.3 km @ $12.0 M/km) | $15 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$95 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 4 | $2.50 M | $10 M |
| `major` | 3 | $4.50 M | $14 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$87 M** |

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
| `tram-2car` (revenue + spare + cold reserve) | 64 | $2.80 M | $179 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 128 | $100 k | $13 M |
| High sensitivity check | 128 | $200 k | $26 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 13,521 kW @ $700/kW | $9.5 M |
| Grid interconnection / PPA tie-in | 13,521 kW @ $100/kW | $1.4 M |
| Annual generation proxy | 13.5 MW × 5.0 peak-sun-h/day × 365 d/yr | 24.7 GWh/yr |
| **Dedicated solar plant subtotal** | | **$11 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 26.5 km × $0.050 M/km | $1.3 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $8.4 M |
| EPC integration + project management (7%) | on subtotal | $28 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $95 M |
| Stations | $87 M |
| Depots | $22 M |
| Rolling stock | $179 M |
| Railway production plant | $13 M |
| Dedicated solar power plant | $11 M |
| Residual train-control wayside + charging microgrids | $9.7 M |
| EPC overhead (7%) | $28 M |
| **CAPEX total** | **$445 M** |
| Per-route-km | $17 M / km |
| Per-capita (city pop) | $1,485 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh machakos`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$11 M / yr** | $36 |
| Steady-state, low-ridership (year 8+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 8+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$9.3 M / yr** | $31 |
| Lifecycle envelope (yr 1–40, low scenario) | **$76 M cumulative** | $252 |
| Lifecycle envelope (yr 1–40, high scenario) | **$76 M cumulative** | $252 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$382 M cumulative** | $1,274 |

_Population basis: 300,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $9.3 M / yr → $9.3 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $178 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $223 M | 2.0% | 40 y, 7 y grace | $9.3 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 11.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $45 M | — | — | — |
| **Total** | **100%** | **$445 M** | | | **$9.3 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $4.5 M / yr + fallback bonds $0 k / yr = **$4.5 M / yr** total. The $178 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($6.4 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $7.2 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $4.1 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $66 k |
| Traction energy (42.3 GWh / yr) | 13,401 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 2 cars × 4.0 kWh/car-km; on-site PV 20.8 GWh/yr + dedicated solar plant 13.5 MW / 24.7 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $162 k |
| Labour (281 FTE) | driverless roster: OCC/remote 53, station/platform 71, passenger service 37, fleet maintenance 37, infrastructure/energy 47, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $1.1 M |
| **OPEX subtotal** | | **$13 M / yr** |

_Annual service work: 13,401 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 5.3 M train-km / yr (10.6 M car-km / yr). On-site PV covers 20.8 GWh/yr and the dedicated solar plant adds 24.7 GWh/yr against 42.3 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.61 |
| Day pass (3 trips) | $1.56 (15 % bulk discount) |
| Monthly unlimited pass | $18.40 (~8 % of median monthly income) |
| Annual pass | $202.40 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (230,400 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 56,775 | 102,195 | 24,551 |
| Daily active riders / catchment | 25% | 45% | 11% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 113,550 | 204,390 | 49,102 |
| Daily paid trips / city population | 38% | 68% | 16% |
| Annual paid trips | 41.4 M | 74.6 M | 17.9 M |
| Farebox revenue | $25 M / yr | $46 M / yr | $11 M / yr |
| Station shop leases | $606 k / yr | $606 k / yr | $606 k / yr |
| Advertising boards | $972 k / yr | $972 k / yr | $972 k / yr |
| **Total revenue** | **$27 M / yr** | **$47 M / yr** | **$13 M / yr** |
| Revenue / OPEX recovery | 215% | 377% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Gross repayable-debt service + residual OPEX subsidy | $9.3 M / yr | $9.3 M / yr | **$9.3 M / yr** |
| Operating surplus applied to debt support | -$9.3 M / yr | -$9.3 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$9.3 M / yr** |
| Operating surplus after OPEX (before debt support) | $14 M / yr | $35 M / yr | $0 / yr |

_Commercial-revenue assumptions: 3,120 m² of station shop/kiosk leases at $18/m²/month and 592 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`machakos.toml`](machakos.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`machakos-network-map.png`](machakos-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`machakos.corridor.geojson`](machakos.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`machakos.stations.json`](machakos.stations.json) | Machine-readable station list |
| [`machakos.design-quality.yaml`](machakos.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug machakos

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug machakos \
    --sidecar .cache/osr-pipeline/rasters/machakos.grid.json \
    --out-dir designs/.../Machakos

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../machakos.toml \
    --out designs/.../README.md
```

`scripts/regenerate-machakos.sh` chains steps 3 + drift tests into a single command.
