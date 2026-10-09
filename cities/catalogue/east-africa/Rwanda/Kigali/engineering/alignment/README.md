# Kigali Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kigali-line1.aln.toml`](kigali-line1.aln.toml) | `line-1` | 27,641.7 m | 20 |
| [`kigali-line10.aln.toml`](kigali-line10.aln.toml) | `line-10` | 4,753.9 m | 4 |
| [`kigali-line11.aln.toml`](kigali-line11.aln.toml) | `line-11` | 13,258.8 m | 9 |
| [`kigali-line12.aln.toml`](kigali-line12.aln.toml) | `line-12` | 4,977.6 m | 4 |
| [`kigali-line13.aln.toml`](kigali-line13.aln.toml) | `line-13` | 4,255.6 m | 4 |
| [`kigali-line14.aln.toml`](kigali-line14.aln.toml) | `line-14` | 3,537.9 m | 3 |
| [`kigali-line15.aln.toml`](kigali-line15.aln.toml) | `line-15` | 6,691.6 m | 4 |
| [`kigali-line16.aln.toml`](kigali-line16.aln.toml) | `line-16` | 5,454.4 m | 6 |
| [`kigali-line17.aln.toml`](kigali-line17.aln.toml) | `line-17` | 4,251.6 m | 4 |
| [`kigali-line18.aln.toml`](kigali-line18.aln.toml) | `line-18` | 8,456.1 m | 6 |
| [`kigali-line19.aln.toml`](kigali-line19.aln.toml) | `line-19` | 5,057.3 m | 4 |
| [`kigali-line2.aln.toml`](kigali-line2.aln.toml) | `line-2` | 15,831.8 m | 12 |
| [`kigali-line20.aln.toml`](kigali-line20.aln.toml) | `line-20` | 5,040.1 m | 5 |
| [`kigali-line21.aln.toml`](kigali-line21.aln.toml) | `line-21` | 3,275.4 m | 3 |
| [`kigali-line22.aln.toml`](kigali-line22.aln.toml) | `line-22` | 5,837.0 m | 4 |
| [`kigali-line23.aln.toml`](kigali-line23.aln.toml) | `line-23` | 5,939.0 m | 4 |
| [`kigali-line24.aln.toml`](kigali-line24.aln.toml) | `line-24` | 6,453.4 m | 6 |
| [`kigali-line25.aln.toml`](kigali-line25.aln.toml) | `line-25` | 11,737.3 m | 10 |
| [`kigali-line26.aln.toml`](kigali-line26.aln.toml) | `line-26` | 5,841.9 m | 5 |
| [`kigali-line27.aln.toml`](kigali-line27.aln.toml) | `line-27` | 6,574.1 m | 5 |
| [`kigali-line28.aln.toml`](kigali-line28.aln.toml) | `line-28` | 8,899.3 m | 6 |
| [`kigali-line29.aln.toml`](kigali-line29.aln.toml) | `line-29` | 7,074.5 m | 5 |
| [`kigali-line3.aln.toml`](kigali-line3.aln.toml) | `line-3` | 14,343.3 m | 14 |
| [`kigali-line30.aln.toml`](kigali-line30.aln.toml) | `line-30` | 5,167.6 m | 3 |
| [`kigali-line4.aln.toml`](kigali-line4.aln.toml) | `line-4` | 21,334.5 m | 14 |
| [`kigali-line5.aln.toml`](kigali-line5.aln.toml) | `line-5` | 21,461.6 m | 15 |
| [`kigali-line6.aln.toml`](kigali-line6.aln.toml) | `line-6` | 56,601.6 m | 37 |
| [`kigali-line7.aln.toml`](kigali-line7.aln.toml) | `line-7` | 3,537.6 m | 4 |
| [`kigali-line8.aln.toml`](kigali-line8.aln.toml) | `line-8` | 4,553.3 m | 3 |
| [`kigali-line9.aln.toml`](kigali-line9.aln.toml) | `line-9` | 5,462.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
