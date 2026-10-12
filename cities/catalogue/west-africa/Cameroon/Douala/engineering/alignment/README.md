# Douala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`douala-line1.aln.toml`](douala-line1.aln.toml) | `line-1` | 35,711.8 m | 13 |
| [`douala-line2.aln.toml`](douala-line2.aln.toml) | `line-2` | 44,959.3 m | 16 |
| [`douala-line3.aln.toml`](douala-line3.aln.toml) | `line-3` | 34,814.0 m | 11 |
| [`douala-line4.aln.toml`](douala-line4.aln.toml) | `line-4` | 33,886.7 m | 9 |
| [`douala-line5.aln.toml`](douala-line5.aln.toml) | `line-5` | 55,614.4 m | 21 |
| [`douala-line6.aln.toml`](douala-line6.aln.toml) | `line-6` | 4,963.0 m | 2 |
| [`douala-line7.aln.toml`](douala-line7.aln.toml) | `line-7` | 6,942.6 m | 4 |
| [`douala-line8.aln.toml`](douala-line8.aln.toml) | `line-8` | 5,194.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
