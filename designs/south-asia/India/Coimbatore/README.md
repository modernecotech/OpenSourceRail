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
| Unique stations | 122 |
| Interchange stations | 21 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 31.2% |
| Route length (double track) | 267.9 km |
| Revenue fleet | 193 × 6-car trainsets |
| Spare + cold-reserve | 21 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 52.2 km | 20 | 42 | NE Outer ↔ SW Outer |
| line-2 | 47.9 km | 23 | 39 | S Outer ↔ N Outer |
| line-3 | 37.0 km | 21 | 30 | E Outer ↔ W Mid |
| line-4 | 37.3 km | 19 | 30 | N Outer ↔ S Mid |
| line-5 | 93.4 km | 40 | 73 | W Mid ↔ W Mid |
| **Total** | **267.9 km** | **122 unique** | **214** | |

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
| Interchange | 21 | 500 kW | 3000 kWh |
| Major | 26 | 400 kW | 2500 kWh |
| Standard | 68 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **123** | **49,800 kW** | **325,000 kWh** |

Aggregate station-rail charging power: **31,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (243.3 km @ €3.5 M/km) | €851 M |
| Elevated (23.8 km @ €18 M/km) | €429 M |
| Elevated-interchange premium (10 sites @ €20 M) | €200 M |
| **Civil subtotal** | **€1.48 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 68 | €1.5 M | €102 M |
| `major` | 26 | €3.0 M | €78 M |
| `terminal` | 7 | €2.5 M | €18 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 21 | €4.5 M | €94 M |
| **Stations subtotal** | | | **€295 M** |

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
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 267.9 km × €0.4 M/km | €107 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 267.9 km × €0.8 M/km | €214 M |
| EPC integration + project management (7%) | on subtotal | €217 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.48 bn |
| Stations | €295 M |
| Depots | €46 M |
| Rolling stock | €963 M |
| Signalling + power | €321 M |
| EPC overhead (7%) | €217 M |
| **CAPEX total** | **€3.32 bn** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €1,077 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh coimbatore`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.99 bn | 4.0% | 25 y, 5 y grace | €147 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €830 M | 7.2% | 25 y, 5 y grace | €80 M / yr |
| Government equity (no debt service) | 15% | €498 M | — | — | — |
| **Total** | **100%** | **€3.32 bn** | | | **€226 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €39 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €36 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €5.3 M |
| Traction energy (909.8 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,619 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.8 M |
| **OPEX subtotal** | | **€86 M / yr** |

_Annual fleet utilisation: 193 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 37.9 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$230 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

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
| Farebox / OPEX recovery | 23% | 46% |
| Country policy-target recovery (diagnostic) | 55% | 55% |
| Operating shortfall (gov subsidy required) | €66 M / yr | €46 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€292 M / yr** | **€273 M / yr** |

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
