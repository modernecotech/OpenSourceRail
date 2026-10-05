# Mandalay Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mandalay-line1.aln.toml`](mandalay-line1.aln.toml) | `line-1` | 38,333.2 m | 14 |
| [`mandalay-line2.aln.toml`](mandalay-line2.aln.toml) | `line-2` | 30,801.1 m | 12 |
| [`mandalay-line3.aln.toml`](mandalay-line3.aln.toml) | `line-3` | 33,776.6 m | 11 |
| [`mandalay-line4.aln.toml`](mandalay-line4.aln.toml) | `line-4` | 21,760.1 m | 9 |
| [`mandalay-line5.aln.toml`](mandalay-line5.aln.toml) | `line-5` | 23,366.3 m | 8 |
| [`mandalay-line6.aln.toml`](mandalay-line6.aln.toml) | `line-6` | 84,977.6 m | 24 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
