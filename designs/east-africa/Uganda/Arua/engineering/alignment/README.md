# Arua Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`arua-line1.aln.toml`](arua-line1.aln.toml) | `line-1` | 9,896.5 m | 7 |
| [`arua-line2.aln.toml`](arua-line2.aln.toml) | `line-2` | 15,010.2 m | 10 |
| [`arua-line3.aln.toml`](arua-line3.aln.toml) | `line-3` | 12,824.0 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
