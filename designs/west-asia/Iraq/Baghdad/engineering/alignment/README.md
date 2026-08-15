# Baghdad Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`baghdad-line1.aln.toml`](baghdad-line1.aln.toml) | `line-1` | 58,109.9 m | 30 |
| [`baghdad-line2.aln.toml`](baghdad-line2.aln.toml) | `line-2` | 45,806.3 m | 23 |
| [`baghdad-line3.aln.toml`](baghdad-line3.aln.toml) | `line-3` | 55,088.0 m | 29 |
| [`baghdad-line4.aln.toml`](baghdad-line4.aln.toml) | `line-4` | 52,919.5 m | 28 |
| [`baghdad-line5.aln.toml`](baghdad-line5.aln.toml) | `line-5` | 43,123.5 m | 23 |
| [`baghdad-line6.aln.toml`](baghdad-line6.aln.toml) | `line-6` | 47,231.7 m | 24 |
| [`baghdad-line7.aln.toml`](baghdad-line7.aln.toml) | `line-7` | 56,905.2 m | 29 |
| [`baghdad-line8.aln.toml`](baghdad-line8.aln.toml) | `line-8` | 36,358.5 m | 17 |
| [`baghdad-line9.aln.toml`](baghdad-line9.aln.toml) | `line-9` | 105,707.8 m | 58 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
