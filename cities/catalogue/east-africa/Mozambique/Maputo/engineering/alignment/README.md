# Maputo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maputo-line1.aln.toml`](maputo-line1.aln.toml) | `line-1` | 21,914.0 m | 21 |
| [`maputo-line10.aln.toml`](maputo-line10.aln.toml) | `line-10` | 4,960.7 m | 4 |
| [`maputo-line11.aln.toml`](maputo-line11.aln.toml) | `line-11` | 8,413.4 m | 6 |
| [`maputo-line12.aln.toml`](maputo-line12.aln.toml) | `line-12` | 4,029.9 m | 3 |
| [`maputo-line13.aln.toml`](maputo-line13.aln.toml) | `line-13` | 5,256.7 m | 4 |
| [`maputo-line14.aln.toml`](maputo-line14.aln.toml) | `line-14` | 4,729.4 m | 3 |
| [`maputo-line15.aln.toml`](maputo-line15.aln.toml) | `line-15` | 5,718.0 m | 3 |
| [`maputo-line16.aln.toml`](maputo-line16.aln.toml) | `line-16` | 4,730.7 m | 3 |
| [`maputo-line17.aln.toml`](maputo-line17.aln.toml) | `line-17` | 5,040.7 m | 3 |
| [`maputo-line18.aln.toml`](maputo-line18.aln.toml) | `line-18` | 8,333.2 m | 5 |
| [`maputo-line19.aln.toml`](maputo-line19.aln.toml) | `line-19` | 3,728.8 m | 3 |
| [`maputo-line2.aln.toml`](maputo-line2.aln.toml) | `line-2` | 19,740.7 m | 15 |
| [`maputo-line20.aln.toml`](maputo-line20.aln.toml) | `line-20` | 4,464.5 m | 7 |
| [`maputo-line21.aln.toml`](maputo-line21.aln.toml) | `line-21` | 4,829.6 m | 4 |
| [`maputo-line22.aln.toml`](maputo-line22.aln.toml) | `line-22` | 6,401.8 m | 4 |
| [`maputo-line23.aln.toml`](maputo-line23.aln.toml) | `line-23` | 6,845.8 m | 7 |
| [`maputo-line3.aln.toml`](maputo-line3.aln.toml) | `line-3` | 18,516.9 m | 10 |
| [`maputo-line4.aln.toml`](maputo-line4.aln.toml) | `line-4` | 27,944.0 m | 16 |
| [`maputo-line5.aln.toml`](maputo-line5.aln.toml) | `line-5` | 18,112.0 m | 13 |
| [`maputo-line6.aln.toml`](maputo-line6.aln.toml) | `line-6` | 54,142.1 m | 40 |
| [`maputo-line7.aln.toml`](maputo-line7.aln.toml) | `line-7` | 6,667.0 m | 5 |
| [`maputo-line8.aln.toml`](maputo-line8.aln.toml) | `line-8` | 5,973.9 m | 6 |
| [`maputo-line9.aln.toml`](maputo-line9.aln.toml) | `line-9` | 8,818.4 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
