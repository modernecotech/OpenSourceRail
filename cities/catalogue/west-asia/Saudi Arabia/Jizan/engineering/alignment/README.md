# Jizan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jizan-line1.aln.toml`](jizan-line1.aln.toml) | `line-1` | 22,743.4 m | 10 |
| [`jizan-line2.aln.toml`](jizan-line2.aln.toml) | `line-2` | 7,365.6 m | 4 |
| [`jizan-line3.aln.toml`](jizan-line3.aln.toml) | `line-3` | 19,061.2 m | 9 |
| [`jizan-line4.aln.toml`](jizan-line4.aln.toml) | `line-4` | 6,919.2 m | 2 |
| [`jizan-line5.aln.toml`](jizan-line5.aln.toml) | `line-5` | 5,246.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
