# Tete Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tete-line1.aln.toml`](tete-line1.aln.toml) | `line-1` | 12,169.3 m | 5 |
| [`tete-line2.aln.toml`](tete-line2.aln.toml) | `line-2` | 11,747.6 m | 3 |
| [`tete-line3.aln.toml`](tete-line3.aln.toml) | `line-3` | 9,650.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
