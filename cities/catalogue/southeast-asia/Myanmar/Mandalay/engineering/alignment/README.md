# Mandalay Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mandalay-line1.aln.toml`](mandalay-line1.aln.toml) | `line-1` | 38,333.2 m | 12 |
| [`mandalay-line2.aln.toml`](mandalay-line2.aln.toml) | `line-2` | 30,612.8 m | 13 |
| [`mandalay-line3.aln.toml`](mandalay-line3.aln.toml) | `line-3` | 30,188.2 m | 9 |
| [`mandalay-line4.aln.toml`](mandalay-line4.aln.toml) | `line-4` | 21,760.1 m | 8 |
| [`mandalay-line5.aln.toml`](mandalay-line5.aln.toml) | `line-5` | 23,366.3 m | 8 |
| [`mandalay-line6.aln.toml`](mandalay-line6.aln.toml) | `line-6` | 84,921.0 m | 21 |
| [`mandalay-line7.aln.toml`](mandalay-line7.aln.toml) | `line-7` | 6,239.9 m | 2 |
| [`mandalay-line8.aln.toml`](mandalay-line8.aln.toml) | `line-8` | 5,651.0 m | 2 |
| [`mandalay-line9.aln.toml`](mandalay-line9.aln.toml) | `line-9` | 13,599.7 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
