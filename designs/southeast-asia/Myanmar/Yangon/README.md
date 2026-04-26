# Yangon — Urban Rail Network

**Country:** MM · **Population:** 5,200,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Yangon rail network on OpenStreetMap](yangon-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`yangon.corridor.geojson`](yangon.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 213 |
| Interchange stations | 43 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 56.4% |
| Route length (double track) | 417.5 km |
| Revenue fleet | 301 × 6-car trainsets |
| Spare + cold-reserve | 34 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 53.5 km | 27 | 42 | NW Outer ↔ SE Outer |
| line-2 | 51.9 km | 23 | 41 | SE Outer ↔ NW Outer |
| line-3 | 42.3 km | 20 | 35 | NE Mid ↔ W Outer |
| line-4 | 32.1 km | 18 | 27 | SE Mid ↔ N Mid |
| line-5 | 39.0 km | 21 | 31 | S Outer ↔ N Mid |
| line-6 | 38.8 km | 19 | 31 | N Mid ↔ S Outer |
| line-7 | 43.8 km | 21 | 36 | E Mid ↔ SW Outer |
| line-8 | 38.6 km | 20 | 31 | SW Mid ↔ NE Outer |
| line-9 | 77.4 km | 45 | 61 | NW Mid ↔ NW Mid |
| **Total** | **417.5 km** | **213 unique** | **335** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **293,279 – 439,919 trips/day**

## Catchment

- City population: **5,200,000**
- Anchor-weighted coverage: 56.4%
- Catchment population: **≈ 2,932,799** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 43 | 500 kW | 3000 kWh |
| Major | 97 | 400 kW | 2500 kWh |
| Standard | 51 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **207** | **88,100 kW** | **558,500 kWh** |

Aggregate station-rail charging power: **86,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (375.2 km @ €3.5 M/km) | €1.31 bn |
| Elevated (39.3 km @ €18 M/km) | €708 M |
| Elevated-interchange premium (18 sites @ €20 M) | €360 M |
| **Civil subtotal** | **€2.38 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 7 | €0.4 M | €2.8 M |
| `standard` | 51 | €1.5 M | €76 M |
| `major` | 97 | €3.0 M | €291 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 4 | €4.5 M | €18 M |
| `interchange-elevated` | 39 | €4.5 M | €176 M |
| **Stations subtotal** | | | **€604 M** |

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
| `metro-6car` (revenue + spare + cold reserve) | 335 | €4.5 M | €1.51 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 417.5 km × €0.4 M/km | €166 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 417.5 km × €0.8 M/km | €332 M |
| EPC integration + project management (7%) | on subtotal | €354 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.38 bn |
| Stations | €604 M |
| Depots | €70 M |
| Rolling stock | €1.51 bn |
| Signalling + power | €497 M |
| EPC overhead (7%) | €354 M |
| **CAPEX total** | **€5.41 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €1,041 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh yangon`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €3.25 bn | 4.5% | 30 y, 10 y grace | €250 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.35 bn | 13.0% | 30 y, 10 y grace | €193 M / yr |
| Government equity (no debt service) | 15% | €812 M | — | — | — |
| **Total** | **100%** | **€5.41 bn** | | | **€442 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €60 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €61 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €8.3 M |
| Traction energy (1418.9 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (2,517 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.1 M |
| **OPEX subtotal** | | **€135 M / yr** |

_Annual fleet utilisation: 301 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 59.1 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$130 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.20 (~$0.22 USD) |
| Day pass (3 trips) | €0.51 (15 % bulk discount) |
| Monthly unlimited pass | €5.98 (~5 % of median monthly income) |
| Annual pass | €65.78 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 94.9 M | 189.8 M |
| Farebox revenue | €19 M / yr | €38 M / yr |
| Farebox / OPEX recovery | 14% | 28% |
| Country policy-target recovery (diagnostic) | 40% | 40% |
| Operating shortfall (gov subsidy required) | €116 M / yr | €97 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€558 M / yr** | **€539 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`yangon.toml`](yangon.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`yangon-network-map.png`](yangon-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`yangon.corridor.geojson`](yangon.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`yangon.stations.json`](yangon.stations.json) | Machine-readable station list |
| [`yangon.design-quality.yaml`](yangon.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug yangon

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug yangon \
    --sidecar .cache/osr-pipeline/rasters/yangon.grid.json \
    --out-dir designs/.../Yangon

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../yangon.toml \
    --out designs/.../README.md
```

`scripts/regenerate-yangon.sh` chains steps 3 + drift tests into a single command.
