# Douala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`douala-line1.aln.toml`](douala-line1.aln.toml) | `line-1` | 37,851.9 m | 29 |
| [`douala-line2.aln.toml`](douala-line2.aln.toml) | `line-2` | 42,911.2 m | 22 |
| [`douala-line3.aln.toml`](douala-line3.aln.toml) | `line-3` | 44,950.8 m | 25 |
| [`douala-line4.aln.toml`](douala-line4.aln.toml) | `line-4` | 29,037.3 m | 18 |
| [`douala-line5.aln.toml`](douala-line5.aln.toml) | `line-5` | 52,791.2 m | 39 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
