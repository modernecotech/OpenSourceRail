# Indore Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`indore-line1.aln.toml`](indore-line1.aln.toml) | `line-1` | 42,154.1 m | 13 |
| [`indore-line2.aln.toml`](indore-line2.aln.toml) | `line-2` | 43,268.0 m | 23 |
| [`indore-line3.aln.toml`](indore-line3.aln.toml) | `line-3` | 35,539.5 m | 10 |
| [`indore-line4.aln.toml`](indore-line4.aln.toml) | `line-4` | 46,495.0 m | 26 |
| [`indore-line5.aln.toml`](indore-line5.aln.toml) | `line-5` | 45,728.7 m | 14 |
| [`indore-line6.aln.toml`](indore-line6.aln.toml) | `line-6` | 29,160.5 m | 10 |
| [`indore-line7.aln.toml`](indore-line7.aln.toml) | `line-7` | 35,790.0 m | 12 |
| [`indore-line8.aln.toml`](indore-line8.aln.toml) | `line-8` | 82,769.5 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
