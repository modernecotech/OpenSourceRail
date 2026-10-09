# La-Paz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`la-paz-line1.aln.toml`](la-paz-line1.aln.toml) | `line-1` | 30,531.4 m | 21 |
| [`la-paz-line10.aln.toml`](la-paz-line10.aln.toml) | `line-10` | 5,035.3 m | 4 |
| [`la-paz-line11.aln.toml`](la-paz-line11.aln.toml) | `line-11` | 4,461.3 m | 3 |
| [`la-paz-line12.aln.toml`](la-paz-line12.aln.toml) | `line-12` | 10,742.2 m | 7 |
| [`la-paz-line13.aln.toml`](la-paz-line13.aln.toml) | `line-13` | 4,221.9 m | 4 |
| [`la-paz-line14.aln.toml`](la-paz-line14.aln.toml) | `line-14` | 4,583.0 m | 5 |
| [`la-paz-line15.aln.toml`](la-paz-line15.aln.toml) | `line-15` | 4,018.7 m | 3 |
| [`la-paz-line16.aln.toml`](la-paz-line16.aln.toml) | `line-16` | 5,143.8 m | 5 |
| [`la-paz-line17.aln.toml`](la-paz-line17.aln.toml) | `line-17` | 7,647.7 m | 6 |
| [`la-paz-line18.aln.toml`](la-paz-line18.aln.toml) | `line-18` | 4,990.7 m | 5 |
| [`la-paz-line19.aln.toml`](la-paz-line19.aln.toml) | `line-19` | 4,368.2 m | 3 |
| [`la-paz-line2.aln.toml`](la-paz-line2.aln.toml) | `line-2` | 30,365.5 m | 20 |
| [`la-paz-line20.aln.toml`](la-paz-line20.aln.toml) | `line-20` | 12,384.5 m | 11 |
| [`la-paz-line21.aln.toml`](la-paz-line21.aln.toml) | `line-21` | 6,168.5 m | 7 |
| [`la-paz-line22.aln.toml`](la-paz-line22.aln.toml) | `line-22` | 7,177.5 m | 5 |
| [`la-paz-line23.aln.toml`](la-paz-line23.aln.toml) | `line-23` | 9,798.6 m | 7 |
| [`la-paz-line24.aln.toml`](la-paz-line24.aln.toml) | `line-24` | 9,476.9 m | 6 |
| [`la-paz-line3.aln.toml`](la-paz-line3.aln.toml) | `line-3` | 27,896.7 m | 19 |
| [`la-paz-line4.aln.toml`](la-paz-line4.aln.toml) | `line-4` | 30,317.1 m | 19 |
| [`la-paz-line5.aln.toml`](la-paz-line5.aln.toml) | `line-5` | 23,083.1 m | 16 |
| [`la-paz-line6.aln.toml`](la-paz-line6.aln.toml) | `line-6` | 53,148.4 m | 36 |
| [`la-paz-line7.aln.toml`](la-paz-line7.aln.toml) | `line-7` | 4,198.7 m | 3 |
| [`la-paz-line8.aln.toml`](la-paz-line8.aln.toml) | `line-8` | 4,866.1 m | 5 |
| [`la-paz-line9.aln.toml`](la-paz-line9.aln.toml) | `line-9` | 5,457.1 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
