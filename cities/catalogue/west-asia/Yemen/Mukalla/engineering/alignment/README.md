# Mukalla Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mukalla-line1.aln.toml`](mukalla-line1.aln.toml) | `line-1` | 19,191.9 m | 8 |
| [`mukalla-line2.aln.toml`](mukalla-line2.aln.toml) | `line-2` | 16,453.5 m | 5 |
| [`mukalla-line3.aln.toml`](mukalla-line3.aln.toml) | `line-3` | 25,965.1 m | 9 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
