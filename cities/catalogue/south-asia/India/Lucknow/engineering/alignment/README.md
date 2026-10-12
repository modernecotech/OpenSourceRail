# Lucknow Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lucknow-line1.aln.toml`](lucknow-line1.aln.toml) | `line-1` | 52,577.4 m | 18 |
| [`lucknow-line2.aln.toml`](lucknow-line2.aln.toml) | `line-2` | 26,591.8 m | 10 |
| [`lucknow-line3.aln.toml`](lucknow-line3.aln.toml) | `line-3` | 21,751.1 m | 9 |
| [`lucknow-line4.aln.toml`](lucknow-line4.aln.toml) | `line-4` | 23,228.0 m | 8 |
| [`lucknow-line5.aln.toml`](lucknow-line5.aln.toml) | `line-5` | 51,218.0 m | 15 |
| [`lucknow-line6.aln.toml`](lucknow-line6.aln.toml) | `line-6` | 43,378.8 m | 14 |
| [`lucknow-line7.aln.toml`](lucknow-line7.aln.toml) | `line-7` | 41,414.2 m | 12 |
| [`lucknow-line8.aln.toml`](lucknow-line8.aln.toml) | `line-8` | 100,093.6 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
