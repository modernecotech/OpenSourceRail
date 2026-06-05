# Kandahar — Urban Rail Network

**Country:** AF · **Population:** 700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kandahar rail network on OpenStreetMap](kandahar-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kandahar.corridor.geojson`](kandahar.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 43 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 53.0% |
| Route length (double track) | 64.0 km |
| Revenue fleet | 56 × 3-car trainsets |
| Spare + cold-reserve | 6 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 21.3 km | 14 | 21 | E Mid ↔ W Outer |
| line-2 | 20.5 km | 15 | 20 | W Outer ↔ SE Outer |
| line-3 | 22.2 km | 14 | 21 | NW Mid ↔ E Outer |
| **Total** | **64.0 km** | **43 unique** | **62** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 360 × 12 = **4,320 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 4,320 = **25,920 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **259,200 passenger-trips/day**
- **Practical daily service capacity** (65% load factor): ≈ **168,480 passenger-trips/day**
- **Planning daily ridership scenario** (18-30% of catchment): ≈ **66,780 – 111,300 trips/day**

## Catchment

- City population: **700,000**
- Anchor-weighted coverage: 53.0%
- Catchment population: **≈ 371,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 23 | 400 kW | 2500 kWh |
| Standard | 11 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **43** | **21,500 kW** | **143,500 kWh** |

Aggregate station-rail charging power: **24,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 256 kWh | 21.3 km average line length |
| Onboard battery coverage | 1.4× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.5 kWh/stop | 570 kW average charger across stops |
| Stops to refill one trainset pack | 38 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 108 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 144 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (62.9 km @ $3.0 M/km) | $189 M |
| Elevated (1.1 km @ $12.0 M/km) | $13 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$206 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Standard and larger stations include a covered pedestrian overbridge/concourse for safe access to central or median platforms, with step-free vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 11 | $2.50 M | $28 M |
| `major` | 23 | $4.50 M | $104 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$194 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 62 | $4.20 M | $260 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 186 | $100 k | $19 M |
| High sensitivity check | 186 | $200 k | $37 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 64.0 km × $0.050 M/km | $3.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $19 M |
| EPC integration + project management (7%) | on subtotal | $51 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $206 M |
| Stations | $194 M |
| Depots | $22 M |
| Rolling stock | $260 M |
| Railway production plant | $19 M |
| Residual train-control wayside + charging microgrids | $22 M |
| EPC overhead (7%) | $51 M |
| **CAPEX total** | **$775 M** |
| Per-route-km | $12 M / km |
| Per-capita (city pop) | $1,107 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kandahar`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **25 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **$67 M / yr** | $96 |
| Steady-state, low-ridership (year 11+) | **$81 M / yr** | $115 |
| Steady-state, high-ridership (year 11+) | **$78 M / yr** | $112 |
| Steady-state, operating-neutral revenue case | **$67 M / yr** | $95 |
| Lifecycle envelope (yr 1–35, low scenario) | **$2.69 bn cumulative** | $3,847 |
| Lifecycle envelope (yr 1–35, high scenario) | **$2.63 bn cumulative** | $3,760 |
| Lifecycle envelope (yr 1–35, operating-neutral after opening) | **$2.34 bn cumulative** | $3,348 |

_Population basis: 700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 35, debt service drops to zero; the operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $14 M / yr → $12 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | $465 M | 4.5% | 35 y, 10 y grace | $31 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | $194 M | 18.0% | 35 y, 10 y grace | $35 M / yr |
| Government equity (no debt service) | 15% | $116 M | — | — | — |
| **Total** | **100%** | **$775 M** | | | **$67 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral $21 M / yr + bonds $35 M / yr = **$56 M / yr** total — plus the equity tranche amortised across construction ($12 M / yr × 10 yr). Principal repayment begins in year 11 on a 25-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $10 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $8.5 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $160 k |
| Traction energy (113.1 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (396 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $499 k |
| **OPEX subtotal** | | **$20 M / yr** |

_Annual fleet utilisation: 56 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 9.4 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$75 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Base affordability marker: a monthly unlimited-ride pass costs **5 % of median monthly income**. The operating-neutral case lifts that to **6 %** (+20 % over the baseline) and pairs it with higher service uptake plus station retail and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Baseline single-trip fare (5 % pass) | $0.12 |
| Operating-neutral single-trip fare (6 % pass) | $0.15 |
| Day pass (3 trips) | $0.38 (15 % bulk discount) |
| Monthly unlimited pass | $4.50 (~6 % of median monthly income) |
| Annual pass | $49.50 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 18-30% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (168,480 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Post-grace debt service remains a capital-funding obligation in the government commitment table above.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 66,780 | 111,300 | 322,071 |
| Daily paid trips / catchment | 18% | 30% | 87% |
| Daily paid trips / city population | 10% | 16% | 46% |
| Annual paid trips | 24.4 M | 40.6 M | 117.6 M |
| Farebox revenue | $3.7 M / yr | $6.1 M / yr | $18 M / yr |
| Station shop leases | $805 k / yr | $805 k / yr | $805 k / yr |
| Advertising boards | $1.1 M / yr | $1.1 M / yr | $1.1 M / yr |
| **Total revenue** | **$5.6 M / yr** | **$8.0 M / yr** | **$20 M / yr** |
| Revenue / OPEX recovery | 28% | 41% | 100% |
| Country farebox-only policy target (diagnostic) | 30% | 30% | 30% |
| Remaining steady-state gov commitment | $81 M / yr | $78 M / yr | **$67 M / yr** |
| Operating surplus after OPEX | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 7,624 m² of station shop/kiosk leases at $10/m²/month and 1,424 advertising boards at $75/board/month, with occupancy derates applied._

**Caveats:** The funding-stack 60/25/15 split, the 6 % operating-neutral fare target, the 18-30% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kandahar.toml`](kandahar.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kandahar-network-map.png`](kandahar-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kandahar.corridor.geojson`](kandahar.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kandahar.stations.json`](kandahar.stations.json) | Machine-readable station list |
| [`kandahar.design-quality.yaml`](kandahar.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kandahar

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kandahar \
    --sidecar .cache/osr-pipeline/rasters/kandahar.grid.json \
    --out-dir designs/.../Kandahar

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kandahar.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kandahar.sh` chains steps 3 + drift tests into a single command.
