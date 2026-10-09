# Mbarara Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mbarara-line1.aln.toml`](mbarara-line1.aln.toml) | `line-1` | 10,182.1 m | 8 |
| [`mbarara-line10.aln.toml`](mbarara-line10.aln.toml) | `line-10` | 3,778.2 m | 3 |
| [`mbarara-line11.aln.toml`](mbarara-line11.aln.toml) | `line-11` | 3,078.5 m | 3 |
| [`mbarara-line12.aln.toml`](mbarara-line12.aln.toml) | `line-12` | 7,317.5 m | 5 |
| [`mbarara-line13.aln.toml`](mbarara-line13.aln.toml) | `line-13` | 4,277.0 m | 3 |
| [`mbarara-line2.aln.toml`](mbarara-line2.aln.toml) | `line-2` | 13,032.7 m | 9 |
| [`mbarara-line3.aln.toml`](mbarara-line3.aln.toml) | `line-3` | 24,737.6 m | 15 |
| [`mbarara-line4.aln.toml`](mbarara-line4.aln.toml) | `line-4` | 6,857.4 m | 4 |
| [`mbarara-line5.aln.toml`](mbarara-line5.aln.toml) | `line-5` | 2,161.7 m | 2 |
| [`mbarara-line6.aln.toml`](mbarara-line6.aln.toml) | `line-6` | 3,313.0 m | 3 |
| [`mbarara-line7.aln.toml`](mbarara-line7.aln.toml) | `line-7` | 3,356.5 m | 3 |
| [`mbarara-line8.aln.toml`](mbarara-line8.aln.toml) | `line-8` | 3,683.3 m | 3 |
| [`mbarara-line9.aln.toml`](mbarara-line9.aln.toml) | `line-9` | 9,973.9 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
