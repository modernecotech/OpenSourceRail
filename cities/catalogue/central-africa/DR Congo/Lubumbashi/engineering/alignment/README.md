# Lubumbashi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lubumbashi-line1.aln.toml`](lubumbashi-line1.aln.toml) | `line-1` | 19,543.8 m | 12 |
| [`lubumbashi-line10.aln.toml`](lubumbashi-line10.aln.toml) | `line-10` | 3,556.5 m | 3 |
| [`lubumbashi-line11.aln.toml`](lubumbashi-line11.aln.toml) | `line-11` | 3,297.9 m | 3 |
| [`lubumbashi-line12.aln.toml`](lubumbashi-line12.aln.toml) | `line-12` | 4,689.8 m | 4 |
| [`lubumbashi-line13.aln.toml`](lubumbashi-line13.aln.toml) | `line-13` | 3,102.5 m | 2 |
| [`lubumbashi-line14.aln.toml`](lubumbashi-line14.aln.toml) | `line-14` | 3,315.4 m | 3 |
| [`lubumbashi-line15.aln.toml`](lubumbashi-line15.aln.toml) | `line-15` | 2,792.8 m | 3 |
| [`lubumbashi-line16.aln.toml`](lubumbashi-line16.aln.toml) | `line-16` | 2,392.8 m | 2 |
| [`lubumbashi-line17.aln.toml`](lubumbashi-line17.aln.toml) | `line-17` | 4,302.3 m | 3 |
| [`lubumbashi-line18.aln.toml`](lubumbashi-line18.aln.toml) | `line-18` | 6,448.9 m | 5 |
| [`lubumbashi-line19.aln.toml`](lubumbashi-line19.aln.toml) | `line-19` | 9,687.5 m | 6 |
| [`lubumbashi-line2.aln.toml`](lubumbashi-line2.aln.toml) | `line-2` | 16,441.0 m | 9 |
| [`lubumbashi-line20.aln.toml`](lubumbashi-line20.aln.toml) | `line-20` | 4,135.0 m | 4 |
| [`lubumbashi-line21.aln.toml`](lubumbashi-line21.aln.toml) | `line-21` | 2,611.4 m | 2 |
| [`lubumbashi-line22.aln.toml`](lubumbashi-line22.aln.toml) | `line-22` | 2,866.5 m | 2 |
| [`lubumbashi-line23.aln.toml`](lubumbashi-line23.aln.toml) | `line-23` | 10,823.7 m | 7 |
| [`lubumbashi-line24.aln.toml`](lubumbashi-line24.aln.toml) | `line-24` | 4,263.0 m | 3 |
| [`lubumbashi-line25.aln.toml`](lubumbashi-line25.aln.toml) | `line-25` | 6,948.5 m | 6 |
| [`lubumbashi-line26.aln.toml`](lubumbashi-line26.aln.toml) | `line-26` | 4,898.4 m | 3 |
| [`lubumbashi-line27.aln.toml`](lubumbashi-line27.aln.toml) | `line-27` | 3,703.1 m | 3 |
| [`lubumbashi-line28.aln.toml`](lubumbashi-line28.aln.toml) | `line-28` | 5,919.3 m | 5 |
| [`lubumbashi-line29.aln.toml`](lubumbashi-line29.aln.toml) | `line-29` | 4,981.5 m | 3 |
| [`lubumbashi-line3.aln.toml`](lubumbashi-line3.aln.toml) | `line-3` | 12,261.6 m | 10 |
| [`lubumbashi-line30.aln.toml`](lubumbashi-line30.aln.toml) | `line-30` | 4,859.8 m | 3 |
| [`lubumbashi-line4.aln.toml`](lubumbashi-line4.aln.toml) | `line-4` | 24,459.7 m | 15 |
| [`lubumbashi-line5.aln.toml`](lubumbashi-line5.aln.toml) | `line-5` | 43,769.4 m | 26 |
| [`lubumbashi-line6.aln.toml`](lubumbashi-line6.aln.toml) | `line-6` | 6,435.0 m | 4 |
| [`lubumbashi-line7.aln.toml`](lubumbashi-line7.aln.toml) | `line-7` | 2,429.6 m | 2 |
| [`lubumbashi-line8.aln.toml`](lubumbashi-line8.aln.toml) | `line-8` | 3,149.9 m | 3 |
| [`lubumbashi-line9.aln.toml`](lubumbashi-line9.aln.toml) | `line-9` | 3,561.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
