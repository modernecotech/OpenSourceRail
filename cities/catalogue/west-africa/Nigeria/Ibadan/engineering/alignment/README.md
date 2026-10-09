# Ibadan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ibadan-line1.aln.toml`](ibadan-line1.aln.toml) | `line-1` | 21,493.6 m | 16 |
| [`ibadan-line10.aln.toml`](ibadan-line10.aln.toml) | `line-10` | 2,383.7 m | 2 |
| [`ibadan-line11.aln.toml`](ibadan-line11.aln.toml) | `line-11` | 5,145.5 m | 5 |
| [`ibadan-line12.aln.toml`](ibadan-line12.aln.toml) | `line-12` | 6,017.5 m | 4 |
| [`ibadan-line13.aln.toml`](ibadan-line13.aln.toml) | `line-13` | 2,632.2 m | 2 |
| [`ibadan-line14.aln.toml`](ibadan-line14.aln.toml) | `line-14` | 4,841.9 m | 4 |
| [`ibadan-line15.aln.toml`](ibadan-line15.aln.toml) | `line-15` | 6,296.0 m | 4 |
| [`ibadan-line16.aln.toml`](ibadan-line16.aln.toml) | `line-16` | 4,501.6 m | 3 |
| [`ibadan-line17.aln.toml`](ibadan-line17.aln.toml) | `line-17` | 2,235.0 m | 2 |
| [`ibadan-line18.aln.toml`](ibadan-line18.aln.toml) | `line-18` | 3,612.5 m | 3 |
| [`ibadan-line19.aln.toml`](ibadan-line19.aln.toml) | `line-19` | 4,063.9 m | 5 |
| [`ibadan-line2.aln.toml`](ibadan-line2.aln.toml) | `line-2` | 17,180.3 m | 13 |
| [`ibadan-line20.aln.toml`](ibadan-line20.aln.toml) | `line-20` | 7,704.9 m | 6 |
| [`ibadan-line21.aln.toml`](ibadan-line21.aln.toml) | `line-21` | 6,412.9 m | 4 |
| [`ibadan-line22.aln.toml`](ibadan-line22.aln.toml) | `line-22` | 7,295.9 m | 6 |
| [`ibadan-line23.aln.toml`](ibadan-line23.aln.toml) | `line-23` | 6,675.2 m | 6 |
| [`ibadan-line24.aln.toml`](ibadan-line24.aln.toml) | `line-24` | 4,186.8 m | 4 |
| [`ibadan-line25.aln.toml`](ibadan-line25.aln.toml) | `line-25` | 2,818.0 m | 3 |
| [`ibadan-line26.aln.toml`](ibadan-line26.aln.toml) | `line-26` | 4,372.4 m | 4 |
| [`ibadan-line27.aln.toml`](ibadan-line27.aln.toml) | `line-27` | 3,868.8 m | 3 |
| [`ibadan-line3.aln.toml`](ibadan-line3.aln.toml) | `line-3` | 15,772.7 m | 12 |
| [`ibadan-line4.aln.toml`](ibadan-line4.aln.toml) | `line-4` | 26,395.5 m | 16 |
| [`ibadan-line5.aln.toml`](ibadan-line5.aln.toml) | `line-5` | 26,830.9 m | 18 |
| [`ibadan-line6.aln.toml`](ibadan-line6.aln.toml) | `line-6` | 4,365.9 m | 3 |
| [`ibadan-line7.aln.toml`](ibadan-line7.aln.toml) | `line-7` | 5,674.8 m | 4 |
| [`ibadan-line8.aln.toml`](ibadan-line8.aln.toml) | `line-8` | 9,457.3 m | 7 |
| [`ibadan-line9.aln.toml`](ibadan-line9.aln.toml) | `line-9` | 4,775.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
