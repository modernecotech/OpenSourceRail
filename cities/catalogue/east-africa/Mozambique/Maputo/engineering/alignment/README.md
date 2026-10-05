# Maputo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maputo-line1.aln.toml`](maputo-line1.aln.toml) | `line-1` | 21,914.0 m | 13 |
| [`maputo-line2.aln.toml`](maputo-line2.aln.toml) | `line-2` | 19,740.7 m | 9 |
| [`maputo-line3.aln.toml`](maputo-line3.aln.toml) | `line-3` | 18,516.9 m | 10 |
| [`maputo-line4.aln.toml`](maputo-line4.aln.toml) | `line-4` | 27,944.0 m | 9 |
| [`maputo-line5.aln.toml`](maputo-line5.aln.toml) | `line-5` | 18,112.0 m | 9 |
| [`maputo-line6.aln.toml`](maputo-line6.aln.toml) | `line-6` | 54,142.1 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
