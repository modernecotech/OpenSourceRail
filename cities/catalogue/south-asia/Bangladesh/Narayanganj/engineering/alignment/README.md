# Narayanganj Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`narayanganj-line1.aln.toml`](narayanganj-line1.aln.toml) | `line-1` | 33,485.2 m | 22 |
| [`narayanganj-line10.aln.toml`](narayanganj-line10.aln.toml) | `line-10` | 3,152.2 m | 3 |
| [`narayanganj-line11.aln.toml`](narayanganj-line11.aln.toml) | `line-11` | 6,711.5 m | 4 |
| [`narayanganj-line12.aln.toml`](narayanganj-line12.aln.toml) | `line-12` | 3,531.6 m | 3 |
| [`narayanganj-line13.aln.toml`](narayanganj-line13.aln.toml) | `line-13` | 2,759.1 m | 2 |
| [`narayanganj-line14.aln.toml`](narayanganj-line14.aln.toml) | `line-14` | 3,146.8 m | 2 |
| [`narayanganj-line15.aln.toml`](narayanganj-line15.aln.toml) | `line-15` | 2,992.2 m | 2 |
| [`narayanganj-line16.aln.toml`](narayanganj-line16.aln.toml) | `line-16` | 3,560.7 m | 3 |
| [`narayanganj-line17.aln.toml`](narayanganj-line17.aln.toml) | `line-17` | 4,153.0 m | 4 |
| [`narayanganj-line18.aln.toml`](narayanganj-line18.aln.toml) | `line-18` | 9,540.6 m | 8 |
| [`narayanganj-line19.aln.toml`](narayanganj-line19.aln.toml) | `line-19` | 5,881.0 m | 4 |
| [`narayanganj-line2.aln.toml`](narayanganj-line2.aln.toml) | `line-2` | 23,075.8 m | 13 |
| [`narayanganj-line3.aln.toml`](narayanganj-line3.aln.toml) | `line-3` | 18,953.9 m | 12 |
| [`narayanganj-line4.aln.toml`](narayanganj-line4.aln.toml) | `line-4` | 2,001.7 m | 2 |
| [`narayanganj-line5.aln.toml`](narayanganj-line5.aln.toml) | `line-5` | 4,121.9 m | 3 |
| [`narayanganj-line6.aln.toml`](narayanganj-line6.aln.toml) | `line-6` | 3,901.0 m | 3 |
| [`narayanganj-line7.aln.toml`](narayanganj-line7.aln.toml) | `line-7` | 6,678.4 m | 4 |
| [`narayanganj-line8.aln.toml`](narayanganj-line8.aln.toml) | `line-8` | 6,326.7 m | 5 |
| [`narayanganj-line9.aln.toml`](narayanganj-line9.aln.toml) | `line-9` | 6,070.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
