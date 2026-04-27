# Khartoum — Urban Rail Network

**Country:** SD · **Population:** 5,829,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Khartoum rail network on OpenStreetMap](khartoum-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`khartoum.corridor.geojson`](khartoum.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 151 |
| Interchange stations | 15 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 22.1% |
| Route length (double track) | 362.7 km |
| Revenue fleet | 258 × 6-car trainsets |
| Spare + cold-reserve | 29 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 58.5 km | 26 | 47 | SE Outer ↔ NW Outer |
| line-2 | 55.2 km | 26 | 45 | N Outer ↔ S Outer |
| line-3 | 51.1 km | 25 | 41 | NW Outer ↔ SE Outer |
| line-4 | 48.6 km | 21 | 39 | SW Outer ↔ NE Outer |
| line-5 | 149.3 km | 54 | 115 | W Outer ↔ W Outer |
| **Total** | **362.7 km** | **151 unique** | **287** | |

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
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 10,800 = **108,000 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,080,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **128,820 – 193,231 trips/day**

## Catchment

- City population: **5,829,000**
- Anchor-weighted coverage: 22.1%
- Catchment population: **≈ 1,288,209** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 15 | 500 kW | 3000 kWh |
| Major | 37 | 400 kW | 2500 kWh |
| Standard | 90 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **150** | **57,800 kW** | **378,500 kWh** |

Aggregate station-rail charging power: **34,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, **onboard-first train control with a sparse LoRa-linked wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (343.5 km @ €3.5 M/km) | €1.20 bn |
| Elevated (18.1 km @ €18 M/km) | €326 M |
| Elevated-interchange premium (7 sites @ €20 M) | €140 M |
| **Civil subtotal** | **€1.67 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | €0.4 M | €0.8 M |
| `standard` | 90 | €1.5 M | €135 M |
| `major` | 37 | €3.0 M | €111 M |
| `terminal` | 7 | €2.5 M | €18 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 15 | €4.5 M | €68 M |
| **Stations subtotal** | | | **€335 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 7 | €3.0 M | €21 M |
| **Depots subtotal** | | | **€46 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion traction battery (~$80/kWh, RFC 0021 §3 — distinct from the trackside stationary battery in the *Systems* section below), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body. Motors and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 287 | €4.5 M | €1.29 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (onboard ATC + LoRa-linked wayside W-Nodes, RFC 0019/0001) | 362.7 km × €0.1 M/km | €36 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 362.7 km × €0.8 M/km | €289 M |
| EPC integration + project management (7%) | on subtotal | €257 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.67 bn |
| Stations | €335 M |
| Depots | €46 M |
| Rolling stock | €1.29 bn |
| Signalling + power | €325 M |
| EPC overhead (7%) | €257 M |
| **CAPEX total** | **€3.92 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €673 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh khartoum`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–10** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 11** and runs for **30 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–10) | **€277 M / yr** | €47 |
| Steady-state, low-ridership (year 11+) | **€350 M / yr** | €60 |
| Steady-state, high-ridership (year 11+) | **€332 M / yr** | €57 |
| Lifecycle envelope (yr 1–40, low scenario) | **€13.25 bn cumulative** | €2,274 |
| Lifecycle envelope (yr 1–40, high scenario) | **€12.72 bn cumulative** | €2,181 |

_Population basis: 5,829,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero and only the OPEX shortfall remains — ~€80 M / yr (low) → €62 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.35 bn | 3.0% | 40 y, 10 y grace | €120 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €981 M | 15.0% | 40 y, 10 y grace | €149 M / yr |
| Government equity (no debt service) | 15% | €588 M | — | — | — |
| **Total** | **100%** | **€3.92 bn** | | | **€269 M / yr** |

_During the 10-year grace period the operator pays interest only — multilateral €71 M / yr + bonds €147 M / yr = **€218 M / yr** total — plus the equity tranche amortised across construction (€59 M / yr × 10 yr). Principal repayment begins in year 11 on a 30-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €52 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €41 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €1.8 M |
| Traction energy (1216.2 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,188 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €3.7 M |
| **OPEX subtotal** | | **€98 M / yr** |

_Annual fleet utilisation: 258 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 50.7 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$110 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.17 (~$0.18 USD) |
| Day pass (3 trips) | €0.43 (15 % bulk discount) |
| Monthly unlimited pass | €5.06 (~5 % of median monthly income) |
| Annual pass | €55.66 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 106.4 M | 212.8 M |
| Farebox revenue | €18 M / yr | €36 M / yr |
| Farebox / OPEX recovery | 18% | 37% |
| Country policy-target recovery (diagnostic) | 30% | 30% |
| Operating shortfall (gov subsidy required) | €80 M / yr | €62 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€350 M / yr** | **€332 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`khartoum.toml`](khartoum.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`khartoum-network-map.png`](khartoum-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`khartoum.corridor.geojson`](khartoum.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`khartoum.stations.json`](khartoum.stations.json) | Machine-readable station list |
| [`khartoum.design-quality.yaml`](khartoum.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug khartoum

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug khartoum \
    --sidecar .cache/osr-pipeline/rasters/khartoum.grid.json \
    --out-dir designs/.../Khartoum

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../khartoum.toml \
    --out designs/.../README.md
```

`scripts/regenerate-khartoum.sh` chains steps 3 + drift tests into a single command.
