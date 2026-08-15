# Hebron Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hebron-line1.aln.toml`](hebron-line1.aln.toml) | `line-1` | 19,498.3 m | 12 |
| [`hebron-line2.aln.toml`](hebron-line2.aln.toml) | `line-2` | 17,472.4 m | 11 |
| [`hebron-line3.aln.toml`](hebron-line3.aln.toml) | `line-3` | 23,341.6 m | 13 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
