# Port-Harcourt Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`port-harcourt-line1.aln.toml`](port-harcourt-line1.aln.toml) | `line-1` | 35,496.2 m | 21 |
| [`port-harcourt-line10.aln.toml`](port-harcourt-line10.aln.toml) | `line-10` | 5,181.9 m | 4 |
| [`port-harcourt-line11.aln.toml`](port-harcourt-line11.aln.toml) | `line-11` | 7,654.9 m | 6 |
| [`port-harcourt-line12.aln.toml`](port-harcourt-line12.aln.toml) | `line-12` | 3,528.8 m | 3 |
| [`port-harcourt-line13.aln.toml`](port-harcourt-line13.aln.toml) | `line-13` | 3,776.5 m | 4 |
| [`port-harcourt-line14.aln.toml`](port-harcourt-line14.aln.toml) | `line-14` | 4,057.1 m | 4 |
| [`port-harcourt-line15.aln.toml`](port-harcourt-line15.aln.toml) | `line-15` | 7,131.4 m | 5 |
| [`port-harcourt-line16.aln.toml`](port-harcourt-line16.aln.toml) | `line-16` | 4,377.9 m | 3 |
| [`port-harcourt-line17.aln.toml`](port-harcourt-line17.aln.toml) | `line-17` | 11,091.5 m | 9 |
| [`port-harcourt-line18.aln.toml`](port-harcourt-line18.aln.toml) | `line-18` | 7,265.2 m | 5 |
| [`port-harcourt-line19.aln.toml`](port-harcourt-line19.aln.toml) | `line-19` | 10,047.6 m | 7 |
| [`port-harcourt-line2.aln.toml`](port-harcourt-line2.aln.toml) | `line-2` | 23,527.8 m | 16 |
| [`port-harcourt-line20.aln.toml`](port-harcourt-line20.aln.toml) | `line-20` | 3,562.7 m | 3 |
| [`port-harcourt-line21.aln.toml`](port-harcourt-line21.aln.toml) | `line-21` | 7,619.3 m | 4 |
| [`port-harcourt-line22.aln.toml`](port-harcourt-line22.aln.toml) | `line-22` | 4,485.6 m | 3 |
| [`port-harcourt-line23.aln.toml`](port-harcourt-line23.aln.toml) | `line-23` | 7,871.5 m | 9 |
| [`port-harcourt-line24.aln.toml`](port-harcourt-line24.aln.toml) | `line-24` | 5,518.7 m | 5 |
| [`port-harcourt-line25.aln.toml`](port-harcourt-line25.aln.toml) | `line-25` | 13,358.9 m | 8 |
| [`port-harcourt-line26.aln.toml`](port-harcourt-line26.aln.toml) | `line-26` | 3,931.0 m | 5 |
| [`port-harcourt-line27.aln.toml`](port-harcourt-line27.aln.toml) | `line-27` | 13,433.7 m | 8 |
| [`port-harcourt-line28.aln.toml`](port-harcourt-line28.aln.toml) | `line-28` | 13,242.6 m | 8 |
| [`port-harcourt-line29.aln.toml`](port-harcourt-line29.aln.toml) | `line-29` | 9,145.4 m | 8 |
| [`port-harcourt-line3.aln.toml`](port-harcourt-line3.aln.toml) | `line-3` | 25,611.7 m | 16 |
| [`port-harcourt-line30.aln.toml`](port-harcourt-line30.aln.toml) | `line-30` | 3,726.2 m | 4 |
| [`port-harcourt-line4.aln.toml`](port-harcourt-line4.aln.toml) | `line-4` | 29,241.2 m | 24 |
| [`port-harcourt-line5.aln.toml`](port-harcourt-line5.aln.toml) | `line-5` | 60,039.1 m | 40 |
| [`port-harcourt-line6.aln.toml`](port-harcourt-line6.aln.toml) | `line-6` | 6,329.3 m | 5 |
| [`port-harcourt-line7.aln.toml`](port-harcourt-line7.aln.toml) | `line-7` | 8,454.4 m | 7 |
| [`port-harcourt-line8.aln.toml`](port-harcourt-line8.aln.toml) | `line-8` | 4,926.4 m | 5 |
| [`port-harcourt-line9.aln.toml`](port-harcourt-line9.aln.toml) | `line-9` | 4,404.2 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
