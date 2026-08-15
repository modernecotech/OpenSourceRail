# Ramadi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ramadi-line1.aln.toml`](ramadi-line1.aln.toml) | `line-1` | 16,406.1 m | 7 |
| [`ramadi-line2.aln.toml`](ramadi-line2.aln.toml) | `line-2` | 14,321.4 m | 7 |
| [`ramadi-line3.aln.toml`](ramadi-line3.aln.toml) | `line-3` | 17,279.8 m | 8 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
