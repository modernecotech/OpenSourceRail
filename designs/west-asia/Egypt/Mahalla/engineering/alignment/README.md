# Mahalla Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mahalla-line1.aln.toml`](mahalla-line1.aln.toml) | `line-1` | 12,268.6 m | 8 |
| [`mahalla-line2.aln.toml`](mahalla-line2.aln.toml) | `line-2` | 18,641.7 m | 9 |
| [`mahalla-line3.aln.toml`](mahalla-line3.aln.toml) | `line-3` | 7,372.9 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
