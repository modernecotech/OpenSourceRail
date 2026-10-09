# Lichinga Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lichinga-line1.aln.toml`](lichinga-line1.aln.toml) | `line-1` | 4,316.6 m | 3 |
| [`lichinga-line2.aln.toml`](lichinga-line2.aln.toml) | `line-2` | 2,825.3 m | 3 |
| [`lichinga-line3.aln.toml`](lichinga-line3.aln.toml) | `line-3` | 4,297.9 m | 3 |
| [`lichinga-line4.aln.toml`](lichinga-line4.aln.toml) | `line-4` | 2,086.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
