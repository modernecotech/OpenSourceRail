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
| Unique stations | 38 |
| Interchange complexes | 2 |
| Anchor-weighted coverage | 55.0% |
| Route length (double track) | 39.0 km |
| Civil mix (at-grade / elevated) | 36.1 km / 2.7 km (7% elevated) |
| Revenue fleet | 21 × 2-car trainsets |
| Spare + cold reserve | 6 × 2-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |
| Depots | 6 |

## Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 11.5 km | 13 | 8 | مستشفى الالماني ↔ ال مطشر |
| line-2 | 15.2 km | 13 | 10 | كشته ↔ مدرسة الوهج الابتدائية المختلطة  |
| line-3 | 12.3 km | 12 | 9 | مستوصف صحي حي العسكري ↔ جامعة الامام جعفر الصادق فرع المثنى |
| **Total** | **39.0 km** | **38 unique** | **27** | |

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

- City population: **280,000**
- Anchor-weighted coverage: **55.0%** (`high_demand_coverage` metric in design-quality.yaml)
- Catchment population: ≈ **154,000**

## Civil cost (planning grade)

From `[costs]` in `design.toml` — €/km × civil-mix lengths per RFC 0011 §9. Excludes rolling stock, stations, depots, and integration.

| Bucket | Value |
|---|---|
| At-grade (36.1 km) | €126 M |
| Elevated (2.7 km) | €48 M |
| Elevated-interchange premium (2 sites) | €40 M |
| **Civil total** | **€215 M** |

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
    --out-dir designs/west-asia/Iraq/designs/west-asia/Iraq/Samawah

# 3. network map PNG
python -m osr_scenario.render_map --design designs/west-asia/Iraq/designs/west-asia/Iraq/Samawah/design.toml
```
