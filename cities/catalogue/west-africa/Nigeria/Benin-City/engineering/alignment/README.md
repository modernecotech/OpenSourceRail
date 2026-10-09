# Benin-City Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`benin-city-line1.aln.toml`](benin-city-line1.aln.toml) | `line-1` | 13,564.4 m | 10 |
| [`benin-city-line10.aln.toml`](benin-city-line10.aln.toml) | `line-10` | 5,806.4 m | 5 |
| [`benin-city-line11.aln.toml`](benin-city-line11.aln.toml) | `line-11` | 4,618.5 m | 4 |
| [`benin-city-line12.aln.toml`](benin-city-line12.aln.toml) | `line-12` | 2,720.5 m | 2 |
| [`benin-city-line13.aln.toml`](benin-city-line13.aln.toml) | `line-13` | 5,959.1 m | 4 |
| [`benin-city-line14.aln.toml`](benin-city-line14.aln.toml) | `line-14` | 2,750.2 m | 2 |
| [`benin-city-line15.aln.toml`](benin-city-line15.aln.toml) | `line-15` | 5,195.9 m | 4 |
| [`benin-city-line16.aln.toml`](benin-city-line16.aln.toml) | `line-16` | 12,584.4 m | 9 |
| [`benin-city-line17.aln.toml`](benin-city-line17.aln.toml) | `line-17` | 3,568.5 m | 3 |
| [`benin-city-line18.aln.toml`](benin-city-line18.aln.toml) | `line-18` | 7,701.0 m | 6 |
| [`benin-city-line19.aln.toml`](benin-city-line19.aln.toml) | `line-19` | 3,195.0 m | 3 |
| [`benin-city-line2.aln.toml`](benin-city-line2.aln.toml) | `line-2` | 22,090.6 m | 16 |
| [`benin-city-line20.aln.toml`](benin-city-line20.aln.toml) | `line-20` | 4,551.9 m | 3 |
| [`benin-city-line21.aln.toml`](benin-city-line21.aln.toml) | `line-21` | 2,331.6 m | 2 |
| [`benin-city-line22.aln.toml`](benin-city-line22.aln.toml) | `line-22` | 2,581.7 m | 3 |
| [`benin-city-line23.aln.toml`](benin-city-line23.aln.toml) | `line-23` | 2,287.9 m | 2 |
| [`benin-city-line24.aln.toml`](benin-city-line24.aln.toml) | `line-24` | 5,752.0 m | 4 |
| [`benin-city-line25.aln.toml`](benin-city-line25.aln.toml) | `line-25` | 8,803.0 m | 6 |
| [`benin-city-line26.aln.toml`](benin-city-line26.aln.toml) | `line-26` | 4,216.7 m | 3 |
| [`benin-city-line27.aln.toml`](benin-city-line27.aln.toml) | `line-27` | 2,450.5 m | 2 |
| [`benin-city-line28.aln.toml`](benin-city-line28.aln.toml) | `line-28` | 5,265.6 m | 4 |
| [`benin-city-line3.aln.toml`](benin-city-line3.aln.toml) | `line-3` | 23,268.9 m | 15 |
| [`benin-city-line4.aln.toml`](benin-city-line4.aln.toml) | `line-4` | 22,586.6 m | 15 |
| [`benin-city-line5.aln.toml`](benin-city-line5.aln.toml) | `line-5` | 23,966.6 m | 20 |
| [`benin-city-line6.aln.toml`](benin-city-line6.aln.toml) | `line-6` | 2,795.4 m | 2 |
| [`benin-city-line7.aln.toml`](benin-city-line7.aln.toml) | `line-7` | 3,623.0 m | 3 |
| [`benin-city-line8.aln.toml`](benin-city-line8.aln.toml) | `line-8` | 4,389.6 m | 3 |
| [`benin-city-line9.aln.toml`](benin-city-line9.aln.toml) | `line-9` | 3,973.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
