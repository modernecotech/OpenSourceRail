# Tunis Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tunis-line1.aln.toml`](tunis-line1.aln.toml) | `line-1` | 34,858.6 m | 19 |
| [`tunis-line10.aln.toml`](tunis-line10.aln.toml) | `line-10` | 4,152.2 m | 4 |
| [`tunis-line11.aln.toml`](tunis-line11.aln.toml) | `line-11` | 4,359.3 m | 3 |
| [`tunis-line12.aln.toml`](tunis-line12.aln.toml) | `line-12` | 4,597.9 m | 4 |
| [`tunis-line13.aln.toml`](tunis-line13.aln.toml) | `line-13` | 12,125.8 m | 6 |
| [`tunis-line14.aln.toml`](tunis-line14.aln.toml) | `line-14` | 5,640.1 m | 5 |
| [`tunis-line15.aln.toml`](tunis-line15.aln.toml) | `line-15` | 9,410.1 m | 6 |
| [`tunis-line16.aln.toml`](tunis-line16.aln.toml) | `line-16` | 4,524.8 m | 3 |
| [`tunis-line17.aln.toml`](tunis-line17.aln.toml) | `line-17` | 5,806.8 m | 4 |
| [`tunis-line18.aln.toml`](tunis-line18.aln.toml) | `line-18` | 5,077.6 m | 4 |
| [`tunis-line19.aln.toml`](tunis-line19.aln.toml) | `line-19` | 4,274.8 m | 3 |
| [`tunis-line2.aln.toml`](tunis-line2.aln.toml) | `line-2` | 24,480.1 m | 19 |
| [`tunis-line20.aln.toml`](tunis-line20.aln.toml) | `line-20` | 6,160.5 m | 4 |
| [`tunis-line21.aln.toml`](tunis-line21.aln.toml) | `line-21` | 8,083.6 m | 6 |
| [`tunis-line22.aln.toml`](tunis-line22.aln.toml) | `line-22` | 7,170.2 m | 5 |
| [`tunis-line23.aln.toml`](tunis-line23.aln.toml) | `line-23` | 4,874.9 m | 3 |
| [`tunis-line24.aln.toml`](tunis-line24.aln.toml) | `line-24` | 7,676.8 m | 5 |
| [`tunis-line25.aln.toml`](tunis-line25.aln.toml) | `line-25` | 6,776.5 m | 5 |
| [`tunis-line26.aln.toml`](tunis-line26.aln.toml) | `line-26` | 7,343.6 m | 5 |
| [`tunis-line27.aln.toml`](tunis-line27.aln.toml) | `line-27` | 11,051.1 m | 7 |
| [`tunis-line28.aln.toml`](tunis-line28.aln.toml) | `line-28` | 5,967.0 m | 4 |
| [`tunis-line29.aln.toml`](tunis-line29.aln.toml) | `line-29` | 6,139.0 m | 4 |
| [`tunis-line3.aln.toml`](tunis-line3.aln.toml) | `line-3` | 39,917.8 m | 22 |
| [`tunis-line30.aln.toml`](tunis-line30.aln.toml) | `line-30` | 7,547.1 m | 5 |
| [`tunis-line31.aln.toml`](tunis-line31.aln.toml) | `line-31` | 9,706.7 m | 6 |
| [`tunis-line32.aln.toml`](tunis-line32.aln.toml) | `line-32` | 4,207.2 m | 3 |
| [`tunis-line33.aln.toml`](tunis-line33.aln.toml) | `line-33` | 6,591.3 m | 4 |
| [`tunis-line34.aln.toml`](tunis-line34.aln.toml) | `line-34` | 9,487.1 m | 6 |
| [`tunis-line35.aln.toml`](tunis-line35.aln.toml) | `line-35` | 5,382.2 m | 4 |
| [`tunis-line4.aln.toml`](tunis-line4.aln.toml) | `line-4` | 28,074.8 m | 19 |
| [`tunis-line5.aln.toml`](tunis-line5.aln.toml) | `line-5` | 74,349.3 m | 45 |
| [`tunis-line6.aln.toml`](tunis-line6.aln.toml) | `line-6` | 4,309.0 m | 3 |
| [`tunis-line7.aln.toml`](tunis-line7.aln.toml) | `line-7` | 8,476.7 m | 6 |
| [`tunis-line8.aln.toml`](tunis-line8.aln.toml) | `line-8` | 6,123.0 m | 4 |
| [`tunis-line9.aln.toml`](tunis-line9.aln.toml) | `line-9` | 6,143.2 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
