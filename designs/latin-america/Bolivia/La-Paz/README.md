# La-Paz — Urban Rail Network

**Country:** BO · **Population:** 1,815,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![La-Paz rail network on OpenStreetMap](la-paz-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`la-paz.corridor.geojson`](la-paz.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 6 |
| Unique stations | 114 |
| Interchange stations | 24 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.7% |
| Route length (double track) | 212.3 km |
| Revenue fleet | 156 × 4-car trainsets |
| Spare + cold-reserve | 18 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 39.4 km | 22 | 32 | E Outer ↔ W Outer |
| line-2 | 42.9 km | 19 | 35 | NE Outer ↔ SW Outer |
| line-3 | 23.3 km | 15 | 20 | S Mid ↔ NW Mid |
| line-4 | 25.5 km | 13 | 21 | N Mid ↔ SE Outer |
| line-5 | 22.7 km | 13 | 19 | N Mid ↔ SE Mid |
| line-6 | 58.5 km | 33 | 47 | W Mid ↔ W Mid |
| **Total** | **212.3 km** | **114 unique** | **174** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 90 m |
| Max speed | 90 km/h |
| Onboard battery | 460 kWh per trainset |
| Nominal capacity | 540 pax (seated + standing, `metro-4car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 540 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 540 × 12 = **6,480 pphpd**
- **Network peak throughput (all lines, both directions):** 6 lines × 2 directions × 6,480 = **77,760 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **777,600 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **102,910 – 154,365 trips/day**

## Catchment

- City population: **1,815,000**
- Anchor-weighted coverage: 56.7%
- Catchment population: **≈ 1,029,104** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 24 | 500 kW | 3000 kWh |
| Major | 50 | 400 kW | 2500 kWh |
| Standard | 28 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **112** | **49,900 kW** | **320,000 kWh** |

Aggregate station-rail charging power: **47,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 460 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (185.2 km @ €3.5 M/km) | €648 M |
| Elevated (25.9 km @ €18 M/km) | €467 M |
| Elevated-interchange premium (13 sites @ €20 M) | €260 M |
| **Civil subtotal** | **€1.38 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 3 | €0.4 M | €1.2 M |
| `standard` | 28 | €1.5 M | €42 M |
| `major` | 50 | €3.0 M | €150 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 2 | €4.5 M | €9.0 M |
| `interchange-elevated` | 22 | €4.5 M | €99 M |
| **Stations subtotal** | | | **€327 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 9 | €3.0 M | €27 M |
| **Depots subtotal** | | | **€52 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion traction battery (~$80/kWh, RFC 0021 §3 — distinct from the trackside stationary battery in the *Systems* section below), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body. Motors and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-4car` (revenue + spare + cold reserve) | 174 | €3.0 M | €522 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 212.3 km × €0.4 M/km | €84 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 212.3 km × €0.8 M/km | €169 M |
| EPC integration + project management (7%) | on subtotal | €177 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.38 bn |
| Stations | €327 M |
| Depots | €52 M |
| Rolling stock | €522 M |
| Signalling + power | €253 M |
| EPC overhead (7%) | €177 M |
| **CAPEX total** | **€2.71 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,491 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh la-paz`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.62 bn | 4.5% | 25 y, 5 y grace | €125 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €677 M | 10.5% | 25 y, 5 y grace | €82 M / yr |
| Government equity (no debt service) | 15% | €406 M | — | — | — |
| **Total** | **100%** | **€2.71 bn** | | | **€207 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €21 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €35 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €4.2 M |
| Traction energy (490.3 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,286 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.8 M |
| **OPEX subtotal** | | **€66 M / yr** |

_Annual fleet utilisation: 156 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 30.6 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$290 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.44 (~$0.48 USD) |
| Day pass (3 trips) | €1.13 (15 % bulk discount) |
| Monthly unlimited pass | €13.34 (~5 % of median monthly income) |
| Annual pass | €146.74 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 33.1 M | 66.2 M |
| Farebox revenue | €15 M / yr | €29 M / yr |
| Farebox / OPEX recovery | 22% | 45% |
| Country policy-target recovery (diagnostic) | 50% | 50% |
| Operating shortfall (gov subsidy required) | €51 M / yr | €36 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€258 M / yr** | **€244 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`la-paz.toml`](la-paz.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`la-paz-network-map.png`](la-paz-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`la-paz.corridor.geojson`](la-paz.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`la-paz.stations.json`](la-paz.stations.json) | Machine-readable station list |
| [`la-paz.design-quality.yaml`](la-paz.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug la-paz

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug la-paz \
    --sidecar .cache/osr-pipeline/rasters/la-paz.grid.json \
    --out-dir designs/.../La-Paz

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../la-paz.toml \
    --out designs/.../README.md
```

`scripts/regenerate-la-paz.sh` chains steps 3 + drift tests into a single command.
