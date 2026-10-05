# Douala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`douala-line1.aln.toml`](douala-line1.aln.toml) | `line-1` | 35,711.8 m | 13 |
| [`douala-line2.aln.toml`](douala-line2.aln.toml) | `line-2` | 39,851.3 m | 15 |
| [`douala-line3.aln.toml`](douala-line3.aln.toml) | `line-3` | 25,449.2 m | 9 |
| [`douala-line4.aln.toml`](douala-line4.aln.toml) | `line-4` | 48,532.0 m | 15 |
| [`douala-line5.aln.toml`](douala-line5.aln.toml) | `line-5` | 43,893.8 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
