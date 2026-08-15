# Vijayawada Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`vijayawada-line1.aln.toml`](vijayawada-line1.aln.toml) | `line-1` | 33,077.1 m | 19 |
| [`vijayawada-line2.aln.toml`](vijayawada-line2.aln.toml) | `line-2` | 28,792.2 m | 16 |
| [`vijayawada-line3.aln.toml`](vijayawada-line3.aln.toml) | `line-3` | 43,419.0 m | 22 |
| [`vijayawada-line4.aln.toml`](vijayawada-line4.aln.toml) | `line-4` | 25,004.7 m | 12 |
| [`vijayawada-line5.aln.toml`](vijayawada-line5.aln.toml) | `line-5` | 23,296.2 m | 12 |
| [`vijayawada-line6.aln.toml`](vijayawada-line6.aln.toml) | `line-6` | 74,677.1 m | 38 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
