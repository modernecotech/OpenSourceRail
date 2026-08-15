# Kigoma Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kigoma-line1.aln.toml`](kigoma-line1.aln.toml) | `line-1` | 12,324.5 m | 6 |
| [`kigoma-line2.aln.toml`](kigoma-line2.aln.toml) | `line-2` | 14,733.7 m | 6 |
| [`kigoma-line3.aln.toml`](kigoma-line3.aln.toml) | `line-3` | 8,868.6 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
