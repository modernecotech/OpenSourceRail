# Ouagadougou Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ouagadougou-line1.aln.toml`](ouagadougou-line1.aln.toml) | `line-1` | 33,932.5 m | 21 |
| [`ouagadougou-line10.aln.toml`](ouagadougou-line10.aln.toml) | `line-10` | 6,263.8 m | 5 |
| [`ouagadougou-line11.aln.toml`](ouagadougou-line11.aln.toml) | `line-11` | 5,281.6 m | 5 |
| [`ouagadougou-line12.aln.toml`](ouagadougou-line12.aln.toml) | `line-12` | 8,259.9 m | 5 |
| [`ouagadougou-line13.aln.toml`](ouagadougou-line13.aln.toml) | `line-13` | 8,081.6 m | 5 |
| [`ouagadougou-line14.aln.toml`](ouagadougou-line14.aln.toml) | `line-14` | 5,259.3 m | 4 |
| [`ouagadougou-line15.aln.toml`](ouagadougou-line15.aln.toml) | `line-15` | 5,233.0 m | 4 |
| [`ouagadougou-line16.aln.toml`](ouagadougou-line16.aln.toml) | `line-16` | 7,572.4 m | 7 |
| [`ouagadougou-line17.aln.toml`](ouagadougou-line17.aln.toml) | `line-17` | 4,108.8 m | 3 |
| [`ouagadougou-line18.aln.toml`](ouagadougou-line18.aln.toml) | `line-18` | 4,507.0 m | 3 |
| [`ouagadougou-line19.aln.toml`](ouagadougou-line19.aln.toml) | `line-19` | 8,006.8 m | 6 |
| [`ouagadougou-line2.aln.toml`](ouagadougou-line2.aln.toml) | `line-2` | 19,441.9 m | 15 |
| [`ouagadougou-line20.aln.toml`](ouagadougou-line20.aln.toml) | `line-20` | 5,142.2 m | 4 |
| [`ouagadougou-line21.aln.toml`](ouagadougou-line21.aln.toml) | `line-21` | 6,861.6 m | 4 |
| [`ouagadougou-line22.aln.toml`](ouagadougou-line22.aln.toml) | `line-22` | 5,390.7 m | 5 |
| [`ouagadougou-line23.aln.toml`](ouagadougou-line23.aln.toml) | `line-23` | 5,621.2 m | 4 |
| [`ouagadougou-line24.aln.toml`](ouagadougou-line24.aln.toml) | `line-24` | 11,458.0 m | 7 |
| [`ouagadougou-line25.aln.toml`](ouagadougou-line25.aln.toml) | `line-25` | 5,332.8 m | 4 |
| [`ouagadougou-line26.aln.toml`](ouagadougou-line26.aln.toml) | `line-26` | 7,332.7 m | 5 |
| [`ouagadougou-line27.aln.toml`](ouagadougou-line27.aln.toml) | `line-27` | 15,696.7 m | 9 |
| [`ouagadougou-line28.aln.toml`](ouagadougou-line28.aln.toml) | `line-28` | 9,065.6 m | 7 |
| [`ouagadougou-line29.aln.toml`](ouagadougou-line29.aln.toml) | `line-29` | 4,529.3 m | 4 |
| [`ouagadougou-line3.aln.toml`](ouagadougou-line3.aln.toml) | `line-3` | 25,524.5 m | 15 |
| [`ouagadougou-line30.aln.toml`](ouagadougou-line30.aln.toml) | `line-30` | 6,844.9 m | 7 |
| [`ouagadougou-line31.aln.toml`](ouagadougou-line31.aln.toml) | `line-31` | 4,659.9 m | 3 |
| [`ouagadougou-line32.aln.toml`](ouagadougou-line32.aln.toml) | `line-32` | 9,830.5 m | 6 |
| [`ouagadougou-line33.aln.toml`](ouagadougou-line33.aln.toml) | `line-33` | 16,980.7 m | 11 |
| [`ouagadougou-line4.aln.toml`](ouagadougou-line4.aln.toml) | `line-4` | 27,702.1 m | 19 |
| [`ouagadougou-line5.aln.toml`](ouagadougou-line5.aln.toml) | `line-5` | 27,201.8 m | 17 |
| [`ouagadougou-line6.aln.toml`](ouagadougou-line6.aln.toml) | `line-6` | 60,666.4 m | 35 |
| [`ouagadougou-line7.aln.toml`](ouagadougou-line7.aln.toml) | `line-7` | 5,557.3 m | 4 |
| [`ouagadougou-line8.aln.toml`](ouagadougou-line8.aln.toml) | `line-8` | 5,520.5 m | 5 |
| [`ouagadougou-line9.aln.toml`](ouagadougou-line9.aln.toml) | `line-9` | 4,814.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
