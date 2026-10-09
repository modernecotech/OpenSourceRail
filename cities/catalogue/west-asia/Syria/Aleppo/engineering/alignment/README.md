# Aleppo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`aleppo-line1.aln.toml`](aleppo-line1.aln.toml) | `line-1` | 23,571.6 m | 15 |
| [`aleppo-line10.aln.toml`](aleppo-line10.aln.toml) | `line-10` | 6,360.0 m | 4 |
| [`aleppo-line11.aln.toml`](aleppo-line11.aln.toml) | `line-11` | 3,299.4 m | 3 |
| [`aleppo-line12.aln.toml`](aleppo-line12.aln.toml) | `line-12` | 4,712.0 m | 3 |
| [`aleppo-line13.aln.toml`](aleppo-line13.aln.toml) | `line-13` | 7,556.1 m | 5 |
| [`aleppo-line14.aln.toml`](aleppo-line14.aln.toml) | `line-14` | 4,473.6 m | 4 |
| [`aleppo-line15.aln.toml`](aleppo-line15.aln.toml) | `line-15` | 4,829.4 m | 3 |
| [`aleppo-line16.aln.toml`](aleppo-line16.aln.toml) | `line-16` | 4,375.0 m | 3 |
| [`aleppo-line17.aln.toml`](aleppo-line17.aln.toml) | `line-17` | 6,337.1 m | 6 |
| [`aleppo-line18.aln.toml`](aleppo-line18.aln.toml) | `line-18` | 3,899.3 m | 3 |
| [`aleppo-line19.aln.toml`](aleppo-line19.aln.toml) | `line-19` | 10,039.5 m | 7 |
| [`aleppo-line2.aln.toml`](aleppo-line2.aln.toml) | `line-2` | 24,243.6 m | 15 |
| [`aleppo-line20.aln.toml`](aleppo-line20.aln.toml) | `line-20` | 7,805.9 m | 4 |
| [`aleppo-line21.aln.toml`](aleppo-line21.aln.toml) | `line-21` | 3,858.5 m | 3 |
| [`aleppo-line22.aln.toml`](aleppo-line22.aln.toml) | `line-22` | 9,497.3 m | 6 |
| [`aleppo-line3.aln.toml`](aleppo-line3.aln.toml) | `line-3` | 13,191.3 m | 9 |
| [`aleppo-line4.aln.toml`](aleppo-line4.aln.toml) | `line-4` | 20,685.3 m | 13 |
| [`aleppo-line5.aln.toml`](aleppo-line5.aln.toml) | `line-5` | 23,850.6 m | 15 |
| [`aleppo-line6.aln.toml`](aleppo-line6.aln.toml) | `line-6` | 54,397.3 m | 33 |
| [`aleppo-line7.aln.toml`](aleppo-line7.aln.toml) | `line-7` | 6,508.4 m | 5 |
| [`aleppo-line8.aln.toml`](aleppo-line8.aln.toml) | `line-8` | 6,932.2 m | 5 |
| [`aleppo-line9.aln.toml`](aleppo-line9.aln.toml) | `line-9` | 5,179.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
