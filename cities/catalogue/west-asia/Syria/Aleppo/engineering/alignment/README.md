# Aleppo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`aleppo-line1.aln.toml`](aleppo-line1.aln.toml) | `line-1` | 23,762.7 m | 11 |
| [`aleppo-line2.aln.toml`](aleppo-line2.aln.toml) | `line-2` | 24,243.6 m | 10 |
| [`aleppo-line3.aln.toml`](aleppo-line3.aln.toml) | `line-3` | 13,281.0 m | 7 |
| [`aleppo-line4.aln.toml`](aleppo-line4.aln.toml) | `line-4` | 20,685.3 m | 9 |
| [`aleppo-line5.aln.toml`](aleppo-line5.aln.toml) | `line-5` | 23,850.6 m | 9 |
| [`aleppo-line6.aln.toml`](aleppo-line6.aln.toml) | `line-6` | 54,397.3 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
