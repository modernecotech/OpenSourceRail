# Basra Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`basra-line1.aln.toml`](basra-line1.aln.toml) | `line-1` | 39,725.4 m | 26 |
| [`basra-line10.aln.toml`](basra-line10.aln.toml) | `line-10` | 7,174.7 m | 7 |
| [`basra-line11.aln.toml`](basra-line11.aln.toml) | `line-11` | 5,932.7 m | 5 |
| [`basra-line12.aln.toml`](basra-line12.aln.toml) | `line-12` | 6,178.2 m | 5 |
| [`basra-line13.aln.toml`](basra-line13.aln.toml) | `line-13` | 9,788.5 m | 8 |
| [`basra-line14.aln.toml`](basra-line14.aln.toml) | `line-14` | 9,355.2 m | 7 |
| [`basra-line15.aln.toml`](basra-line15.aln.toml) | `line-15` | 15,198.0 m | 9 |
| [`basra-line16.aln.toml`](basra-line16.aln.toml) | `line-16` | 5,805.0 m | 4 |
| [`basra-line17.aln.toml`](basra-line17.aln.toml) | `line-17` | 6,394.4 m | 5 |
| [`basra-line18.aln.toml`](basra-line18.aln.toml) | `line-18` | 5,891.3 m | 4 |
| [`basra-line19.aln.toml`](basra-line19.aln.toml) | `line-19` | 8,694.5 m | 7 |
| [`basra-line2.aln.toml`](basra-line2.aln.toml) | `line-2` | 17,314.0 m | 10 |
| [`basra-line20.aln.toml`](basra-line20.aln.toml) | `line-20` | 7,601.6 m | 4 |
| [`basra-line21.aln.toml`](basra-line21.aln.toml) | `line-21` | 10,016.3 m | 9 |
| [`basra-line22.aln.toml`](basra-line22.aln.toml) | `line-22` | 13,814.1 m | 9 |
| [`basra-line23.aln.toml`](basra-line23.aln.toml) | `line-23` | 14,352.5 m | 9 |
| [`basra-line24.aln.toml`](basra-line24.aln.toml) | `line-24` | 6,562.4 m | 5 |
| [`basra-line25.aln.toml`](basra-line25.aln.toml) | `line-25` | 18,737.5 m | 12 |
| [`basra-line3.aln.toml`](basra-line3.aln.toml) | `line-3` | 42,556.3 m | 25 |
| [`basra-line4.aln.toml`](basra-line4.aln.toml) | `line-4` | 34,970.7 m | 22 |
| [`basra-line5.aln.toml`](basra-line5.aln.toml) | `line-5` | 35,407.4 m | 25 |
| [`basra-line6.aln.toml`](basra-line6.aln.toml) | `line-6` | 26,389.0 m | 18 |
| [`basra-line7.aln.toml`](basra-line7.aln.toml) | `line-7` | 90,530.2 m | 52 |
| [`basra-line8.aln.toml`](basra-line8.aln.toml) | `line-8` | 9,007.5 m | 6 |
| [`basra-line9.aln.toml`](basra-line9.aln.toml) | `line-9` | 10,918.0 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
