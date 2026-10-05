# Gazipur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gazipur-line1.aln.toml`](gazipur-line1.aln.toml) | `line-1` | 33,117.7 m | 14 |
| [`gazipur-line2.aln.toml`](gazipur-line2.aln.toml) | `line-2` | 34,429.1 m | 13 |
| [`gazipur-line3.aln.toml`](gazipur-line3.aln.toml) | `line-3` | 46,869.6 m | 17 |
| [`gazipur-line4.aln.toml`](gazipur-line4.aln.toml) | `line-4` | 45,200.8 m | 16 |
| [`gazipur-line5.aln.toml`](gazipur-line5.aln.toml) | `line-5` | 27,832.4 m | 9 |
| [`gazipur-line6.aln.toml`](gazipur-line6.aln.toml) | `line-6` | 66,069.9 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
