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
| Unique stations | 293 |
| Interchange complexes | 19 |
| Anchor-weighted coverage | 39.3% |
| Route length (double track) | 476.2 km |
| Civil mix (at-grade / elevated) | 443.0 km / 31.6 km (7% elevated) |
| Revenue fleet | 242 × 6-car trainsets |
| Spare + cold reserve | 30 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |
| Depots | 16 |

## Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 47.9 km | 30 | 27 | عرب خيط ↔ مستشفى الدكتور قيصر |
| line-2 | 47.0 km | 30 | 27 | شارع حارث ابن كلده ↔ معهد الكوكب للتدريس الخصوصي ودورات التقوية |
| line-3 | 46.5 km | 30 | 27 | مدرسة الغصون الابتدائيه للبنات في ابو عظام ↔ مدارس أكاديمية التجمع الابتدائية و الثانوية الأهلية |
| line-4 | 47.2 km | 31 | 27 | مركز صحي الشاعورة ↔ Багдад |
| line-5 | 47.9 km | 27 | 27 | مركز صحي الباجة جي ↔ مدرسة سكينة الابتدائية للبنات /الكرخ ٢ |
| line-6 | 43.8 km | 26 | 25 | مجمع دار الشفاء الطبي ↔ line-6-0326-2070 |
| line-7 | 44.9 km | 26 | 26 | مركز صحي سبع البور الجديد ↔ line-7-1088-2164 |
| line-8 | 46.7 km | 27 | 27 | مركز صحي ↔ ثانوية ريحانة الرسول + بلقيس الابتدائية |
| line-9 | 104.3 km | 68 | 59 | اعدادية الشعلة للبنين ↔ اعدادية الشعلة للبنين |
| **Total** | **476.2 km** | **293 unique** | **272** | |

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
- **Practical daily ridership estimate** (10–15 % of 39% catchment): **294,750 – 442,125 trips/day**

## Catchment

- City population: **7,500,000**
- Anchor-weighted coverage: **39.3%** (`high_demand_coverage` metric in design-quality.yaml)
- Catchment population: ≈ **2,947,500**

## Civil cost (planning grade)

From `[costs]` in `design.toml` — €/km × civil-mix lengths per RFC 0011 §9. Excludes rolling stock, stations, depots, and integration.

| Bucket | Value |
|---|---|
| At-grade (443.0 km) | €1.55 bn |
| Elevated (31.6 km) | €568 M |
| Elevated-interchange premium (19 sites) | €360 M |
| **Civil total** | **€2.48 bn** |

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
    --out-dir designs/west-asia/Iraq/designs/west-asia/Iraq/Baghdad

# 3. network map PNG
python -m osr_scenario.render_map --design designs/west-asia/Iraq/designs/west-asia/Iraq/Baghdad/design.toml
```
