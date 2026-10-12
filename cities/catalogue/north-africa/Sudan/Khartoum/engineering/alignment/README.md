# Khartoum Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khartoum-line1.aln.toml`](khartoum-line1.aln.toml) | `line-1` | 43,391.5 m | 19 |
| [`khartoum-line10.aln.toml`](khartoum-line10.aln.toml) | `line-10` | 7,684.1 m | 3 |
| [`khartoum-line11.aln.toml`](khartoum-line11.aln.toml) | `line-11` | 6,744.2 m | 2 |
| [`khartoum-line12.aln.toml`](khartoum-line12.aln.toml) | `line-12` | 6,123.9 m | 2 |
| [`khartoum-line13.aln.toml`](khartoum-line13.aln.toml) | `line-13` | 7,172.7 m | 3 |
| [`khartoum-line14.aln.toml`](khartoum-line14.aln.toml) | `line-14` | 6,599.9 m | 2 |
| [`khartoum-line2.aln.toml`](khartoum-line2.aln.toml) | `line-2` | 36,067.7 m | 19 |
| [`khartoum-line3.aln.toml`](khartoum-line3.aln.toml) | `line-3` | 58,657.5 m | 16 |
| [`khartoum-line4.aln.toml`](khartoum-line4.aln.toml) | `line-4` | 25,381.0 m | 15 |
| [`khartoum-line5.aln.toml`](khartoum-line5.aln.toml) | `line-5` | 44,025.7 m | 19 |
| [`khartoum-line6.aln.toml`](khartoum-line6.aln.toml) | `line-6` | 34,242.4 m | 11 |
| [`khartoum-line7.aln.toml`](khartoum-line7.aln.toml) | `line-7` | 43,160.0 m | 20 |
| [`khartoum-line8.aln.toml`](khartoum-line8.aln.toml) | `line-8` | 30,073.5 m | 9 |
| [`khartoum-line9.aln.toml`](khartoum-line9.aln.toml) | `line-9` | 118,730.7 m | 41 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
