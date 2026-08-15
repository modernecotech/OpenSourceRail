# Gujranwala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gujranwala-line1.aln.toml`](gujranwala-line1.aln.toml) | `line-1` | 39,245.6 m | 22 |
| [`gujranwala-line2.aln.toml`](gujranwala-line2.aln.toml) | `line-2` | 32,882.0 m | 17 |
| [`gujranwala-line3.aln.toml`](gujranwala-line3.aln.toml) | `line-3` | 20,042.4 m | 12 |
| [`gujranwala-line4.aln.toml`](gujranwala-line4.aln.toml) | `line-4` | 32,621.2 m | 17 |
| [`gujranwala-line5.aln.toml`](gujranwala-line5.aln.toml) | `line-5` | 62,394.9 m | 36 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
