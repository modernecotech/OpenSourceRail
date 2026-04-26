# Tunis — Urban Rail Network

**Country:** TN · **Population:** 2,900,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Tunis rail network on OpenStreetMap](tunis-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`tunis.corridor.geojson`](tunis.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 120 |
| Interchange stations | 19 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 47.9% |
| Route length (double track) | 237.9 km |
| Revenue fleet | 172 × 4-car trainsets |
| Spare + cold-reserve | 20 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 42.6 km | 21 | 35 | SE Outer ↔ W Outer |
| line-2 | 38.2 km | 21 | 31 | W Outer ↔ NE Outer |
| line-3 | 32.9 km | 20 | 27 | N Mid ↔ S Outer |
| line-4 | 40.9 km | 20 | 34 | SE Outer ↔ NW Outer |
| line-5 | 83.3 km | 39 | 65 | W Mid ↔ W Mid |
| **Total** | **237.9 km** | **120 unique** | **192** | |

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
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 6,480 = **64,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **648,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **138,910 – 208,365 trips/day**

## Catchment

- City population: **2,900,000**
- Anchor-weighted coverage: 47.9%
- Catchment population: **≈ 1,389,100** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 19 | 500 kW | 3000 kWh |
| Major | 46 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 7 | 500 kW | 3000 kWh |
| **Total installed** | **119** | **50,200 kW** | **325,000 kWh** |

Aggregate station-rail charging power: **40,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 460 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (223.9 km @ €3.5 M/km) | €784 M |
| Elevated (13.2 km @ €18 M/km) | €237 M |
| Elevated-interchange premium (11 sites @ €20 M) | €220 M |
| **Civil subtotal** | **€1.24 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | €0.4 M | €0.8 M |
| `standard` | 46 | €1.5 M | €69 M |
| `major` | 46 | €3.0 M | €138 M |
| `terminal` | 7 | €2.5 M | €18 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 19 | €4.5 M | €86 M |
| **Stations subtotal** | | | **€314 M** |

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
| `metro-4car` (revenue + spare + cold reserve) | 192 | €3.0 M | €576 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 237.9 km × €0.4 M/km | €95 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 237.9 km × €0.8 M/km | €190 M |
| EPC integration + project management (7%) | on subtotal | €172 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.24 bn |
| Stations | €314 M |
| Depots | €46 M |
| Rolling stock | €576 M |
| Signalling + power | €285 M |
| EPC overhead (7%) | €172 M |
| **CAPEX total** | **€2.63 bn** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €908 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh tunis`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.58 bn | 4.5% | 25 y, 5 y grace | €121 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €658 M | 9.0% | 25 y, 5 y grace | €72 M / yr |
| Government equity (no debt service) | 15% | €395 M | — | — | — |
| **Total** | **100%** | **€2.63 bn** | | | **€194 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €23 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €32 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €4.7 M |
| Traction energy (540.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,439 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €7.8 M |
| **OPEX subtotal** | | **€68 M / yr** |

_Annual fleet utilisation: 172 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 33.8 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$350 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.54 (~$0.58 USD) |
| Day pass (3 trips) | €1.37 (15 % bulk discount) |
| Monthly unlimited pass | €16.10 (~5 % of median monthly income) |
| Annual pass | €177.10 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 52.9 M | 105.8 M |
| Farebox revenue | €28 M / yr | €57 M / yr |
| Farebox / OPEX recovery | 42% | 84% |
| Country policy-target recovery (diagnostic) | 50% | 50% |
| Operating shortfall (gov subsidy required) | €39 M / yr | €11 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€233 M / yr** | **€204 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`tunis.toml`](tunis.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`tunis-network-map.png`](tunis-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`tunis.corridor.geojson`](tunis.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`tunis.stations.json`](tunis.stations.json) | Machine-readable station list |
| [`tunis.design-quality.yaml`](tunis.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug tunis

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug tunis \
    --sidecar .cache/osr-pipeline/rasters/tunis.grid.json \
    --out-dir designs/.../Tunis

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../tunis.toml \
    --out designs/.../README.md
```

`scripts/regenerate-tunis.sh` chains steps 3 + drift tests into a single command.
