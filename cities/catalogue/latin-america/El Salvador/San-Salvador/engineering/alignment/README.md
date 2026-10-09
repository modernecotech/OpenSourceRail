# San-Salvador Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`san-salvador-line1.aln.toml`](san-salvador-line1.aln.toml) | `line-1` | 27,197.7 m | 19 |
| [`san-salvador-line10.aln.toml`](san-salvador-line10.aln.toml) | `line-10` | 5,829.6 m | 4 |
| [`san-salvador-line11.aln.toml`](san-salvador-line11.aln.toml) | `line-11` | 5,530.4 m | 4 |
| [`san-salvador-line12.aln.toml`](san-salvador-line12.aln.toml) | `line-12` | 5,115.6 m | 4 |
| [`san-salvador-line13.aln.toml`](san-salvador-line13.aln.toml) | `line-13` | 7,108.8 m | 5 |
| [`san-salvador-line14.aln.toml`](san-salvador-line14.aln.toml) | `line-14` | 6,091.0 m | 4 |
| [`san-salvador-line15.aln.toml`](san-salvador-line15.aln.toml) | `line-15` | 9,967.5 m | 8 |
| [`san-salvador-line16.aln.toml`](san-salvador-line16.aln.toml) | `line-16` | 14,065.5 m | 9 |
| [`san-salvador-line17.aln.toml`](san-salvador-line17.aln.toml) | `line-17` | 9,133.4 m | 6 |
| [`san-salvador-line18.aln.toml`](san-salvador-line18.aln.toml) | `line-18` | 5,786.1 m | 5 |
| [`san-salvador-line19.aln.toml`](san-salvador-line19.aln.toml) | `line-19` | 10,148.0 m | 6 |
| [`san-salvador-line2.aln.toml`](san-salvador-line2.aln.toml) | `line-2` | 33,026.3 m | 20 |
| [`san-salvador-line20.aln.toml`](san-salvador-line20.aln.toml) | `line-20` | 8,081.9 m | 4 |
| [`san-salvador-line21.aln.toml`](san-salvador-line21.aln.toml) | `line-21` | 7,619.8 m | 5 |
| [`san-salvador-line3.aln.toml`](san-salvador-line3.aln.toml) | `line-3` | 34,465.9 m | 21 |
| [`san-salvador-line4.aln.toml`](san-salvador-line4.aln.toml) | `line-4` | 36,238.5 m | 24 |
| [`san-salvador-line5.aln.toml`](san-salvador-line5.aln.toml) | `line-5` | 29,506.3 m | 18 |
| [`san-salvador-line6.aln.toml`](san-salvador-line6.aln.toml) | `line-6` | 74,811.5 m | 45 |
| [`san-salvador-line7.aln.toml`](san-salvador-line7.aln.toml) | `line-7` | 6,581.8 m | 7 |
| [`san-salvador-line8.aln.toml`](san-salvador-line8.aln.toml) | `line-8` | 5,004.8 m | 4 |
| [`san-salvador-line9.aln.toml`](san-salvador-line9.aln.toml) | `line-9` | 8,447.7 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
