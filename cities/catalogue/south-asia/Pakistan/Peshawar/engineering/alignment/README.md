# Peshawar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`peshawar-line1.aln.toml`](peshawar-line1.aln.toml) | `line-1` | 28,987.7 m | 19 |
| [`peshawar-line10.aln.toml`](peshawar-line10.aln.toml) | `line-10` | 4,241.3 m | 4 |
| [`peshawar-line11.aln.toml`](peshawar-line11.aln.toml) | `line-11` | 3,542.7 m | 3 |
| [`peshawar-line12.aln.toml`](peshawar-line12.aln.toml) | `line-12` | 7,080.7 m | 4 |
| [`peshawar-line13.aln.toml`](peshawar-line13.aln.toml) | `line-13` | 9,478.7 m | 6 |
| [`peshawar-line14.aln.toml`](peshawar-line14.aln.toml) | `line-14` | 4,466.7 m | 3 |
| [`peshawar-line15.aln.toml`](peshawar-line15.aln.toml) | `line-15` | 10,040.0 m | 6 |
| [`peshawar-line16.aln.toml`](peshawar-line16.aln.toml) | `line-16` | 3,824.2 m | 3 |
| [`peshawar-line17.aln.toml`](peshawar-line17.aln.toml) | `line-17` | 6,970.7 m | 5 |
| [`peshawar-line18.aln.toml`](peshawar-line18.aln.toml) | `line-18` | 6,649.8 m | 4 |
| [`peshawar-line19.aln.toml`](peshawar-line19.aln.toml) | `line-19` | 5,448.7 m | 5 |
| [`peshawar-line2.aln.toml`](peshawar-line2.aln.toml) | `line-2` | 28,971.3 m | 16 |
| [`peshawar-line20.aln.toml`](peshawar-line20.aln.toml) | `line-20` | 4,758.1 m | 3 |
| [`peshawar-line21.aln.toml`](peshawar-line21.aln.toml) | `line-21` | 7,897.9 m | 5 |
| [`peshawar-line22.aln.toml`](peshawar-line22.aln.toml) | `line-22` | 12,645.0 m | 9 |
| [`peshawar-line23.aln.toml`](peshawar-line23.aln.toml) | `line-23` | 6,965.7 m | 5 |
| [`peshawar-line24.aln.toml`](peshawar-line24.aln.toml) | `line-24` | 7,336.4 m | 4 |
| [`peshawar-line25.aln.toml`](peshawar-line25.aln.toml) | `line-25` | 5,345.6 m | 4 |
| [`peshawar-line26.aln.toml`](peshawar-line26.aln.toml) | `line-26` | 12,424.9 m | 7 |
| [`peshawar-line27.aln.toml`](peshawar-line27.aln.toml) | `line-27` | 4,961.5 m | 4 |
| [`peshawar-line28.aln.toml`](peshawar-line28.aln.toml) | `line-28` | 13,242.3 m | 9 |
| [`peshawar-line29.aln.toml`](peshawar-line29.aln.toml) | `line-29` | 6,382.2 m | 4 |
| [`peshawar-line3.aln.toml`](peshawar-line3.aln.toml) | `line-3` | 30,747.1 m | 20 |
| [`peshawar-line30.aln.toml`](peshawar-line30.aln.toml) | `line-30` | 3,649.8 m | 3 |
| [`peshawar-line31.aln.toml`](peshawar-line31.aln.toml) | `line-31` | 6,992.0 m | 5 |
| [`peshawar-line4.aln.toml`](peshawar-line4.aln.toml) | `line-4` | 22,123.9 m | 14 |
| [`peshawar-line5.aln.toml`](peshawar-line5.aln.toml) | `line-5` | 61,824.6 m | 35 |
| [`peshawar-line6.aln.toml`](peshawar-line6.aln.toml) | `line-6` | 5,472.9 m | 5 |
| [`peshawar-line7.aln.toml`](peshawar-line7.aln.toml) | `line-7` | 3,632.2 m | 4 |
| [`peshawar-line8.aln.toml`](peshawar-line8.aln.toml) | `line-8` | 4,586.8 m | 4 |
| [`peshawar-line9.aln.toml`](peshawar-line9.aln.toml) | `line-9` | 3,594.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
