# Comilla Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`comilla-line1.aln.toml`](comilla-line1.aln.toml) | `line-1` | 20,123.3 m | 13 |
| [`comilla-line2.aln.toml`](comilla-line2.aln.toml) | `line-2` | 20,341.5 m | 12 |
| [`comilla-line3.aln.toml`](comilla-line3.aln.toml) | `line-3` | 15,053.6 m | 10 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
