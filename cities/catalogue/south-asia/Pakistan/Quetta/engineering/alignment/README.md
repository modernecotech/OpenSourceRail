# Quetta Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`quetta-line1.aln.toml`](quetta-line1.aln.toml) | `line-1` | 20,784.9 m | 13 |
| [`quetta-line10.aln.toml`](quetta-line10.aln.toml) | `line-10` | 2,821.9 m | 2 |
| [`quetta-line11.aln.toml`](quetta-line11.aln.toml) | `line-11` | 6,400.1 m | 4 |
| [`quetta-line12.aln.toml`](quetta-line12.aln.toml) | `line-12` | 2,759.7 m | 2 |
| [`quetta-line13.aln.toml`](quetta-line13.aln.toml) | `line-13` | 3,634.2 m | 3 |
| [`quetta-line14.aln.toml`](quetta-line14.aln.toml) | `line-14` | 5,198.8 m | 4 |
| [`quetta-line15.aln.toml`](quetta-line15.aln.toml) | `line-15` | 2,318.5 m | 2 |
| [`quetta-line16.aln.toml`](quetta-line16.aln.toml) | `line-16` | 3,865.0 m | 6 |
| [`quetta-line17.aln.toml`](quetta-line17.aln.toml) | `line-17` | 3,001.9 m | 4 |
| [`quetta-line18.aln.toml`](quetta-line18.aln.toml) | `line-18` | 2,777.6 m | 2 |
| [`quetta-line19.aln.toml`](quetta-line19.aln.toml) | `line-19` | 3,087.4 m | 3 |
| [`quetta-line2.aln.toml`](quetta-line2.aln.toml) | `line-2` | 21,215.1 m | 14 |
| [`quetta-line20.aln.toml`](quetta-line20.aln.toml) | `line-20` | 6,289.6 m | 6 |
| [`quetta-line21.aln.toml`](quetta-line21.aln.toml) | `line-21` | 4,949.6 m | 3 |
| [`quetta-line22.aln.toml`](quetta-line22.aln.toml) | `line-22` | 2,352.5 m | 2 |
| [`quetta-line3.aln.toml`](quetta-line3.aln.toml) | `line-3` | 12,002.6 m | 7 |
| [`quetta-line4.aln.toml`](quetta-line4.aln.toml) | `line-4` | 49,607.7 m | 28 |
| [`quetta-line5.aln.toml`](quetta-line5.aln.toml) | `line-5` | 4,203.9 m | 3 |
| [`quetta-line6.aln.toml`](quetta-line6.aln.toml) | `line-6` | 4,625.6 m | 5 |
| [`quetta-line7.aln.toml`](quetta-line7.aln.toml) | `line-7` | 4,135.3 m | 4 |
| [`quetta-line8.aln.toml`](quetta-line8.aln.toml) | `line-8` | 3,831.6 m | 3 |
| [`quetta-line9.aln.toml`](quetta-line9.aln.toml) | `line-9` | 3,756.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
