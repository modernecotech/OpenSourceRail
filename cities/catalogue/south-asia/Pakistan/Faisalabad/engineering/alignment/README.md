# Faisalabad Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`faisalabad-line1.aln.toml`](faisalabad-line1.aln.toml) | `line-1` | 27,374.9 m | 21 |
| [`faisalabad-line10.aln.toml`](faisalabad-line10.aln.toml) | `line-10` | 4,999.9 m | 4 |
| [`faisalabad-line11.aln.toml`](faisalabad-line11.aln.toml) | `line-11` | 3,215.6 m | 3 |
| [`faisalabad-line12.aln.toml`](faisalabad-line12.aln.toml) | `line-12` | 3,761.3 m | 3 |
| [`faisalabad-line13.aln.toml`](faisalabad-line13.aln.toml) | `line-13` | 7,830.0 m | 5 |
| [`faisalabad-line14.aln.toml`](faisalabad-line14.aln.toml) | `line-14` | 7,809.3 m | 5 |
| [`faisalabad-line15.aln.toml`](faisalabad-line15.aln.toml) | `line-15` | 3,484.3 m | 3 |
| [`faisalabad-line16.aln.toml`](faisalabad-line16.aln.toml) | `line-16` | 6,174.5 m | 4 |
| [`faisalabad-line17.aln.toml`](faisalabad-line17.aln.toml) | `line-17` | 8,770.1 m | 5 |
| [`faisalabad-line18.aln.toml`](faisalabad-line18.aln.toml) | `line-18` | 4,256.2 m | 3 |
| [`faisalabad-line19.aln.toml`](faisalabad-line19.aln.toml) | `line-19` | 5,730.4 m | 3 |
| [`faisalabad-line2.aln.toml`](faisalabad-line2.aln.toml) | `line-2` | 19,966.1 m | 17 |
| [`faisalabad-line20.aln.toml`](faisalabad-line20.aln.toml) | `line-20` | 8,499.1 m | 5 |
| [`faisalabad-line21.aln.toml`](faisalabad-line21.aln.toml) | `line-21` | 13,621.4 m | 10 |
| [`faisalabad-line22.aln.toml`](faisalabad-line22.aln.toml) | `line-22` | 4,775.3 m | 6 |
| [`faisalabad-line23.aln.toml`](faisalabad-line23.aln.toml) | `line-23` | 3,631.6 m | 4 |
| [`faisalabad-line3.aln.toml`](faisalabad-line3.aln.toml) | `line-3` | 20,288.8 m | 15 |
| [`faisalabad-line4.aln.toml`](faisalabad-line4.aln.toml) | `line-4` | 20,915.7 m | 19 |
| [`faisalabad-line5.aln.toml`](faisalabad-line5.aln.toml) | `line-5` | 23,346.3 m | 16 |
| [`faisalabad-line6.aln.toml`](faisalabad-line6.aln.toml) | `line-6` | 39,189.3 m | 23 |
| [`faisalabad-line7.aln.toml`](faisalabad-line7.aln.toml) | `line-7` | 4,187.6 m | 4 |
| [`faisalabad-line8.aln.toml`](faisalabad-line8.aln.toml) | `line-8` | 7,379.8 m | 5 |
| [`faisalabad-line9.aln.toml`](faisalabad-line9.aln.toml) | `line-9` | 8,682.5 m | 9 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
