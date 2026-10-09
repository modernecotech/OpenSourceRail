# Yangon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yangon-line1.aln.toml`](yangon-line1.aln.toml) | `line-1` | 35,759.6 m | 25 |
| [`yangon-line10.aln.toml`](yangon-line10.aln.toml) | `line-10` | 6,661.1 m | 6 |
| [`yangon-line11.aln.toml`](yangon-line11.aln.toml) | `line-11` | 7,208.4 m | 5 |
| [`yangon-line12.aln.toml`](yangon-line12.aln.toml) | `line-12` | 7,679.3 m | 7 |
| [`yangon-line13.aln.toml`](yangon-line13.aln.toml) | `line-13` | 7,581.5 m | 6 |
| [`yangon-line14.aln.toml`](yangon-line14.aln.toml) | `line-14` | 7,712.2 m | 5 |
| [`yangon-line15.aln.toml`](yangon-line15.aln.toml) | `line-15` | 6,009.3 m | 4 |
| [`yangon-line16.aln.toml`](yangon-line16.aln.toml) | `line-16` | 10,866.0 m | 7 |
| [`yangon-line17.aln.toml`](yangon-line17.aln.toml) | `line-17` | 12,532.1 m | 9 |
| [`yangon-line18.aln.toml`](yangon-line18.aln.toml) | `line-18` | 12,317.5 m | 8 |
| [`yangon-line19.aln.toml`](yangon-line19.aln.toml) | `line-19` | 8,992.6 m | 6 |
| [`yangon-line2.aln.toml`](yangon-line2.aln.toml) | `line-2` | 31,787.9 m | 18 |
| [`yangon-line20.aln.toml`](yangon-line20.aln.toml) | `line-20` | 8,300.8 m | 6 |
| [`yangon-line21.aln.toml`](yangon-line21.aln.toml) | `line-21` | 6,495.9 m | 5 |
| [`yangon-line22.aln.toml`](yangon-line22.aln.toml) | `line-22` | 11,708.9 m | 7 |
| [`yangon-line23.aln.toml`](yangon-line23.aln.toml) | `line-23` | 10,286.1 m | 7 |
| [`yangon-line24.aln.toml`](yangon-line24.aln.toml) | `line-24` | 10,401.5 m | 10 |
| [`yangon-line25.aln.toml`](yangon-line25.aln.toml) | `line-25` | 7,353.5 m | 6 |
| [`yangon-line26.aln.toml`](yangon-line26.aln.toml) | `line-26` | 12,270.5 m | 9 |
| [`yangon-line27.aln.toml`](yangon-line27.aln.toml) | `line-27` | 8,383.2 m | 5 |
| [`yangon-line28.aln.toml`](yangon-line28.aln.toml) | `line-28` | 15,377.5 m | 16 |
| [`yangon-line29.aln.toml`](yangon-line29.aln.toml) | `line-29` | 9,793.5 m | 8 |
| [`yangon-line3.aln.toml`](yangon-line3.aln.toml) | `line-3` | 59,438.5 m | 46 |
| [`yangon-line30.aln.toml`](yangon-line30.aln.toml) | `line-30` | 6,714.1 m | 5 |
| [`yangon-line31.aln.toml`](yangon-line31.aln.toml) | `line-31` | 6,785.8 m | 5 |
| [`yangon-line32.aln.toml`](yangon-line32.aln.toml) | `line-32` | 6,727.4 m | 4 |
| [`yangon-line4.aln.toml`](yangon-line4.aln.toml) | `line-4` | 53,999.3 m | 36 |
| [`yangon-line5.aln.toml`](yangon-line5.aln.toml) | `line-5` | 48,480.0 m | 38 |
| [`yangon-line6.aln.toml`](yangon-line6.aln.toml) | `line-6` | 35,136.0 m | 27 |
| [`yangon-line7.aln.toml`](yangon-line7.aln.toml) | `line-7` | 36,122.0 m | 29 |
| [`yangon-line8.aln.toml`](yangon-line8.aln.toml) | `line-8` | 51,762.5 m | 40 |
| [`yangon-line9.aln.toml`](yangon-line9.aln.toml) | `line-9` | 95,434.2 m | 73 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
