# Mandalay Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mandalay-line1.aln.toml`](mandalay-line1.aln.toml) | `line-1` | 43,875.8 m | 23 |
| [`mandalay-line2.aln.toml`](mandalay-line2.aln.toml) | `line-2` | 32,265.1 m | 16 |
| [`mandalay-line3.aln.toml`](mandalay-line3.aln.toml) | `line-3` | 31,964.0 m | 18 |
| [`mandalay-line4.aln.toml`](mandalay-line4.aln.toml) | `line-4` | 25,810.7 m | 13 |
| [`mandalay-line5.aln.toml`](mandalay-line5.aln.toml) | `line-5` | 27,266.7 m | 17 |
| [`mandalay-line6.aln.toml`](mandalay-line6.aln.toml) | `line-6` | 60,730.8 m | 34 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
