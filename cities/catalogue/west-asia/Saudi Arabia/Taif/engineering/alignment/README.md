# Taif Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`taif-line1.aln.toml`](taif-line1.aln.toml) | `line-1` | 23,886.7 m | 16 |
| [`taif-line10.aln.toml`](taif-line10.aln.toml) | `line-10` | 6,077.2 m | 4 |
| [`taif-line11.aln.toml`](taif-line11.aln.toml) | `line-11` | 2,400.0 m | 2 |
| [`taif-line12.aln.toml`](taif-line12.aln.toml) | `line-12` | 3,220.0 m | 3 |
| [`taif-line13.aln.toml`](taif-line13.aln.toml) | `line-13` | 2,687.1 m | 2 |
| [`taif-line2.aln.toml`](taif-line2.aln.toml) | `line-2` | 12,367.6 m | 8 |
| [`taif-line3.aln.toml`](taif-line3.aln.toml) | `line-3` | 18,876.7 m | 11 |
| [`taif-line4.aln.toml`](taif-line4.aln.toml) | `line-4` | 4,950.7 m | 4 |
| [`taif-line5.aln.toml`](taif-line5.aln.toml) | `line-5` | 9,732.8 m | 6 |
| [`taif-line6.aln.toml`](taif-line6.aln.toml) | `line-6` | 5,587.5 m | 4 |
| [`taif-line7.aln.toml`](taif-line7.aln.toml) | `line-7` | 5,578.1 m | 4 |
| [`taif-line8.aln.toml`](taif-line8.aln.toml) | `line-8` | 2,909.0 m | 3 |
| [`taif-line9.aln.toml`](taif-line9.aln.toml) | `line-9` | 10,728.5 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
