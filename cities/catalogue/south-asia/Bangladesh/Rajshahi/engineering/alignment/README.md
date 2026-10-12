# Rajshahi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rajshahi-line1.aln.toml`](rajshahi-line1.aln.toml) | `line-1` | 19,352.0 m | 23 |
| [`rajshahi-line2.aln.toml`](rajshahi-line2.aln.toml) | `line-2` | 5,435.0 m | 3 |
| [`rajshahi-line3.aln.toml`](rajshahi-line3.aln.toml) | `line-3` | 14,157.7 m | 22 |
| [`rajshahi-line4.aln.toml`](rajshahi-line4.aln.toml) | `line-4` | 5,801.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
