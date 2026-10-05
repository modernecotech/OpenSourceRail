# Kumba Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kumba-line1.aln.toml`](kumba-line1.aln.toml) | `line-1` | 16,646.3 m | 6 |
| [`kumba-line2.aln.toml`](kumba-line2.aln.toml) | `line-2` | 11,017.8 m | 5 |
| [`kumba-line3.aln.toml`](kumba-line3.aln.toml) | `line-3` | 8,138.0 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
