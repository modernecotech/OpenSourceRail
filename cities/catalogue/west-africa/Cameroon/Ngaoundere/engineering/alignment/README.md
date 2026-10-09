# Ngaoundere Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ngaoundere-line1.aln.toml`](ngaoundere-line1.aln.toml) | `line-1` | 8,167.9 m | 6 |
| [`ngaoundere-line2.aln.toml`](ngaoundere-line2.aln.toml) | `line-2` | 6,725.2 m | 5 |
| [`ngaoundere-line3.aln.toml`](ngaoundere-line3.aln.toml) | `line-3` | 6,145.2 m | 5 |
| [`ngaoundere-line4.aln.toml`](ngaoundere-line4.aln.toml) | `line-4` | 3,293.6 m | 3 |
| [`ngaoundere-line5.aln.toml`](ngaoundere-line5.aln.toml) | `line-5` | 4,707.6 m | 3 |
| [`ngaoundere-line6.aln.toml`](ngaoundere-line6.aln.toml) | `line-6` | 5,763.8 m | 4 |
| [`ngaoundere-line7.aln.toml`](ngaoundere-line7.aln.toml) | `line-7` | 6,436.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
