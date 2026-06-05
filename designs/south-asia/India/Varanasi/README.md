# Varanasi — Urban Rail Network

**Country:** IN · **Population:** 1,500,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Varanasi rail network on OpenStreetMap](varanasi-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`varanasi.corridor.geojson`](varanasi.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 99 |
| Interchange stations | 14 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 46.7% |
| Route length (double track) | 202.0 km |
| Revenue fleet | 147 × 4-car trainsets |
| Spare + cold-reserve | 18 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.5 km | 20 | 34 | NW Outer ↔ SE Mid |
| line-2 | 35.2 km | 17 | 29 | E Outer ↔ W Outer |
| line-3 | 31.6 km | 17 | 26 | NE Outer ↔ SW Mid |
| line-4 | 26.6 km | 13 | 23 | NW Inner ↔ S Outer |
| line-5 | 67.1 km | 33 | 53 | NW Mid ↔ NW Mid |
| **Total** | **202.0 km** | **99 unique** | **165** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 75 m |
| Max speed | 90 km/h |
| Onboard battery | 480 kWh per trainset |
| Seats | 80 longitudinal seats |
| Nominal capacity (AW2) | 480 pax (seated + standing, `metro-4car` per RFC 0008 §1) |
| Crush capacity (AW3) | 640 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 480 AW2 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 480 × 12 = **5,760 pphpd**
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 5,760 = **57,600 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **576,000 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **374,400 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **126,090 – 210,150 trips/day**

## Catchment

- City population: **1,500,000**
- Anchor-weighted coverage: 46.7%
- Catchment population: **≈ 700,500** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 14 | 500 kW | 3000 kWh |
| Major | 40 | 400 kW | 2500 kWh |
| Standard | 35 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **97** | **42,000 kW** | **273,000 kWh** |

Aggregate station-rail charging power: **53,250 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 480 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 16.0 kWh/km | 4 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 646 kWh | 40.4 km average line length |
| Onboard battery coverage | 0.7× average line run | 480 kWh usable pack |
| Average 60 s dwell charge | 9.0 kWh/stop | 538 kW average charger across stops |
| Stops to refill one trainset pack | 54 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 210 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 273 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (170.1 km @ $3.0 M/km) | $510 M |
| Elevated (31.0 km @ $12.0 M/km) | $373 M |
| Elevated-interchange premium (6 sites @ $4.50 M) | $27 M |
| **Civil subtotal** | **$910 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | $600 k | $1.8 M |
| `standard` | 35 | $2.50 M | $88 M |
| `major` | 40 | $4.50 M | $180 M |
| `terminal` | 7 | $4.50 M | $32 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
| `interchange-elevated` | 12 | $12.0 M | $144 M |
| **Stations subtotal** | | | **$466 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 165 | $5.60 M | $924 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 660 | $100 k | $66 M |
| High sensitivity check | 660 | $200 k | $132 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 202.0 km × $0.050 M/km | $10 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $43 M |
| EPC integration + project management (7%) | on subtotal | $171 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $910 M |
| Stations | $466 M |
| Depots | $26 M |
| Rolling stock | $924 M |
| Railway production plant | $66 M |
| Residual train-control wayside + charging microgrids | $53 M |
| EPC overhead (7%) | $171 M |
| **CAPEX total** | **$2.62 bn** |
| Per-route-km | $13 M / km |
| Per-capita (city pop) | $1,744 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh varanasi`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$188 M / yr** | $126 |
| Steady-state, low-ridership (year 6+) | **$219 M / yr** | $146 |
| Steady-state, high-ridership (year 6+) | **$205 M / yr** | $136 |
| Steady-state, operating-neutral revenue case | **$178 M / yr** | $119 |
| Lifecycle envelope (yr 1–25, low scenario) | **$5.31 bn cumulative** | $3,543 |
| Lifecycle envelope (yr 1–25, high scenario) | **$5.03 bn cumulative** | $3,355 |
| Lifecycle envelope (yr 1–25, operating-neutral after opening) | **$4.51 bn cumulative** | $3,004 |

_Population basis: 1,500,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $40 M / yr → $26 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $1.57 bn | 4.0% | 25 y, 5 y grace | $115 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $654 M | 7.2% | 25 y, 5 y grace | $63 M / yr |
| Government equity (no debt service) | 15% | $392 M | — | — | — |
| **Total** | **100%** | **$2.62 bn** | | | **$178 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral $63 M / yr + bonds $47 M / yr = **$110 M / yr** total — plus the equity tranche amortised across construction ($78 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $37 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $28 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $503 k |
| Traction energy (462.0 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (1,224 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $4.7 M |
| **OPEX subtotal** | | **$70 M / yr** |

_Annual fleet utilisation: 147 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 28.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.38 |
| Operating-neutral single-trip fare (6 % pass) | $0.46 |
| Day pass (3 trips) | $1.17 (15 % bulk discount) |
| Monthly unlimited pass | $13.80 (~6 % of median monthly income) |
| Annual pass | $151.80 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (374,400 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 126,090 | 210,150 | 366,943 |
| Daily paid trips / catchment | 18% | 30% | 52% |
| Daily paid trips / city population | 8% | 14% | 24% |
| Annual paid trips | 46.0 M | 76.7 M | 133.9 M |
| Farebox revenue | $21 M / yr | $35 M / yr | $62 M / yr |
| Station shop leases | $3.4 M / yr | $3.4 M / yr | $3.4 M / yr |
| Advertising boards | $5.3 M / yr | $5.3 M / yr | $5.3 M / yr |
| **Total revenue** | **$30 M / yr** | **$44 M / yr** | **$70 M / yr** |
| Revenue / OPEX recovery | 42% | 63% | 100% |
| Country farebox-only policy target (diagnostic) | 55% | 55% | 55% |
| Remaining steady-state gov commitment | $219 M / yr | $205 M / yr | **$178 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 17,288 m² of station shop/kiosk leases at $18/m²/month and 3,200 advertising boards at $161/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`varanasi.toml`](varanasi.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`varanasi-network-map.png`](varanasi-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`varanasi.corridor.geojson`](varanasi.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`varanasi.stations.json`](varanasi.stations.json) | Machine-readable station list |
| [`varanasi.design-quality.yaml`](varanasi.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug varanasi

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug varanasi \
    --sidecar .cache/osr-pipeline/rasters/varanasi.grid.json \
    --out-dir designs/.../Varanasi

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../varanasi.toml \
    --out designs/.../README.md
```

`scripts/regenerate-varanasi.sh` chains steps 3 + drift tests into a single command.
