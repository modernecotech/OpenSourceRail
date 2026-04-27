# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`sanaa.corridor.geojson`](sanaa.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 126 |
| Interchange stations | 32 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 78.0% |
| Route length (double track) | 260.8 km |
| Revenue fleet | 193 × 6-car trainsets |
| Spare + cold-reserve | 25 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 41.2 km | 17 | 34 | SE Outer ↔ NW Outer |
| line-2 | 28.8 km | 15 | 24 | S Mid ↔ N Outer |
| line-3 | 22.1 km | 10 | 19 | N Mid ↔ SW Mid |
| line-4 | 27.1 km | 13 | 23 | N Mid ↔ S Mid |
| line-5 | 27.1 km | 10 | 23 | SE Outer ↔ SW Inner |
| line-6 | 24.5 km | 12 | 20 | E Inner ↔ W Outer |
| line-7 | 20.6 km | 9 | 18 | NW Mid ↔ E Mid |
| line-8 | 17.2 km | 11 | 15 | SW Mid ↔ NE Inner |
| line-9 | 52.3 km | 29 | 42 | NW Mid ↔ W Inner |
| **Total** | **260.8 km** | **126 unique** | **218** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **307,125 – 460,687 trips/day**

## Catchment

- City population: **3,937,500**
- Anchor-weighted coverage: 78.0%
- Catchment population: **≈ 3,071,250** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 32 | 500 kW | 3000 kWh |
| Major | 34 | 400 kW | 2500 kWh |
| Standard | 36 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **118** | **52,900 kW** | **338,000 kWh** |

Aggregate station-rail charging power: **49,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, **onboard-first train control with a sparse LoRa-linked wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (239.4 km @ €3.5 M/km) | €838 M |
| Elevated (20.6 km @ €18 M/km) | €370 M |
| Elevated-interchange premium (19 sites @ €20 M) | €380 M |
| **Civil subtotal** | **€1.59 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 8 | €0.4 M | €3.2 M |
| `standard` | 36 | €1.5 M | €54 M |
| `major` | 34 | €3.0 M | €102 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 32 | €4.5 M | €144 M |
| **Stations subtotal** | | | **€344 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 218 | €4.5 M | €981 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (onboard ATC + LoRa-linked wayside W-Nodes, RFC 0019/0001) | 260.8 km × €0.1 M/km | €26 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 260.8 km × €0.8 M/km | €208 M |
| EPC integration + project management (7%) | on subtotal | €225 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.59 bn |
| Stations | €344 M |
| Depots | €70 M |
| Rolling stock | €981 M |
| Signalling + power | €234 M |
| EPC overhead (7%) | €225 M |
| **CAPEX total** | **€3.44 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €874 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh sanaa`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€268 M / yr** | €68 |
| Steady-state, low-ridership (year 11+) | **€335 M / yr** | €85 |
| Steady-state, high-ridership (year 11+) | **€326 M / yr** | €83 |
| Lifecycle envelope (yr 1–40, low scenario) | **€12.74 bn cumulative** | €3,235 |
| Lifecycle envelope (yr 1–40, high scenario) | **€12.47 bn cumulative** | €3,168 |

_Population basis: 3,937,500 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero and only the OPEX shortfall remains — ~€74 M / yr (low) → €65 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.07 bn | 3.0% | 40 y, 10 y grace | €105 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €861 M | 18.0% | 40 y, 10 y grace | €156 M / yr |
| Government equity (no debt service) | 15% | €516 M | — | — | — |
| **Total** | **100%** | **€3.44 bn** | | | **€261 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €62 M / yr + bonds €155 M / yr = **€217 M / yr** total — plus the equity tranche amortised across construction (€52 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €39 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €40 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €1.3 M |
| Traction energy (909.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,577 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €1.9 M |
| **OPEX subtotal** | | **€83 M / yr** |

_Annual fleet utilisation: 193 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 37.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$80 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.12 (~$0.13 USD) |
| Day pass (3 trips) | €0.31 (15 % bulk discount) |
| Monthly unlimited pass | €3.68 (~5 % of median monthly income) |
| Annual pass | €40.48 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 71.9 M | 143.7 M |
| Farebox revenue | €8.8 M / yr | €18 M / yr |
| Farebox / OPEX recovery | 11% | 21% |
| Country policy-target recovery (diagnostic) | 25% | 25% |
| Operating shortfall (gov subsidy required) | €74 M / yr | €65 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€335 M / yr** | **€326 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`sanaa-network-map.png`](sanaa-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`sanaa.stations.json`](sanaa.stations.json) | Machine-readable station list |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug sanaa

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug sanaa \
    --sidecar .cache/osr-pipeline/rasters/sanaa.grid.json \
    --out-dir designs/.../Sanaa

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../sanaa.toml \
    --out designs/.../README.md
```

`scripts/regenerate-sanaa.sh` chains steps 3 + drift tests into a single command.
