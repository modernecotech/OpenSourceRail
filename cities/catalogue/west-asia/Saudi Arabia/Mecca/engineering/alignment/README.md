# Mecca Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mecca-line1.aln.toml`](mecca-line1.aln.toml) | `line-1` | 27,831.8 m | 16 |
| [`mecca-line10.aln.toml`](mecca-line10.aln.toml) | `line-10` | 4,880.7 m | 4 |
| [`mecca-line11.aln.toml`](mecca-line11.aln.toml) | `line-11` | 4,801.3 m | 4 |
| [`mecca-line12.aln.toml`](mecca-line12.aln.toml) | `line-12` | 5,667.0 m | 4 |
| [`mecca-line13.aln.toml`](mecca-line13.aln.toml) | `line-13` | 4,095.3 m | 3 |
| [`mecca-line14.aln.toml`](mecca-line14.aln.toml) | `line-14` | 6,532.7 m | 5 |
| [`mecca-line15.aln.toml`](mecca-line15.aln.toml) | `line-15` | 7,584.5 m | 5 |
| [`mecca-line16.aln.toml`](mecca-line16.aln.toml) | `line-16` | 5,884.4 m | 3 |
| [`mecca-line17.aln.toml`](mecca-line17.aln.toml) | `line-17` | 9,512.3 m | 6 |
| [`mecca-line18.aln.toml`](mecca-line18.aln.toml) | `line-18` | 8,898.3 m | 6 |
| [`mecca-line19.aln.toml`](mecca-line19.aln.toml) | `line-19` | 4,388.2 m | 3 |
| [`mecca-line2.aln.toml`](mecca-line2.aln.toml) | `line-2` | 23,404.0 m | 15 |
| [`mecca-line20.aln.toml`](mecca-line20.aln.toml) | `line-20` | 4,121.6 m | 3 |
| [`mecca-line21.aln.toml`](mecca-line21.aln.toml) | `line-21` | 5,895.8 m | 4 |
| [`mecca-line22.aln.toml`](mecca-line22.aln.toml) | `line-22` | 5,191.9 m | 4 |
| [`mecca-line23.aln.toml`](mecca-line23.aln.toml) | `line-23` | 4,700.7 m | 6 |
| [`mecca-line24.aln.toml`](mecca-line24.aln.toml) | `line-24` | 6,270.9 m | 6 |
| [`mecca-line25.aln.toml`](mecca-line25.aln.toml) | `line-25` | 4,572.5 m | 5 |
| [`mecca-line26.aln.toml`](mecca-line26.aln.toml) | `line-26` | 4,726.2 m | 4 |
| [`mecca-line27.aln.toml`](mecca-line27.aln.toml) | `line-27` | 4,090.8 m | 3 |
| [`mecca-line3.aln.toml`](mecca-line3.aln.toml) | `line-3` | 32,601.1 m | 18 |
| [`mecca-line4.aln.toml`](mecca-line4.aln.toml) | `line-4` | 30,194.2 m | 16 |
| [`mecca-line5.aln.toml`](mecca-line5.aln.toml) | `line-5` | 23,263.4 m | 15 |
| [`mecca-line6.aln.toml`](mecca-line6.aln.toml) | `line-6` | 65,707.4 m | 40 |
| [`mecca-line7.aln.toml`](mecca-line7.aln.toml) | `line-7` | 6,438.6 m | 5 |
| [`mecca-line8.aln.toml`](mecca-line8.aln.toml) | `line-8` | 8,691.2 m | 7 |
| [`mecca-line9.aln.toml`](mecca-line9.aln.toml) | `line-9` | 4,809.8 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
