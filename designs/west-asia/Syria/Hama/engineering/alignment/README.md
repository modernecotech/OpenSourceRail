# Hama Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hama-line1.aln.toml`](hama-line1.aln.toml) | `line-1` | 20,922.8 m | 8 |
| [`hama-line2.aln.toml`](hama-line2.aln.toml) | `line-2` | 11,524.4 m | 6 |
| [`hama-line3.aln.toml`](hama-line3.aln.toml) | `line-3` | 18,997.8 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
