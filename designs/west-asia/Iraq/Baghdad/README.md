# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 9,780,429

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Baghdad rail network on OpenStreetMap](baghdad-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`baghdad.corridor.geojson`](baghdad.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 199 |
| Interchange stations | 32 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 44.3% |
| Route length (double track) | 436.5 km |
| Revenue fleet | 315 × 6-car trainsets |
| Spare + cold-reserve | 37 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 47.2 km | 21 | 38 | N Outer ↔ S Outer |
| line-2 | 47.9 km | 22 | 39 | SE Outer ↔ NW Outer |
| line-3 | 40.9 km | 21 | 34 | NE Outer ↔ SE Mid |
| line-4 | 39.0 km | 22 | 31 | NE Mid ↔ W Outer |
| line-5 | 41.0 km | 16 | 34 | E Mid ↔ W Outer |
| line-6 | 43.0 km | 18 | 35 | NW Outer ↔ SE Mid |
| line-7 | 39.5 km | 16 | 32 | N Outer ↔ SW Mid |
| line-8 | 38.6 km | 17 | 31 | SW Outer ↔ E Mid |
| line-9 | 99.4 km | 47 | 78 | NW Mid ↔ NW Mid |
| **Total** | **436.5 km** | **199 unique** | **352** | |

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
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **433,273 – 649,909 trips/day**

## Catchment

- City population: **9,780,429**
- Anchor-weighted coverage: 44.3%
- Catchment population: **≈ 4,332,730** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 32 | 500 kW | 3000 kWh |
| Major | 56 | 400 kW | 2500 kWh |
| Standard | 94 | 300 kW | 2000 kWh |
| Terminal | 15 | 500 kW | 3000 kWh |
| **Total installed** | **198** | **79,100 kW** | **509,000 kWh** |

Aggregate station-rail charging power: **60,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (405.5 km @ €3.5 M/km) | €1.42 bn |
| Elevated (29.3 km @ €18 M/km) | €527 M |
| Elevated-interchange premium (19 sites @ €20 M) | €380 M |
| **Civil subtotal** | **€2.33 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | €0.4 M | €0.8 M |
| `standard` | 94 | €1.5 M | €141 M |
| `major` | 56 | €3.0 M | €168 M |
| `terminal` | 15 | €2.5 M | €38 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 4 | €4.5 M | €18 M |
| `interchange-elevated` | 28 | €4.5 M | €126 M |
| **Stations subtotal** | | | **€494 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 15 | €3.0 M | €45 M |
| **Depots subtotal** | | | **€70 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: commodity Na-ion cells (~$80/kWh, RFC 0021), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 352 | €4.5 M | €1.58 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 436.5 km × €0.4 M/km | €174 M |
| Traction power (distributed PV + Na-ion, no OCS, RFC 0002) | 436.5 km × €0.8 M/km | €348 M |
| EPC integration + project management (7%) | on subtotal | €350 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.33 bn |
| Stations | €494 M |
| Depots | €70 M |
| Rolling stock | €1.58 bn |
| Signalling + power | €522 M |
| EPC overhead (7%) | €350 M |
| **CAPEX total** | **€5.35 bn** |
| Per-route-km | €12 M / km |
| Per-capita (city pop) | €547 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh baghdad`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €3.21 bn | 4.0% | 25 y, 5 y grace | €236 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €1.34 bn | 8.5% | 25 y, 5 y grace | €141 M / yr |
| Government equity (no debt service) | 15% | €802 M | — | — | — |
| **Total** | **100%** | **€5.35 bn** | | | **€377 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €63 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €58 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €8.7 M |
| Traction energy + station HVAC | ~6652.7 M car-km × 4 kWh × €0.10 | €2.66 bn |
| Labour (1,185 FTE) | country median × 12 × engineer-premium 1.6 | €8.0 M |
| **OPEX subtotal** | | **€2.80 bn / yr** |

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.58 (~$0.63 USD) |
| Day pass (3 trips) | €1.49 (15 % bulk discount) |
| Monthly unlimited pass | €17.48 (~5 % of median monthly income) |
| Annual pass | €192.28 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 280 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 136.9 M | 273.9 M |
| Farebox revenue | €80 M / yr | €160 M / yr |
| Farebox / OPEX recovery | 3% | 6% |
| Country target recovery | 45% | 45% |
| Operating subsidy needed | €1.18 bn / yr | €1.10 bn / yr |
| **Total annual government burden** | **€1.56 bn / yr** | **€1.48 bn / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`baghdad.toml`](baghdad.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`baghdad-network-map.png`](baghdad-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`baghdad.corridor.geojson`](baghdad.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`baghdad.stations.json`](baghdad.stations.json) | Machine-readable station list |
| [`baghdad.design-quality.yaml`](baghdad.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug baghdad

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug baghdad \
    --sidecar .cache/osr-pipeline/rasters/baghdad.grid.json \
    --out-dir designs/.../Baghdad

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../baghdad.toml \
    --out designs/.../README.md
```

`scripts/regenerate-baghdad.sh` chains steps 3 + drift tests into a single command.
