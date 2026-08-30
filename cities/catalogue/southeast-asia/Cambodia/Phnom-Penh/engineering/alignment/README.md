# Phnom-Penh Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`phnom-penh-line1.aln.toml`](phnom-penh-line1.aln.toml) | `line-1` | 30,282.0 m | 10 |
| [`phnom-penh-line2.aln.toml`](phnom-penh-line2.aln.toml) | `line-2` | 29,076.6 m | 11 |
| [`phnom-penh-line3.aln.toml`](phnom-penh-line3.aln.toml) | `line-3` | 41,534.0 m | 14 |
| [`phnom-penh-line4.aln.toml`](phnom-penh-line4.aln.toml) | `line-4` | 33,216.3 m | 13 |
| [`phnom-penh-line5.aln.toml`](phnom-penh-line5.aln.toml) | `line-5` | 33,516.2 m | 13 |
| [`phnom-penh-line6.aln.toml`](phnom-penh-line6.aln.toml) | `line-6` | 70,775.8 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
