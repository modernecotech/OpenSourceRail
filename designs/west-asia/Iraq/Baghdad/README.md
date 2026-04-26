# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 7,500,000

Auto-planned by the OSR pipeline (`osr_geo` rasters → `osr-design` greedy synthesizer) on Overpass-verified OpenStreetMap data. Every station sits on an aggregated POI cluster; every line follows the OSM road graph (trunk / primary / secondary / tertiary).

## Network map

![Baghdad rail network](baghdad-network-map.png)

*Auto-fit zoom over the network bounding box. Lines are coloured per the osr_scenario palette; interchanges show line transfers.*

Corridor polylines + stations as GeoJSON for GIS tooling: [`baghdad.corridor.geojson`](baghdad.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 286 |
| Interchange complexes | 19 |
| Anchor-weighted coverage | 37.0% |
| Route length (double track) | 470.2 km |
| Civil mix (at-grade / elevated) | 437.9 km / 30.7 km (6% elevated) |
| Revenue fleet | 340 × 6-car trainsets |
| Spare + cold reserve | 39 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |
| Depots | 16 |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 47.9 km | 30 | 39 | E Mid ↔ W Outer |
| line-2 | 47.0 km | 28 | 38 | N Outer ↔ S Mid |
| line-3 | 46.5 km | 29 | 38 | SE Mid ↔ NW Mid |
| line-4 | 47.3 km | 30 | 38 | SW Mid ↔ NE Outer |
| line-5 | 47.9 km | 27 | 39 | NW Outer ↔ SW Mid |
| line-6 | 43.9 km | 26 | 36 | S Mid ↔ NE Outer |
| line-7 | 44.9 km | 26 | 37 | NW Outer ↔ E Mid |
| line-8 | 39.1 km | 22 | 32 | E Outer ↔ SW Mid |
| line-9 | 105.7 km | 70 | 82 | W Mid loop |
| **Total** | **470.2 km** | **286 unique** | **379** | |

## Rolling stock

| Property | Value |
|---|---|
| Family | `metro-6car` |
| Consist | 6-car, 132 m |
| Max speed | 100 km/h |
| Onboard battery | 1800 kWh per trainset |
| Nominal capacity | 900 pax (seated + standing) |

## Ridership capacity

- **Per-train capacity:** 900 passengers
- **Peak frequency:** 12 trains/h/direction (5-min headway)
- **Peak capacity per line per direction:** 900 × 12 = **10,800 pphpd**
- **Network peak throughput** (all lines, both directions): 10,800 × 9 × 2 = **194,400 passengers/hour**
- **Daily theoretical capacity** (peak ≈ 10 % of daily): ≈ **1,944,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of 37% catchment): **277,500 – 416,250 trips/day**

## Catchment

- City population: **7,500,000** (within bbox of 3,162 km², gross density ≈ 2,372/km²)
- Stations: **286** at 800 m walking radius ⇒ raw walkshed = 575 km²; overlap-discounted (30 %) = **403 km²**
- Walkshed catchment population (gross density × walkshed): ≈ **954,731**
- Anchor-weighted demand coverage: **37.0%** — share of OSM POI demand-weight reachable within the walkshed (`high_demand_coverage` metric in design-quality.yaml). Cross-check on the walkshed estimate: 37.0% of 7,500,000 = **2,775,000** demand-weighted catchment.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Base OECD rates; `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (437.9 km @ €3.5 M/km) | €1.53 bn |
| Elevated (30.7 km @ €18 M/km) | €552 M |
| Elevated-interchange premium (19 sites @ €20 M) | €360 M |
| **Civil subtotal** | **€2.44 bn** |

### Stations

At-grade construction per RFC 0010 archetype catalogue. Vertical circulation + canopy PV included.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 8 | €1.5 M | €12 M |
| `standard` | 131 | €8 M | €1.05 bn |
| `major` | 75 | €12 M | €900 M |
| `terminal` | 15 | €10 M | €150 M |
| `depot-terminal` | 1 | €12 M | €12 M |
| `interchange` | 2 | €18 M | €36 M |
| **Stations subtotal** | | | **€2.61 bn** |

### Depots

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €150 M | €150 M |
| `layup-minimal` | 15 | €15 M | €225 M |
| **Depots subtotal** | | | **€375 M** |

### Rolling stock

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 379 | €18 M | €6.82 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling / CBTC (RFC 0015 GoA 4) | 470.2 km × €1.5 M/km | €703 M |
| Traction power (battery-electric, no OCS) | 470.2 km × €0.8 M/km | €375 M |
| EPC integration + project management (10%) | on subtotal | €1.33 bn |

### Total

| Bucket | Value |
|---|---|
| Civil works | €2.44 bn |
| Stations | €2.61 bn |
| Depots | €375 M |
| Rolling stock | €6.82 bn |
| Signalling + power | €1.08 bn |
| EPC overhead (10%) | €1.33 bn |
| **CAPEX total** | **€14.66 bn** |
| Per-route-km | €31 M / km |
| Per-capita (city pop) | €1,954 / person |

## Quality gates

From `design-quality.yaml` — used by the planner's auto-gate to accept/reject a candidate design.

| Gate | Result |
|---|---|
| (hard) `has_stations` | ✅ |
| (hard) `length_reasonable` | ✅ |
| (soft) `coverage_ge_0.30` | ✅ |
| (soft) `anchor_hit_ge_0.20` | ✅ |
| (soft) `elevated_le_0.30` | ✅ |
| (soft) `soft_pass_all` | ✅ |
| **Pass overall** | **✅** |

## Files in this folder

- `design.toml` — authoritative city design (lines, stations, depots, junctions, costs)
- `baghdad.corridor.geojson` — line polylines + station points for GIS tooling
- `baghdad.stations.json` — machine-readable station list
- `baghdad.design-quality.yaml` — coverage / anchor-hit / civil-mix metrics + auto-gate result
- `baghdad-network-map.png` — rendered OSM-backed map
- `diagnose.png` — per-line diagnostic plot
- `corridors.json` — cached greedy-planner output (skip-routing cache)

## Reproducibility

```
# 1. raster bundle from OSM
python -m osr_geo.cli --slug baghdad --bbox <S> <W> <N> <E>

# 2. design synthesis
cargo run --release --bin osr-design -- \
    --slug baghdad --population 7500000 --country IQ \
    --sidecar .cache/osr-pipeline/rasters/baghdad.grid.json \
    --out-dir designs/west-asia/Iraq/Baghdad

# 3. network map PNG
python -m osr_scenario.render_map --design designs/west-asia/Iraq/Baghdad/design.toml
```
