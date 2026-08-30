# Bandung Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bandung-line1.aln.toml`](bandung-line1.aln.toml) | `line-1` | 39,563.4 m | 16 |
| [`bandung-line2.aln.toml`](bandung-line2.aln.toml) | `line-2` | 44,542.0 m | 15 |
| [`bandung-line3.aln.toml`](bandung-line3.aln.toml) | `line-3` | 23,972.9 m | 10 |
| [`bandung-line4.aln.toml`](bandung-line4.aln.toml) | `line-4` | 34,227.6 m | 14 |
| [`bandung-line5.aln.toml`](bandung-line5.aln.toml) | `line-5` | 31,516.1 m | 12 |
| [`bandung-line6.aln.toml`](bandung-line6.aln.toml) | `line-6` | 71,786.3 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
