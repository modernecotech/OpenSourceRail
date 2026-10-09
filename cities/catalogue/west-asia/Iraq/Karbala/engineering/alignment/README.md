# Karbala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karbala-line1.aln.toml`](karbala-line1.aln.toml) | `line-1` | 23,564.1 m | 14 |
| [`karbala-line10.aln.toml`](karbala-line10.aln.toml) | `line-10` | 11,745.1 m | 8 |
| [`karbala-line11.aln.toml`](karbala-line11.aln.toml) | `line-11` | 6,899.6 m | 5 |
| [`karbala-line12.aln.toml`](karbala-line12.aln.toml) | `line-12` | 3,492.2 m | 4 |
| [`karbala-line13.aln.toml`](karbala-line13.aln.toml) | `line-13` | 7,919.5 m | 5 |
| [`karbala-line14.aln.toml`](karbala-line14.aln.toml) | `line-14` | 5,738.6 m | 4 |
| [`karbala-line15.aln.toml`](karbala-line15.aln.toml) | `line-15` | 4,641.0 m | 4 |
| [`karbala-line16.aln.toml`](karbala-line16.aln.toml) | `line-16` | 3,179.1 m | 3 |
| [`karbala-line2.aln.toml`](karbala-line2.aln.toml) | `line-2` | 17,900.4 m | 14 |
| [`karbala-line3.aln.toml`](karbala-line3.aln.toml) | `line-3` | 16,326.7 m | 11 |
| [`karbala-line4.aln.toml`](karbala-line4.aln.toml) | `line-4` | 18,421.5 m | 10 |
| [`karbala-line5.aln.toml`](karbala-line5.aln.toml) | `line-5` | 21,983.4 m | 14 |
| [`karbala-line6.aln.toml`](karbala-line6.aln.toml) | `line-6` | 56,571.2 m | 38 |
| [`karbala-line7.aln.toml`](karbala-line7.aln.toml) | `line-7` | 6,101.6 m | 5 |
| [`karbala-line8.aln.toml`](karbala-line8.aln.toml) | `line-8` | 6,975.8 m | 6 |
| [`karbala-line9.aln.toml`](karbala-line9.aln.toml) | `line-9` | 8,875.5 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
