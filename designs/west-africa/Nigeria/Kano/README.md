# Kano — Urban Rail Network

**Country:** NG · **Population:** 4,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kano rail network on OpenStreetMap](kano-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kano.corridor.geojson`](kano.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 153 |
| Interchange stations | 17 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 36.9% |
| Route length (double track) | 361.9 km |
| Revenue fleet | 429 × 6-car trainsets |
| Revenue fleet passenger capacity | 308,880 AW2 pax (411,840 AW3 crush) |
| Spare + cold-reserve | 47 × 6-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 54.6 km | 23 | 72 | S Outer ↔ NE Outer |
| line-2 | 50.9 km | 21 | 68 | NW Outer ↔ SE Outer |
| line-3 | 49.4 km | 22 | 65 | SW Mid ↔ NE Outer |
| line-4 | 41.9 km | 20 | 56 | NE Mid ↔ W Outer |
| line-5 | 52.1 km | 23 | 69 | NW Outer ↔ SE Outer |
| line-6 | 113.0 km | 45 | 146 | NW Outer ↔ NW Outer |
| **Total** | **361.9 km** | **153 unique** | **476** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 111 m |
| Max speed | 100 km/h |
| Onboard battery | 720 kWh per trainset |
| Seats | 120 longitudinal seats |
| Nominal capacity (AW2) | 720 pax (seated + standing, `metro-6car` per RFC 0008 §1) |
| Crush capacity (AW3) | 960 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 308,880 AW2 pax (411,840 AW3 crush) |
| Total fleet capacity | 342,720 AW2 pax (456,960 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 720 AW2 passengers (`metro-6car`)
- **Revenue fleet simultaneous capacity:** 429 × 720 = **308,880 AW2 passengers** (411,840 AW3 crush)
- **Total fleet passenger capacity:** 476 × 720 = **342,720 AW2 passengers** (456,960 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 720 × 20 = **14,400 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 14,400 = **172,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,728,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **1,382,400 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% of catchment): ≈ **387,450 – 697,410 trips/day**

## Catchment

- City population: **4,200,000**
- Anchor-weighted coverage: 36.9%
- Catchment population: **≈ 1,549,800** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 17 | 500 kW | 3000 kWh |
| Major | 31 | 400 kW | 2500 kWh |
| Standard | 92 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **150** | **58,000 kW** | **379,500 kWh** |

Aggregate station-rail charging power: **81,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 24.0 kWh/km | 6 cars × 4 kWh/car-km planning basis |
| Average one-way line energy | 1,448 kWh | 60.3 km average line length |
| Onboard battery coverage | 0.5× average line run | 720 kWh usable pack |
| Average 60 s dwell charge | 8.8 kWh/stop | 529 kW average charger across stops |
| Stops to refill one trainset pack | 82 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 290 MWh/day | 5 peak-sun-hour planning proxy before local derates |
| Station/depot stationary storage | 380 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (297.1 km @ $3.0 M/km) | $891 M |
| Elevated (63.8 km @ $12.0 M/km) | $765 M |
| Elevated-interchange premium (7 sites @ $4.50 M) | $32 M |
| **Civil subtotal** | **$1.69 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | $600 k | $2.4 M |
| `standard` | 92 | $2.50 M | $230 M |
| `major` | 31 | $4.50 M | $140 M |
| `terminal` | 9 | $4.50 M | $40 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange` | 2 | $8.0 M | $16 M |
| `interchange-elevated` | 15 | $12.0 M | $180 M |
| **Stations subtotal** | | | **$613 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 476 | $8.40 M | $4.00 bn |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 2856 | $100 k | $286 M |
| High sensitivity check | 2856 | $200 k | $571 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 361.9 km × $0.050 M/km | $18 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $57 M |
| EPC integration + project management (7%) | on subtotal | $468 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $1.69 bn |
| Stations | $613 M |
| Depots | $30 M |
| Rolling stock | $4.00 bn |
| Railway production plant | $286 M |
| Residual train-control wayside + charging microgrids | $75 M |
| EPC overhead (7%) | $468 M |
| **CAPEX total** | **$7.16 bn** |
| Per-route-km | $20 M / km |
| Per-capita (city pop) | $1,704 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kano`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$174 M / yr** | $41 |
| Steady-state, low-ridership (year 8+) | **$289 M / yr** | $69 |
| Steady-state, high-ridership (year 8+) | **$236 M / yr** | $56 |
| Steady-state, operating-neutral revenue case | **$149 M / yr** | $36 |
| Lifecycle envelope (yr 1–40, low scenario) | **$10.75 bn cumulative** | $2,560 |
| Lifecycle envelope (yr 1–40, high scenario) | **$9.01 bn cumulative** | $2,145 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$6.14 bn cumulative** | $1,462 |

_Population basis: 4,200,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $140 M / yr → $87 M / yr; surplus applied to debt support is $0 k / yr → $0 k / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $2.86 bn | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $3.58 bn | 2.0% | 40 y, 7 y grace | $149 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 13.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $716 M | — | — | — |
| **Total** | **100%** | **$7.16 bn** | | | **$149 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $72 M / yr + fallback bonds $0 k / yr = **$72 M / yr** total. The $2.86 bn grant tranche carries no repayment or coupon. Government equity is drawn across construction ($102 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $160 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $47 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $902 k |
| Traction energy (2022.3 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, $0 / yr** | $0 k |
| Labour (2,183 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | $6.4 M |
| **OPEX subtotal** | | **$214 M / yr** |

_Annual fleet utilisation: 429 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 84.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$175 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.47 |
| Day pass (3 trips) | $1.19 (15 % bulk discount) |
| Monthly unlimited pass | $14.00 (~8 % of median monthly income) |
| Annual pass | $154.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = 25-45% of catchment × 365 service-days at the operating-neutral fare, capped by practical service capacity (1,382,400 trips/day). The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily paid trips | 387,450 | 697,410 | 1,207,495 |
| Daily paid trips / catchment | 25% | 45% | 78% |
| Daily paid trips / city population | 9% | 17% | 29% |
| Annual paid trips | 141.4 M | 254.6 M | 440.7 M |
| Farebox revenue | $66 M / yr | $119 M / yr | $206 M / yr |
| Station shop leases | $3.1 M / yr | $3.1 M / yr | $3.1 M / yr |
| Advertising boards | $5.1 M / yr | $5.1 M / yr | $5.1 M / yr |
| **Total revenue** | **$74 M / yr** | **$127 M / yr** | **$214 M / yr** |
| Revenue / OPEX recovery | 35% | 59% | 100% |
| Country farebox-only policy target (diagnostic) | 45% | 45% | 45% |
| Gross repayable-debt service + residual OPEX subsidy | $289 M / yr | $236 M / yr | **$149 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | $0 k / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $289 M / yr | $236 M / yr | **$149 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $0 k / yr | $0 / yr |

_Commercial-revenue assumptions: 21,136 m² of station shop/kiosk leases at $14/m²/month and 4,064 advertising boards at $122/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-pax bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kano.toml`](kano.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kano-network-map.png`](kano-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kano.corridor.geojson`](kano.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kano.stations.json`](kano.stations.json) | Machine-readable station list |
| [`kano.design-quality.yaml`](kano.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kano

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kano \
    --sidecar .cache/osr-pipeline/rasters/kano.grid.json \
    --out-dir designs/.../Kano

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kano.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kano.sh` chains steps 3 + drift tests into a single command.
