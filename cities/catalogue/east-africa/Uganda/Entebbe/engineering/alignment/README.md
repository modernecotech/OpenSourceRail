# Entebbe Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`entebbe-line1.aln.toml`](entebbe-line1.aln.toml) | `line-1` | 12,593.7 m | 5 |
| [`entebbe-line2.aln.toml`](entebbe-line2.aln.toml) | `line-2` | 4,505.7 m | 3 |
| [`entebbe-line3.aln.toml`](entebbe-line3.aln.toml) | `line-3` | 13,813.6 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
