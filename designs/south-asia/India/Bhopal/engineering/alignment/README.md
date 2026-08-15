# Bhopal Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bhopal-line1.aln.toml`](bhopal-line1.aln.toml) | `line-1` | 25,943.5 m | 13 |
| [`bhopal-line2.aln.toml`](bhopal-line2.aln.toml) | `line-2` | 25,335.4 m | 11 |
| [`bhopal-line3.aln.toml`](bhopal-line3.aln.toml) | `line-3` | 22,018.4 m | 8 |
| [`bhopal-line4.aln.toml`](bhopal-line4.aln.toml) | `line-4` | 35,847.3 m | 13 |
| [`bhopal-line5.aln.toml`](bhopal-line5.aln.toml) | `line-5` | 26,130.6 m | 7 |
| [`bhopal-line6.aln.toml`](bhopal-line6.aln.toml) | `line-6` | 59,355.7 m | 20 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
