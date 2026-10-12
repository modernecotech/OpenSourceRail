# Gujranwala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gujranwala-line1.aln.toml`](gujranwala-line1.aln.toml) | `line-1` | 44,021.9 m | 12 |
| [`gujranwala-line2.aln.toml`](gujranwala-line2.aln.toml) | `line-2` | 31,441.8 m | 10 |
| [`gujranwala-line3.aln.toml`](gujranwala-line3.aln.toml) | `line-3` | 21,538.4 m | 9 |
| [`gujranwala-line4.aln.toml`](gujranwala-line4.aln.toml) | `line-4` | 28,693.6 m | 9 |
| [`gujranwala-line5.aln.toml`](gujranwala-line5.aln.toml) | `line-5` | 62,350.3 m | 17 |
| [`gujranwala-line6.aln.toml`](gujranwala-line6.aln.toml) | `line-6` | 5,223.1 m | 2 |
| [`gujranwala-line7.aln.toml`](gujranwala-line7.aln.toml) | `line-7` | 4,062.7 m | 2 |
| [`gujranwala-line8.aln.toml`](gujranwala-line8.aln.toml) | `line-8` | 5,067.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
