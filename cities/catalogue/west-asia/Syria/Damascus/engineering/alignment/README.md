# Damascus Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`damascus-line1.aln.toml`](damascus-line1.aln.toml) | `line-1` | 25,224.9 m | 17 |
| [`damascus-line10.aln.toml`](damascus-line10.aln.toml) | `line-10` | 3,367.6 m | 3 |
| [`damascus-line11.aln.toml`](damascus-line11.aln.toml) | `line-11` | 4,811.6 m | 4 |
| [`damascus-line12.aln.toml`](damascus-line12.aln.toml) | `line-12` | 5,785.3 m | 4 |
| [`damascus-line13.aln.toml`](damascus-line13.aln.toml) | `line-13` | 3,460.7 m | 3 |
| [`damascus-line14.aln.toml`](damascus-line14.aln.toml) | `line-14` | 7,004.0 m | 5 |
| [`damascus-line15.aln.toml`](damascus-line15.aln.toml) | `line-15` | 4,498.8 m | 4 |
| [`damascus-line16.aln.toml`](damascus-line16.aln.toml) | `line-16` | 4,812.4 m | 3 |
| [`damascus-line17.aln.toml`](damascus-line17.aln.toml) | `line-17` | 8,073.8 m | 7 |
| [`damascus-line18.aln.toml`](damascus-line18.aln.toml) | `line-18` | 3,840.1 m | 4 |
| [`damascus-line19.aln.toml`](damascus-line19.aln.toml) | `line-19` | 5,513.3 m | 4 |
| [`damascus-line2.aln.toml`](damascus-line2.aln.toml) | `line-2` | 24,110.0 m | 14 |
| [`damascus-line20.aln.toml`](damascus-line20.aln.toml) | `line-20` | 5,643.0 m | 4 |
| [`damascus-line21.aln.toml`](damascus-line21.aln.toml) | `line-21` | 7,447.9 m | 5 |
| [`damascus-line22.aln.toml`](damascus-line22.aln.toml) | `line-22` | 5,639.3 m | 5 |
| [`damascus-line23.aln.toml`](damascus-line23.aln.toml) | `line-23` | 4,701.7 m | 5 |
| [`damascus-line24.aln.toml`](damascus-line24.aln.toml) | `line-24` | 6,258.3 m | 4 |
| [`damascus-line25.aln.toml`](damascus-line25.aln.toml) | `line-25` | 8,353.9 m | 5 |
| [`damascus-line3.aln.toml`](damascus-line3.aln.toml) | `line-3` | 22,389.3 m | 18 |
| [`damascus-line4.aln.toml`](damascus-line4.aln.toml) | `line-4` | 18,922.3 m | 11 |
| [`damascus-line5.aln.toml`](damascus-line5.aln.toml) | `line-5` | 22,495.0 m | 13 |
| [`damascus-line6.aln.toml`](damascus-line6.aln.toml) | `line-6` | 56,007.7 m | 35 |
| [`damascus-line7.aln.toml`](damascus-line7.aln.toml) | `line-7` | 3,449.9 m | 3 |
| [`damascus-line8.aln.toml`](damascus-line8.aln.toml) | `line-8` | 5,274.4 m | 4 |
| [`damascus-line9.aln.toml`](damascus-line9.aln.toml) | `line-9` | 4,227.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
