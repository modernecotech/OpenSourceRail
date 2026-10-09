# Lucknow Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lucknow-line1.aln.toml`](lucknow-line1.aln.toml) | `line-1` | 44,352.8 m | 14 |
| [`lucknow-line2.aln.toml`](lucknow-line2.aln.toml) | `line-2` | 26,866.3 m | 14 |
| [`lucknow-line3.aln.toml`](lucknow-line3.aln.toml) | `line-3` | 22,207.7 m | 9 |
| [`lucknow-line4.aln.toml`](lucknow-line4.aln.toml) | `line-4` | 17,298.8 m | 8 |
| [`lucknow-line5.aln.toml`](lucknow-line5.aln.toml) | `line-5` | 51,218.0 m | 16 |
| [`lucknow-line6.aln.toml`](lucknow-line6.aln.toml) | `line-6` | 43,378.8 m | 15 |
| [`lucknow-line7.aln.toml`](lucknow-line7.aln.toml) | `line-7` | 37,172.3 m | 13 |
| [`lucknow-line8.aln.toml`](lucknow-line8.aln.toml) | `line-8` | 86,160.7 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
