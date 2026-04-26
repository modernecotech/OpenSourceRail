# Samawah — Urban Rail Network

**Country:** IQ · **Population:** 280,000

Auto-planned by the OSR pipeline (`osr_geo` rasters → `osr-design` greedy synthesizer) on Overpass-verified OpenStreetMap data. Every station sits on an aggregated POI cluster; every line follows the OSM road graph (trunk / primary / secondary / tertiary).

## Network map

![Samawah rail network](samawah-network-map.png)

*Auto-fit zoom over the network bounding box. Lines are coloured per the osr_scenario palette; interchanges show line transfers.*

Corridor polylines + stations as GeoJSON for GIS tooling: [`samawah.corridor.geojson`](samawah.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 40 |
| Interchange complexes | 2 |
| Anchor-weighted coverage | 55.0% |
| Route length (double track) | 39.0 km |
| Civil mix (at-grade / elevated) | 36.1 km / 2.7 km (7% elevated) |
| Revenue fleet | 47 × 2-car trainsets |
| Spare + cold reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |
| Depots | 6 |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 11.5 km | 14 | 16 | SE Mid ↔ N Outer |
| line-2 | 15.2 km | 13 | 20 | W Outer ↔ E Outer |
| line-3 | 12.3 km | 13 | 17 | N Outer ↔ SW Mid |
| **Total** | **39.0 km** | **40 unique** | **53** | |

## Rolling stock

| Property | Value |
|---|---|
| Family | `tram-2car` |
| Consist | 2-car, 42 m |
| Max speed | 70 km/h |
| Onboard battery | 450 kWh per trainset |
| Nominal capacity | 220 pax (seated + standing) |

## Ridership capacity

- **Per-train capacity:** 220 passengers
- **Peak frequency:** 12 trains/h/direction (5-min headway)
- **Peak capacity per line per direction:** 220 × 12 = **2,640 pphpd**
- **Network peak throughput** (all lines, both directions): 2,640 × 3 × 2 = **15,840 passengers/hour**
- **Daily theoretical capacity** (peak ≈ 10 % of daily): ≈ **158,400 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of 55% catchment): **15,400 – 23,100 trips/day**

## Catchment

- City population: **280,000** (within bbox of 165 km², gross density ≈ 1,701/km²)
- Stations: **40** at 800 m walking radius ⇒ raw walkshed = 80 km²; overlap-discounted (30 %) = **56 km²**
- Walkshed catchment population (gross density × walkshed): ≈ **95,783**
- Anchor-weighted demand coverage: **55.0%** — share of OSM POI demand-weight reachable within the walkshed (`high_demand_coverage` metric in design-quality.yaml). Cross-check on the walkshed estimate: 55.0% of 280,000 = **154,000** demand-weighted catchment.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. Base OECD rates; `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (36.1 km @ €3.5 M/km) | €126 M |
| Elevated (2.7 km @ €18 M/km) | €48 M |
| Elevated-interchange premium (2 sites @ €20 M) | €40 M |
| **Civil subtotal** | **€215 M** |

### Stations

At-grade construction per RFC 0010 archetype catalogue. Vertical circulation + canopy PV included.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | €1.5 M | €3 M |
| `standard` | 12 | €8 M | €96 M |
| `major` | 14 | €12 M | €168 M |
| `terminal` | 5 | €10 M | €50 M |
| `depot-terminal` | 1 | €12 M | €12 M |
| **Stations subtotal** | | | **€377 M** |

### Depots

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €150 M | €150 M |
| `layup-minimal` | 5 | €15 M | €75 M |
| **Depots subtotal** | | | **€225 M** |

### Rolling stock

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `tram-2car` (revenue + spare + cold reserve) | 53 | €4 M | €212 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling / CBTC (RFC 0015 GoA 4) | 39.0 km × €1.5 M/km | €58 M |
| Traction power (battery-electric, no OCS) | 39.0 km × €0.8 M/km | €31 M |
| EPC integration + project management (10%) | on subtotal | €112 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €215 M |
| Stations | €377 M |
| Depots | €225 M |
| Rolling stock | €212 M |
| Signalling + power | €89 M |
| EPC overhead (10%) | €112 M |
| **CAPEX total** | **€1.23 bn** |
| Per-route-km | €32 M / km |
| Per-capita (city pop) | €4,392 / person |

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
- `samawah.corridor.geojson` — line polylines + station points for GIS tooling
- `samawah.stations.json` — machine-readable station list
- `samawah.design-quality.yaml` — coverage / anchor-hit / civil-mix metrics + auto-gate result
- `samawah-network-map.png` — rendered OSM-backed map
- `diagnose.png` — per-line diagnostic plot
- `corridors.json` — cached greedy-planner output (skip-routing cache)

## Reproducibility

```
# 1. raster bundle from OSM
python -m osr_geo.cli --slug samawah --bbox <S> <W> <N> <E>

# 2. design synthesis
cargo run --release --bin osr-design -- \
    --slug samawah --population 280000 --country IQ \
    --sidecar .cache/osr-pipeline/rasters/samawah.grid.json \
    --out-dir designs/west-asia/Iraq/Samawah

# 3. network map PNG
python -m osr_scenario.render_map --design designs/west-asia/Iraq/Samawah/design.toml
```
