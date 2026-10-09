# Phnom-Penh Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`phnom-penh-line1.aln.toml`](phnom-penh-line1.aln.toml) | `line-1` | 27,274.6 m | 19 |
| [`phnom-penh-line10.aln.toml`](phnom-penh-line10.aln.toml) | `line-10` | 6,033.3 m | 6 |
| [`phnom-penh-line11.aln.toml`](phnom-penh-line11.aln.toml) | `line-11` | 5,093.0 m | 4 |
| [`phnom-penh-line12.aln.toml`](phnom-penh-line12.aln.toml) | `line-12` | 5,032.1 m | 3 |
| [`phnom-penh-line13.aln.toml`](phnom-penh-line13.aln.toml) | `line-13` | 5,954.1 m | 4 |
| [`phnom-penh-line14.aln.toml`](phnom-penh-line14.aln.toml) | `line-14` | 6,480.0 m | 6 |
| [`phnom-penh-line15.aln.toml`](phnom-penh-line15.aln.toml) | `line-15` | 5,504.2 m | 5 |
| [`phnom-penh-line16.aln.toml`](phnom-penh-line16.aln.toml) | `line-16` | 7,579.0 m | 7 |
| [`phnom-penh-line17.aln.toml`](phnom-penh-line17.aln.toml) | `line-17` | 5,154.2 m | 3 |
| [`phnom-penh-line18.aln.toml`](phnom-penh-line18.aln.toml) | `line-18` | 11,114.1 m | 8 |
| [`phnom-penh-line19.aln.toml`](phnom-penh-line19.aln.toml) | `line-19` | 6,058.1 m | 4 |
| [`phnom-penh-line2.aln.toml`](phnom-penh-line2.aln.toml) | `line-2` | 26,141.2 m | 21 |
| [`phnom-penh-line20.aln.toml`](phnom-penh-line20.aln.toml) | `line-20` | 17,328.3 m | 11 |
| [`phnom-penh-line21.aln.toml`](phnom-penh-line21.aln.toml) | `line-21` | 5,311.3 m | 3 |
| [`phnom-penh-line22.aln.toml`](phnom-penh-line22.aln.toml) | `line-22` | 8,540.0 m | 8 |
| [`phnom-penh-line23.aln.toml`](phnom-penh-line23.aln.toml) | `line-23` | 5,727.8 m | 5 |
| [`phnom-penh-line24.aln.toml`](phnom-penh-line24.aln.toml) | `line-24` | 11,922.7 m | 7 |
| [`phnom-penh-line25.aln.toml`](phnom-penh-line25.aln.toml) | `line-25` | 6,290.7 m | 4 |
| [`phnom-penh-line3.aln.toml`](phnom-penh-line3.aln.toml) | `line-3` | 55,050.0 m | 50 |
| [`phnom-penh-line4.aln.toml`](phnom-penh-line4.aln.toml) | `line-4` | 36,880.1 m | 30 |
| [`phnom-penh-line5.aln.toml`](phnom-penh-line5.aln.toml) | `line-5` | 34,703.0 m | 24 |
| [`phnom-penh-line6.aln.toml`](phnom-penh-line6.aln.toml) | `line-6` | 64,519.0 m | 42 |
| [`phnom-penh-line7.aln.toml`](phnom-penh-line7.aln.toml) | `line-7` | 4,900.7 m | 3 |
| [`phnom-penh-line8.aln.toml`](phnom-penh-line8.aln.toml) | `line-8` | 6,265.8 m | 5 |
| [`phnom-penh-line9.aln.toml`](phnom-penh-line9.aln.toml) | `line-9` | 8,352.2 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
