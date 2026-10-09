# Bamako Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bamako-line1.aln.toml`](bamako-line1.aln.toml) | `line-1` | 40,817.2 m | 25 |
| [`bamako-line10.aln.toml`](bamako-line10.aln.toml) | `line-10` | 5,120.4 m | 7 |
| [`bamako-line11.aln.toml`](bamako-line11.aln.toml) | `line-11` | 4,788.4 m | 4 |
| [`bamako-line12.aln.toml`](bamako-line12.aln.toml) | `line-12` | 4,878.7 m | 5 |
| [`bamako-line13.aln.toml`](bamako-line13.aln.toml) | `line-13` | 5,285.6 m | 4 |
| [`bamako-line14.aln.toml`](bamako-line14.aln.toml) | `line-14` | 8,483.0 m | 7 |
| [`bamako-line15.aln.toml`](bamako-line15.aln.toml) | `line-15` | 7,255.2 m | 5 |
| [`bamako-line16.aln.toml`](bamako-line16.aln.toml) | `line-16` | 6,536.7 m | 5 |
| [`bamako-line17.aln.toml`](bamako-line17.aln.toml) | `line-17` | 5,491.0 m | 4 |
| [`bamako-line18.aln.toml`](bamako-line18.aln.toml) | `line-18` | 5,057.3 m | 3 |
| [`bamako-line19.aln.toml`](bamako-line19.aln.toml) | `line-19` | 10,837.1 m | 8 |
| [`bamako-line2.aln.toml`](bamako-line2.aln.toml) | `line-2` | 23,834.1 m | 18 |
| [`bamako-line20.aln.toml`](bamako-line20.aln.toml) | `line-20` | 7,693.0 m | 5 |
| [`bamako-line21.aln.toml`](bamako-line21.aln.toml) | `line-21` | 8,884.2 m | 9 |
| [`bamako-line22.aln.toml`](bamako-line22.aln.toml) | `line-22` | 5,658.7 m | 4 |
| [`bamako-line3.aln.toml`](bamako-line3.aln.toml) | `line-3` | 16,384.3 m | 11 |
| [`bamako-line4.aln.toml`](bamako-line4.aln.toml) | `line-4` | 56,881.4 m | 40 |
| [`bamako-line5.aln.toml`](bamako-line5.aln.toml) | `line-5` | 19,825.3 m | 14 |
| [`bamako-line6.aln.toml`](bamako-line6.aln.toml) | `line-6` | 64,858.7 m | 41 |
| [`bamako-line7.aln.toml`](bamako-line7.aln.toml) | `line-7` | 8,151.0 m | 7 |
| [`bamako-line8.aln.toml`](bamako-line8.aln.toml) | `line-8` | 6,061.5 m | 5 |
| [`bamako-line9.aln.toml`](bamako-line9.aln.toml) | `line-9` | 8,610.3 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
