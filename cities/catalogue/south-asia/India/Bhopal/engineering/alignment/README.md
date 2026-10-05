# Bhopal Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bhopal-line1.aln.toml`](bhopal-line1.aln.toml) | `line-1` | 20,632.1 m | 8 |
| [`bhopal-line2.aln.toml`](bhopal-line2.aln.toml) | `line-2` | 18,022.0 m | 8 |
| [`bhopal-line3.aln.toml`](bhopal-line3.aln.toml) | `line-3` | 17,496.9 m | 7 |
| [`bhopal-line4.aln.toml`](bhopal-line4.aln.toml) | `line-4` | 30,604.1 m | 10 |
| [`bhopal-line5.aln.toml`](bhopal-line5.aln.toml) | `line-5` | 23,137.5 m | 7 |
| [`bhopal-line6.aln.toml`](bhopal-line6.aln.toml) | `line-6` | 53,226.9 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
