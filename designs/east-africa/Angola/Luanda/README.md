# Luanda — Urban Rail Network

**Country:** AO · **Population:** 9,085,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Luanda rail network on OpenStreetMap](luanda-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`luanda.corridor.geojson`](luanda.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 169 |
| Interchange stations | 37 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 63.8% |
| Route length (double track) | 389.9 km |
| Revenue fleet | 283 × 6-car trainsets |
| Spare + cold-reserve | 34 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 58.6 km | 21 | 47 | NE Outer ↔ SW Outer |
| line-2 | 30.0 km | 15 | 25 | N Mid ↔ W Mid |
| line-3 | 43.9 km | 16 | 36 | SW Outer ↔ NE Mid |
| line-4 | 42.5 km | 17 | 35 | SE Outer ↔ NW Mid |
| line-5 | 39.9 km | 17 | 32 | SE Outer ↔ W Mid |
| line-6 | 30.7 km | 12 | 26 | S Mid ↔ N Mid |
| line-7 | 33.9 km | 16 | 28 | E Outer ↔ NW Mid |
| line-8 | 32.9 km | 15 | 27 | NE Outer ↔ W Mid |
| line-9 | 77.4 km | 41 | 61 | NE Mid ↔ NE Mid |
| **Total** | **389.9 km** | **169 unique** | **317** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 138 m |
| Max speed | 90 km/h |
| Onboard battery | 720 kWh per trainset |
| Nominal capacity | 900 pax (seated + standing, `metro-6car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 900 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 900 × 12 = **10,800 pphpd**
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 10,800 = **194,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,944,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **579,623 – 869,434 trips/day**

## Catchment

- City population: **9,085,000**
- Anchor-weighted coverage: 63.8%
- Catchment population: **≈ 5,796,230** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 37 | 500 kW | 3000 kWh |
| Major | 15 | 400 kW | 2500 kWh |
| Standard | 90 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **158** | **64,000 kW** | **413,500 kWh** |

Aggregate station-rail charging power: **42,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, **onboard-first train control with a sparse LoRa-linked wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (365.9 km @ €3.5 M/km) | €1.28 bn |
| Elevated (22.7 km @ €18 M/km) | €408 M |
| Elevated-interchange premium (19 sites @ €20 M) | €380 M |
| **Civil subtotal** | **€2.07 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 12 | €0.4 M | €4.8 M |
| `standard` | 90 | €1.5 M | €135 M |
| `major` | 15 | €3.0 M | €45 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 37 | €4.5 M | €166 M |
| **Stations subtotal** | | | **€392 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 15 | €3.0 M | €45 M |
| **Depots subtotal** | | | **€70 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion traction battery (~$80/kWh, RFC 0021 §3 — distinct from the trackside stationary battery in the *Systems* section below), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body. Motors and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 317 | €4.5 M | €1.43 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (onboard ATC + LoRa-linked wayside W-Nodes, RFC 0019/0001) | 389.9 km × €0.1 M/km | €39 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 389.9 km × €0.8 M/km | €311 M |
| EPC integration + project management (7%) | on subtotal | €302 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.07 bn |
| Stations | €392 M |
| Depots | €70 M |
| Rolling stock | €1.43 bn |
| Signalling + power | €350 M |
| EPC overhead (7%) | €302 M |
| **CAPEX total** | **€4.61 bn** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €507 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh luanda`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€395 M / yr** | €44 |
| Steady-state, low-ridership (year 6+) | **€419 M / yr** | €46 |
| Steady-state, high-ridership (year 6+) | **€362 M / yr** | €40 |
| Lifecycle envelope (yr 1–25, low scenario) | **€10.36 bn cumulative** | €1,141 |
| Lifecycle envelope (yr 1–25, high scenario) | **€9.22 bn cumulative** | €1,015 |

_Population basis: 9,085,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€57 M / yr (low) → €0 k / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.77 bn | 4.5% | 25 y, 5 y grace | €213 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.15 bn | 11.5% | 25 y, 5 y grace | €149 M / yr |
| Government equity (no debt service) | 15% | €691 M | — | — | — |
| **Total** | **100%** | **€4.61 bn** | | | **€362 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €124 M / yr + bonds €133 M / yr = **€257 M / yr** total — plus the equity tranche amortised across construction (€138 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €57 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €51 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €1.9 M |
| Traction energy (1334.1 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,351 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €8.7 M |
| **OPEX subtotal** | | **€118 M / yr** |

_Annual fleet utilisation: 283 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 55.6 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$240 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.37 (~$0.40 USD) |
| Day pass (3 trips) | €0.94 (15 % bulk discount) |
| Monthly unlimited pass | €11.04 (~5 % of median monthly income) |
| Annual pass | €121.44 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 165.8 M | 331.6 M |
| Farebox revenue | €61 M / yr | €122 M / yr |
| Farebox / OPEX recovery | 52% | 103% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €57 M / yr | €0 k / yr |
| Operating surplus (operator retained → capex sinking fund) | €0 k / yr | €3.7 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€419 M / yr** | **€362 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`luanda.toml`](luanda.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`luanda-network-map.png`](luanda-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`luanda.corridor.geojson`](luanda.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`luanda.stations.json`](luanda.stations.json) | Machine-readable station list |
| [`luanda.design-quality.yaml`](luanda.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug luanda

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug luanda \
    --sidecar .cache/osr-pipeline/rasters/luanda.grid.json \
    --out-dir designs/.../Luanda

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../luanda.toml \
    --out designs/.../README.md
```

`scripts/regenerate-luanda.sh` chains steps 3 + drift tests into a single command.
