# Douala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`douala-line1.aln.toml`](douala-line1.aln.toml) | `line-1` | 35,711.8 m | 31 |
| [`douala-line10.aln.toml`](douala-line10.aln.toml) | `line-10` | 3,880.4 m | 3 |
| [`douala-line11.aln.toml`](douala-line11.aln.toml) | `line-11` | 5,257.0 m | 4 |
| [`douala-line12.aln.toml`](douala-line12.aln.toml) | `line-12` | 5,149.8 m | 4 |
| [`douala-line13.aln.toml`](douala-line13.aln.toml) | `line-13` | 7,820.3 m | 4 |
| [`douala-line14.aln.toml`](douala-line14.aln.toml) | `line-14` | 4,890.2 m | 5 |
| [`douala-line15.aln.toml`](douala-line15.aln.toml) | `line-15` | 6,864.3 m | 11 |
| [`douala-line16.aln.toml`](douala-line16.aln.toml) | `line-16` | 6,606.8 m | 5 |
| [`douala-line17.aln.toml`](douala-line17.aln.toml) | `line-17` | 8,395.9 m | 6 |
| [`douala-line18.aln.toml`](douala-line18.aln.toml) | `line-18` | 6,559.6 m | 5 |
| [`douala-line19.aln.toml`](douala-line19.aln.toml) | `line-19` | 4,633.4 m | 4 |
| [`douala-line2.aln.toml`](douala-line2.aln.toml) | `line-2` | 39,523.3 m | 22 |
| [`douala-line20.aln.toml`](douala-line20.aln.toml) | `line-20` | 5,251.3 m | 4 |
| [`douala-line21.aln.toml`](douala-line21.aln.toml) | `line-21` | 8,560.1 m | 5 |
| [`douala-line22.aln.toml`](douala-line22.aln.toml) | `line-22` | 9,743.1 m | 8 |
| [`douala-line23.aln.toml`](douala-line23.aln.toml) | `line-23` | 4,753.5 m | 3 |
| [`douala-line24.aln.toml`](douala-line24.aln.toml) | `line-24` | 9,535.6 m | 8 |
| [`douala-line25.aln.toml`](douala-line25.aln.toml) | `line-25` | 6,827.8 m | 4 |
| [`douala-line26.aln.toml`](douala-line26.aln.toml) | `line-26` | 4,884.8 m | 4 |
| [`douala-line27.aln.toml`](douala-line27.aln.toml) | `line-27` | 14,893.9 m | 21 |
| [`douala-line28.aln.toml`](douala-line28.aln.toml) | `line-28` | 6,778.7 m | 4 |
| [`douala-line29.aln.toml`](douala-line29.aln.toml) | `line-29` | 4,337.8 m | 3 |
| [`douala-line3.aln.toml`](douala-line3.aln.toml) | `line-3` | 25,449.2 m | 19 |
| [`douala-line30.aln.toml`](douala-line30.aln.toml) | `line-30` | 9,544.9 m | 7 |
| [`douala-line31.aln.toml`](douala-line31.aln.toml) | `line-31` | 5,211.3 m | 4 |
| [`douala-line32.aln.toml`](douala-line32.aln.toml) | `line-32` | 9,862.4 m | 7 |
| [`douala-line33.aln.toml`](douala-line33.aln.toml) | `line-33` | 10,983.7 m | 7 |
| [`douala-line4.aln.toml`](douala-line4.aln.toml) | `line-4` | 48,532.0 m | 30 |
| [`douala-line5.aln.toml`](douala-line5.aln.toml) | `line-5` | 43,893.8 m | 27 |
| [`douala-line6.aln.toml`](douala-line6.aln.toml) | `line-6` | 4,519.3 m | 3 |
| [`douala-line7.aln.toml`](douala-line7.aln.toml) | `line-7` | 4,875.3 m | 5 |
| [`douala-line8.aln.toml`](douala-line8.aln.toml) | `line-8` | 6,263.2 m | 4 |
| [`douala-line9.aln.toml`](douala-line9.aln.toml) | `line-9` | 4,657.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
