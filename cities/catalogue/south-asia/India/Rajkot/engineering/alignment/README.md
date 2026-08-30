# Rajkot Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rajkot-line1.aln.toml`](rajkot-line1.aln.toml) | `line-1` | 25,394.4 m | 10 |
| [`rajkot-line2.aln.toml`](rajkot-line2.aln.toml) | `line-2` | 14,517.4 m | 7 |
| [`rajkot-line3.aln.toml`](rajkot-line3.aln.toml) | `line-3` | 14,835.1 m | 6 |
| [`rajkot-line4.aln.toml`](rajkot-line4.aln.toml) | `line-4` | 23,709.1 m | 8 |
| [`rajkot-line5.aln.toml`](rajkot-line5.aln.toml) | `line-5` | 55,407.1 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
