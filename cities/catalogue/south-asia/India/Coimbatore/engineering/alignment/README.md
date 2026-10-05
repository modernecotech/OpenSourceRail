# Coimbatore Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`coimbatore-line1.aln.toml`](coimbatore-line1.aln.toml) | `line-1` | 41,550.9 m | 14 |
| [`coimbatore-line2.aln.toml`](coimbatore-line2.aln.toml) | `line-2` | 23,792.8 m | 9 |
| [`coimbatore-line3.aln.toml`](coimbatore-line3.aln.toml) | `line-3` | 26,387.9 m | 9 |
| [`coimbatore-line4.aln.toml`](coimbatore-line4.aln.toml) | `line-4` | 28,676.1 m | 8 |
| [`coimbatore-line5.aln.toml`](coimbatore-line5.aln.toml) | `line-5` | 26,417.3 m | 8 |
| [`coimbatore-line6.aln.toml`](coimbatore-line6.aln.toml) | `line-6` | 30,832.4 m | 9 |
| [`coimbatore-line7.aln.toml`](coimbatore-line7.aln.toml) | `line-7` | 19,919.5 m | 8 |
| [`coimbatore-line8.aln.toml`](coimbatore-line8.aln.toml) | `line-8` | 26,840.8 m | 8 |
| [`coimbatore-line9.aln.toml`](coimbatore-line9.aln.toml) | `line-9` | 70,835.6 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
