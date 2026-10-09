# Larkana Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`larkana-line1.aln.toml`](larkana-line1.aln.toml) | `line-1` | 21,266.3 m | 12 |
| [`larkana-line2.aln.toml`](larkana-line2.aln.toml) | `line-2` | 12,814.4 m | 9 |
| [`larkana-line3.aln.toml`](larkana-line3.aln.toml) | `line-3` | 5,696.7 m | 4 |
| [`larkana-line4.aln.toml`](larkana-line4.aln.toml) | `line-4` | 4,972.7 m | 4 |
| [`larkana-line5.aln.toml`](larkana-line5.aln.toml) | `line-5` | 7,521.0 m | 5 |
| [`larkana-line6.aln.toml`](larkana-line6.aln.toml) | `line-6` | 4,163.6 m | 3 |
| [`larkana-line7.aln.toml`](larkana-line7.aln.toml) | `line-7` | 5,069.0 m | 3 |
| [`larkana-line8.aln.toml`](larkana-line8.aln.toml) | `line-8` | 2,429.6 m | 2 |
| [`larkana-line9.aln.toml`](larkana-line9.aln.toml) | `line-9` | 3,885.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
