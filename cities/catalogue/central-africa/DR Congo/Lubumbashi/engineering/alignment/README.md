# Lubumbashi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lubumbashi-line1.aln.toml`](lubumbashi-line1.aln.toml) | `line-1` | 25,362.1 m | 12 |
| [`lubumbashi-line2.aln.toml`](lubumbashi-line2.aln.toml) | `line-2` | 23,542.1 m | 10 |
| [`lubumbashi-line3.aln.toml`](lubumbashi-line3.aln.toml) | `line-3` | 13,787.6 m | 5 |
| [`lubumbashi-line4.aln.toml`](lubumbashi-line4.aln.toml) | `line-4` | 27,973.4 m | 10 |
| [`lubumbashi-line5.aln.toml`](lubumbashi-line5.aln.toml) | `line-5` | 43,769.4 m | 14 |
| [`lubumbashi-line6.aln.toml`](lubumbashi-line6.aln.toml) | `line-6` | 7,438.4 m | 5 |
| [`lubumbashi-line7.aln.toml`](lubumbashi-line7.aln.toml) | `line-7` | 5,862.2 m | 4 |
| [`lubumbashi-line8.aln.toml`](lubumbashi-line8.aln.toml) | `line-8` | 10,376.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
