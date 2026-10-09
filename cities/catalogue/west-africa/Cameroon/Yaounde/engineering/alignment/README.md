# Yaounde Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yaounde-line1.aln.toml`](yaounde-line1.aln.toml) | `line-1` | 38,666.3 m | 23 |
| [`yaounde-line10.aln.toml`](yaounde-line10.aln.toml) | `line-10` | 6,469.6 m | 6 |
| [`yaounde-line11.aln.toml`](yaounde-line11.aln.toml) | `line-11` | 7,185.1 m | 5 |
| [`yaounde-line12.aln.toml`](yaounde-line12.aln.toml) | `line-12` | 4,091.6 m | 4 |
| [`yaounde-line13.aln.toml`](yaounde-line13.aln.toml) | `line-13` | 4,090.2 m | 3 |
| [`yaounde-line14.aln.toml`](yaounde-line14.aln.toml) | `line-14` | 11,961.8 m | 10 |
| [`yaounde-line15.aln.toml`](yaounde-line15.aln.toml) | `line-15` | 9,652.8 m | 7 |
| [`yaounde-line16.aln.toml`](yaounde-line16.aln.toml) | `line-16` | 15,896.3 m | 11 |
| [`yaounde-line17.aln.toml`](yaounde-line17.aln.toml) | `line-17` | 4,254.7 m | 3 |
| [`yaounde-line18.aln.toml`](yaounde-line18.aln.toml) | `line-18` | 6,635.0 m | 4 |
| [`yaounde-line19.aln.toml`](yaounde-line19.aln.toml) | `line-19` | 7,684.9 m | 7 |
| [`yaounde-line2.aln.toml`](yaounde-line2.aln.toml) | `line-2` | 43,625.1 m | 25 |
| [`yaounde-line20.aln.toml`](yaounde-line20.aln.toml) | `line-20` | 6,104.4 m | 4 |
| [`yaounde-line21.aln.toml`](yaounde-line21.aln.toml) | `line-21` | 15,618.7 m | 11 |
| [`yaounde-line3.aln.toml`](yaounde-line3.aln.toml) | `line-3` | 30,054.9 m | 19 |
| [`yaounde-line4.aln.toml`](yaounde-line4.aln.toml) | `line-4` | 16,602.2 m | 12 |
| [`yaounde-line5.aln.toml`](yaounde-line5.aln.toml) | `line-5` | 62,969.0 m | 44 |
| [`yaounde-line6.aln.toml`](yaounde-line6.aln.toml) | `line-6` | 5,180.1 m | 3 |
| [`yaounde-line7.aln.toml`](yaounde-line7.aln.toml) | `line-7` | 7,850.9 m | 7 |
| [`yaounde-line8.aln.toml`](yaounde-line8.aln.toml) | `line-8` | 4,279.7 m | 3 |
| [`yaounde-line9.aln.toml`](yaounde-line9.aln.toml) | `line-9` | 7,091.9 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
