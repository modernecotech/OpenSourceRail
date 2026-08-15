# Dakar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dakar-line1.aln.toml`](dakar-line1.aln.toml) | `line-1` | 40,331.3 m | 15 |
| [`dakar-line2.aln.toml`](dakar-line2.aln.toml) | `line-2` | 30,260.0 m | 11 |
| [`dakar-line3.aln.toml`](dakar-line3.aln.toml) | `line-3` | 31,310.3 m | 12 |
| [`dakar-line4.aln.toml`](dakar-line4.aln.toml) | `line-4` | 26,397.4 m | 11 |
| [`dakar-line5.aln.toml`](dakar-line5.aln.toml) | `line-5` | 28,275.7 m | 9 |
| [`dakar-line6.aln.toml`](dakar-line6.aln.toml) | `line-6` | 65,610.4 m | 24 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
