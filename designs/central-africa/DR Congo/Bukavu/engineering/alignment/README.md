# Bukavu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bukavu-line1.aln.toml`](bukavu-line1.aln.toml) | `line-1` | 18,280.9 m | 12 |
| [`bukavu-line2.aln.toml`](bukavu-line2.aln.toml) | `line-2` | 23,646.1 m | 14 |
| [`bukavu-line3.aln.toml`](bukavu-line3.aln.toml) | `line-3` | 19,448.4 m | 11 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
