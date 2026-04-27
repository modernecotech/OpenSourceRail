# Coimbatore — Urban Rail Network

**Country:** IN · **Population:** 3,084,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Coimbatore rail network on OpenStreetMap](coimbatore-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`coimbatore.corridor.geojson`](coimbatore.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 120 |
| Interchange stations | 22 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 31.2% |
| Route length (double track) | 267.8 km |
| Revenue fleet | 193 × 6-car trainsets |
| Spare + cold-reserve | 21 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 52.2 km | 20 | 42 | NE Outer ↔ SW Outer |
| line-2 | 47.9 km | 23 | 39 | N Outer ↔ S Outer |
| line-3 | 36.9 km | 20 | 30 | W Mid ↔ E Outer |
| line-4 | 37.3 km | 19 | 30 | N Outer ↔ S Mid |
| line-5 | 93.4 km | 39 | 73 | W Mid ↔ W Mid |
| **Total** | **267.8 km** | **120 unique** | **214** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **96,220 – 144,331 trips/day**

## Catchment

- City population: **3,084,000**
- Anchor-weighted coverage: 31.2%
- Catchment population: **≈ 962,208** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 22 | 500 kW | 3000 kWh |
| Major | 24 | 400 kW | 2500 kWh |
| Standard | 67 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **121** | **49,200 kW** | **321,000 kWh** |

Aggregate station-rail charging power: **31,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, **onboard-first train control with a sparse LoRa-linked wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (241.8 km @ €3.5 M/km) | €846 M |
| Elevated (25.2 km @ €18 M/km) | €453 M |
| Elevated-interchange premium (11 sites @ €20 M) | €220 M |
| **Civil subtotal** | **€1.52 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 67 | €1.5 M | €100 M |
| `major` | 24 | €3.0 M | €72 M |
| `terminal` | 7 | €2.5 M | €18 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 22 | €4.5 M | €99 M |
| **Stations subtotal** | | | **€292 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 214 | €4.5 M | €963 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (onboard ATC + LoRa-linked wayside W-Nodes, RFC 0019/0001) | 267.8 km × €0.1 M/km | €27 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 267.8 km × €0.8 M/km | €214 M |
| EPC integration + project management (7%) | on subtotal | €214 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.52 bn |
| Stations | €292 M |
| Depots | €46 M |
| Rolling stock | €963 M |
| Signalling + power | €240 M |
| EPC overhead (7%) | €214 M |
| **CAPEX total** | **€3.27 bn** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €1,062 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh coimbatore`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (equity drawdown + interest-only grace on multilateral + bonds); steady-state operation begins **year 6** and runs for **20 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **€236 M / yr** | €76 |
| Steady-state, low-ridership (year 6+) | **€286 M / yr** | €93 |
| Steady-state, high-ridership (year 6+) | **€266 M / yr** | €86 |
| Lifecycle envelope (yr 1–25, low scenario) | **€6.90 bn cumulative** | €2,237 |
| Lifecycle envelope (yr 1–25, high scenario) | **€6.50 bn cumulative** | €2,108 |

_Population basis: 3,084,000 (catchment per `lib/city-batches/world-sample.toml`). After year 25, debt service drops to zero and only the OPEX shortfall remains — ~€63 M / yr (low) → €43 M / yr (high)._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.96 bn | 4.0% | 25 y, 5 y grace | €145 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €819 M | 7.2% | 25 y, 5 y grace | €78 M / yr |
| Government equity (no debt service) | 15% | €491 M | — | — | — |
| **Total** | **100%** | **€3.27 bn** | | | **€223 M / yr** |

_During the 5-year grace period the operator pays interest only — multilateral €79 M / yr + bonds €59 M / yr = **€138 M / yr** total — plus the equity tranche amortised across construction (€98 M / yr × 5 yr). Principal repayment begins in year 6 on a 20-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €39 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €37 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €1.3 M |
| Traction energy (909.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,619 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.8 M |
| **OPEX subtotal** | | **€83 M / yr** |

_Annual fleet utilisation: 193 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 37.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Affordability target: a monthly unlimited-ride pass costs **5 % of median monthly income**. Single-trip fare set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month then pays an effective ~40 % bulk discount on the pass, matching the structure used by Delhi Metro, Cairo Metro, and STIB.

| Product | Price target |
|---|---|
| Single-trip fare | €0.35 (~$0.38 USD) |
| Day pass (3 trips) | €0.90 (15 % bulk discount) |
| Monthly unlimited pass | €10.58 (~5 % of median monthly income) |
| Annual pass | €116.38 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 56.3 M | 112.6 M |
| Farebox revenue | €20 M / yr | €40 M / yr |
| Farebox / OPEX recovery | 24% | 48% |
| Country policy-target recovery (diagnostic) | 55% | 55% |
| Operating shortfall (gov subsidy required) | €63 M / yr | €43 M / yr |
| **Steady-state government commitment** (debt service + OPEX shortfall) | **€286 M / yr** | **€266 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`coimbatore.toml`](coimbatore.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`coimbatore-network-map.png`](coimbatore-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`coimbatore.corridor.geojson`](coimbatore.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`coimbatore.stations.json`](coimbatore.stations.json) | Machine-readable station list |
| [`coimbatore.design-quality.yaml`](coimbatore.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug coimbatore

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug coimbatore \
    --sidecar .cache/osr-pipeline/rasters/coimbatore.grid.json \
    --out-dir designs/.../Coimbatore

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../coimbatore.toml \
    --out designs/.../README.md
```

`scripts/regenerate-coimbatore.sh` chains steps 3 + drift tests into a single command.
