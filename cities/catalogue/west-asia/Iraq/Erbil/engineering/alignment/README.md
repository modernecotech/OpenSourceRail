# Erbil Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`erbil-line1.aln.toml`](erbil-line1.aln.toml) | `line-1` | 28,706.7 m | 10 |
| [`erbil-line2.aln.toml`](erbil-line2.aln.toml) | `line-2` | 29,912.5 m | 9 |
| [`erbil-line3.aln.toml`](erbil-line3.aln.toml) | `line-3` | 19,203.0 m | 6 |
| [`erbil-line4.aln.toml`](erbil-line4.aln.toml) | `line-4` | 23,734.2 m | 9 |
| [`erbil-line5.aln.toml`](erbil-line5.aln.toml) | `line-5` | 17,619.9 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
