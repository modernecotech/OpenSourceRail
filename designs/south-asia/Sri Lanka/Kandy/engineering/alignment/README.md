# Kandy Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kandy-line1.aln.toml`](kandy-line1.aln.toml) | `line-1` | 27,175.8 m | 15 |
| [`kandy-line2.aln.toml`](kandy-line2.aln.toml) | `line-2` | 25,532.8 m | 14 |
| [`kandy-line3.aln.toml`](kandy-line3.aln.toml) | `line-3` | 22,668.8 m | 12 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
