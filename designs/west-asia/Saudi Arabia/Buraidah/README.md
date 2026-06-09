# Buraidah — Urban Rail Network

**Country:** SA · **Population:** 700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Buraidah rail network on OpenStreetMap](buraidah-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`buraidah.corridor.geojson`](buraidah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 54 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 35.2% |
| Route length (double track) | 79.6 km |
| Revenue fleet | 114 × 3-car trainsets |
| Revenue fleet passenger capacity | 41,040 AW2 pax (54,720 AW3 crush) |
| Spare + cold-reserve | 13 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 29.7 km | 20 | 47 | E Outer ↔ NW Outer |
| line-2 | 25.0 km | 17 | 40 | NW Outer ↔ SE Outer |
| line-3 | 25.0 km | 17 | 40 | SW Outer ↔ E Mid |
| **Total** | **79.6 km** | **54 unique** | **127** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 41,040 AW2 pax (54,720 AW3 crush) |
| Total fleet capacity | 45,720 AW2 pax (60,960 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 114 × 360 = **41,040 AW2 passengers** (54,720 AW3 crush)
- **Total fleet passenger capacity:** 127 × 360 = **45,720 AW2 passengers** (60,960 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **123,200 – 221,760 paid trips/day** (61,600 – 110,880 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **700,000**
- Anchor-weighted coverage: 35.2%
- Catchment population: **≈ 246,400** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 32 | 400 kW | 2500 kWh |
| Standard | 13 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **54** | **25,700 kW** | **170,000 kWh** |

Aggregate station-rail charging power: **30,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **90.3 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 318 kWh | 26.5 km average line length |
| Onboard battery coverage | 1.1× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.3 kWh/stop | 556 kW average charger across stops |
| Stops to refill one trainset pack | 39 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 128 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 521 MWh/day | 40,210 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 393 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 90.3 MW / 452 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 170 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (78.2 km @ $3.0 M/km) | $235 M |
| Elevated (1.3 km @ $12.0 M/km) | $16 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$255 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 13 | $2.50 M | $32 M |
| `major` | 32 | $4.50 M | $144 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$240 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 127 | $4.20 M | $533 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 381 | $100 k | $38 M |
| High sensitivity check | 381 | $200 k | $76 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 90,304 kW @ $700/kW | $63 M |
| Grid interconnection / PPA tie-in | 90,304 kW @ $100/kW | $9.0 M |
| Annual generation proxy | 90.3 MW × 5.0 peak-sun-h/day × 365 d/yr | 164.8 GWh/yr |
| **Dedicated solar plant subtotal** | | **$72 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 79.6 km × $0.050 M/km | $4.0 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $24 M |
| EPC integration + project management (7%) | on subtotal | $78 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $255 M |
| Stations | $240 M |
| Depots | $22 M |
| Rolling stock | $533 M |
| Railway production plant | $38 M |
| Dedicated solar power plant | $72 M |
| Residual train-control wayside + charging microgrids | $28 M |
| EPC overhead (7%) | $78 M |
| **CAPEX total** | **$1.27 bn** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $1,810 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh buraidah`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$38 M / yr** | $54 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$25 M / yr** | $36 |
| Lifecycle envelope (yr 1–40, low scenario) | **$190 M cumulative** | $271 |
| Lifecycle envelope (yr 1–40, high scenario) | **$190 M cumulative** | $271 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$1.08 bn cumulative** | $1,538 |

_Population basis: 700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $25 M / yr → $25 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $507 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $633 M | 2.0% | 40 y, 5 y grace | $25 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 4.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $127 M | — | — | — |
| **Total** | **100%** | **$1.27 bn** | | | **$25 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $13 M / yr + fallback bonds $0 k / yr = **$13 M / yr** total. The $507 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($25 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $21 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $10 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $199 k |
| Traction energy (190.2 GWh / yr) | 40,210 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 46.9 GWh/yr + dedicated solar plant 90.3 MW / 164.8 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $1.1 M |
| Labour (549 FTE) | driverless roster: OCC/remote 81, station/platform 207, passenger service 39, fleet maintenance 91, infrastructure/energy 95, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $16 M |
| **OPEX subtotal** | | **$49 M / yr** |

_Annual service work: 40,210 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 15.9 M train-km / yr (47.6 M car-km / yr). On-site PV covers 46.9 GWh/yr and the dedicated solar plant adds 164.8 GWh/yr against 190.2 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $4.53 |
| Day pass (3 trips) | $11.56 (15 % bulk discount) |
| Monthly unlimited pass | $136.00 (~8 % of median monthly income) |
| Annual pass | $1496.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (345,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 61,600 | 110,880 | 5,421 |
| Daily active riders / catchment | 25% | 45% | 2% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 123,200 | 221,760 | 10,843 |
| Daily paid trips / city population | 18% | 32% | 2% |
| Annual paid trips | 45.0 M | 80.9 M | 4.0 M |
| Farebox revenue | $204 M / yr | $367 M / yr | $18 M / yr |
| Station shop leases | $9.1 M / yr | $9.1 M / yr | $9.1 M / yr |
| Advertising boards | $22 M / yr | $22 M / yr | $22 M / yr |
| **Total revenue** | **$235 M / yr** | **$398 M / yr** | **$49 M / yr** |
| Revenue / OPEX recovery | 482% | 818% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Gross repayable-debt service + residual OPEX subsidy | $25 M / yr | $25 M / yr | **$25 M / yr** |
| Operating surplus applied to debt support | -$25 M / yr | -$25 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$25 M / yr** |
| Operating surplus after OPEX (before debt support) | $186 M / yr | $349 M / yr | $0 / yr |

_Commercial-revenue assumptions: 9,568 m² of station shop/kiosk leases at $90/m²/month and 1,780 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`buraidah.toml`](buraidah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`buraidah-network-map.png`](buraidah-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`buraidah.corridor.geojson`](buraidah.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`buraidah.stations.json`](buraidah.stations.json) | Machine-readable station list |
| [`buraidah.design-quality.yaml`](buraidah.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug buraidah

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug buraidah \
    --sidecar .cache/osr-pipeline/rasters/buraidah.grid.json \
    --out-dir designs/.../Buraidah

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../buraidah.toml \
    --out designs/.../README.md
```

`scripts/regenerate-buraidah.sh` chains steps 3 + drift tests into a single command.
