# Hebron Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hebron-line1.aln.toml`](hebron-line1.aln.toml) | `line-1` | 16,938.8 m | 10 |
| [`hebron-line10.aln.toml`](hebron-line10.aln.toml) | `line-10` | 9,383.3 m | 5 |
| [`hebron-line11.aln.toml`](hebron-line11.aln.toml) | `line-11` | 3,250.8 m | 3 |
| [`hebron-line12.aln.toml`](hebron-line12.aln.toml) | `line-12` | 3,677.9 m | 3 |
| [`hebron-line13.aln.toml`](hebron-line13.aln.toml) | `line-13` | 6,760.3 m | 5 |
| [`hebron-line2.aln.toml`](hebron-line2.aln.toml) | `line-2` | 14,353.6 m | 8 |
| [`hebron-line3.aln.toml`](hebron-line3.aln.toml) | `line-3` | 19,332.6 m | 12 |
| [`hebron-line4.aln.toml`](hebron-line4.aln.toml) | `line-4` | 3,000.0 m | 5 |
| [`hebron-line5.aln.toml`](hebron-line5.aln.toml) | `line-5` | 4,559.3 m | 6 |
| [`hebron-line6.aln.toml`](hebron-line6.aln.toml) | `line-6` | 4,513.6 m | 3 |
| [`hebron-line7.aln.toml`](hebron-line7.aln.toml) | `line-7` | 2,361.3 m | 2 |
| [`hebron-line8.aln.toml`](hebron-line8.aln.toml) | `line-8` | 2,970.8 m | 3 |
| [`hebron-line9.aln.toml`](hebron-line9.aln.toml) | `line-9` | 2,639.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
