# Gujranwala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gujranwala-line1.aln.toml`](gujranwala-line1.aln.toml) | `line-1` | 37,306.4 m | 26 |
| [`gujranwala-line10.aln.toml`](gujranwala-line10.aln.toml) | `line-10` | 5,645.5 m | 5 |
| [`gujranwala-line11.aln.toml`](gujranwala-line11.aln.toml) | `line-11` | 8,781.1 m | 5 |
| [`gujranwala-line12.aln.toml`](gujranwala-line12.aln.toml) | `line-12` | 5,140.7 m | 4 |
| [`gujranwala-line13.aln.toml`](gujranwala-line13.aln.toml) | `line-13` | 6,102.5 m | 4 |
| [`gujranwala-line14.aln.toml`](gujranwala-line14.aln.toml) | `line-14` | 6,170.2 m | 4 |
| [`gujranwala-line15.aln.toml`](gujranwala-line15.aln.toml) | `line-15` | 10,079.0 m | 8 |
| [`gujranwala-line16.aln.toml`](gujranwala-line16.aln.toml) | `line-16` | 4,991.9 m | 4 |
| [`gujranwala-line17.aln.toml`](gujranwala-line17.aln.toml) | `line-17` | 8,467.7 m | 5 |
| [`gujranwala-line18.aln.toml`](gujranwala-line18.aln.toml) | `line-18` | 4,530.2 m | 3 |
| [`gujranwala-line19.aln.toml`](gujranwala-line19.aln.toml) | `line-19` | 3,605.3 m | 3 |
| [`gujranwala-line2.aln.toml`](gujranwala-line2.aln.toml) | `line-2` | 31,441.8 m | 22 |
| [`gujranwala-line20.aln.toml`](gujranwala-line20.aln.toml) | `line-20` | 6,410.4 m | 5 |
| [`gujranwala-line21.aln.toml`](gujranwala-line21.aln.toml) | `line-21` | 3,959.3 m | 4 |
| [`gujranwala-line22.aln.toml`](gujranwala-line22.aln.toml) | `line-22` | 8,469.3 m | 10 |
| [`gujranwala-line23.aln.toml`](gujranwala-line23.aln.toml) | `line-23` | 12,839.0 m | 9 |
| [`gujranwala-line24.aln.toml`](gujranwala-line24.aln.toml) | `line-24` | 4,079.9 m | 3 |
| [`gujranwala-line25.aln.toml`](gujranwala-line25.aln.toml) | `line-25` | 7,195.2 m | 5 |
| [`gujranwala-line26.aln.toml`](gujranwala-line26.aln.toml) | `line-26` | 4,599.3 m | 5 |
| [`gujranwala-line27.aln.toml`](gujranwala-line27.aln.toml) | `line-27` | 4,065.1 m | 4 |
| [`gujranwala-line28.aln.toml`](gujranwala-line28.aln.toml) | `line-28` | 3,749.8 m | 3 |
| [`gujranwala-line29.aln.toml`](gujranwala-line29.aln.toml) | `line-29` | 7,893.6 m | 5 |
| [`gujranwala-line3.aln.toml`](gujranwala-line3.aln.toml) | `line-3` | 18,382.2 m | 15 |
| [`gujranwala-line30.aln.toml`](gujranwala-line30.aln.toml) | `line-30` | 3,753.9 m | 5 |
| [`gujranwala-line31.aln.toml`](gujranwala-line31.aln.toml) | `line-31` | 13,316.8 m | 10 |
| [`gujranwala-line32.aln.toml`](gujranwala-line32.aln.toml) | `line-32` | 3,881.9 m | 3 |
| [`gujranwala-line33.aln.toml`](gujranwala-line33.aln.toml) | `line-33` | 3,752.2 m | 4 |
| [`gujranwala-line4.aln.toml`](gujranwala-line4.aln.toml) | `line-4` | 28,693.6 m | 18 |
| [`gujranwala-line5.aln.toml`](gujranwala-line5.aln.toml) | `line-5` | 59,996.3 m | 41 |
| [`gujranwala-line6.aln.toml`](gujranwala-line6.aln.toml) | `line-6` | 4,137.3 m | 7 |
| [`gujranwala-line7.aln.toml`](gujranwala-line7.aln.toml) | `line-7` | 4,311.0 m | 3 |
| [`gujranwala-line8.aln.toml`](gujranwala-line8.aln.toml) | `line-8` | 10,966.2 m | 10 |
| [`gujranwala-line9.aln.toml`](gujranwala-line9.aln.toml) | `line-9` | 5,067.1 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
