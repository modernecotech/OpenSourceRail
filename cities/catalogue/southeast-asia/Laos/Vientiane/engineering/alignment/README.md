# Vientiane Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`vientiane-line1.aln.toml`](vientiane-line1.aln.toml) | `line-1` | 17,936.4 m | 12 |
| [`vientiane-line10.aln.toml`](vientiane-line10.aln.toml) | `line-10` | 13,333.8 m | 7 |
| [`vientiane-line11.aln.toml`](vientiane-line11.aln.toml) | `line-11` | 4,645.9 m | 3 |
| [`vientiane-line12.aln.toml`](vientiane-line12.aln.toml) | `line-12` | 2,050.8 m | 2 |
| [`vientiane-line13.aln.toml`](vientiane-line13.aln.toml) | `line-13` | 2,624.5 m | 2 |
| [`vientiane-line14.aln.toml`](vientiane-line14.aln.toml) | `line-14` | 3,801.6 m | 3 |
| [`vientiane-line15.aln.toml`](vientiane-line15.aln.toml) | `line-15` | 3,297.4 m | 3 |
| [`vientiane-line16.aln.toml`](vientiane-line16.aln.toml) | `line-16` | 2,175.6 m | 2 |
| [`vientiane-line2.aln.toml`](vientiane-line2.aln.toml) | `line-2` | 19,075.5 m | 12 |
| [`vientiane-line3.aln.toml`](vientiane-line3.aln.toml) | `line-3` | 25,118.7 m | 17 |
| [`vientiane-line4.aln.toml`](vientiane-line4.aln.toml) | `line-4` | 2,932.8 m | 2 |
| [`vientiane-line5.aln.toml`](vientiane-line5.aln.toml) | `line-5` | 6,022.7 m | 3 |
| [`vientiane-line6.aln.toml`](vientiane-line6.aln.toml) | `line-6` | 5,842.8 m | 4 |
| [`vientiane-line7.aln.toml`](vientiane-line7.aln.toml) | `line-7` | 2,653.0 m | 3 |
| [`vientiane-line8.aln.toml`](vientiane-line8.aln.toml) | `line-8` | 9,728.8 m | 6 |
| [`vientiane-line9.aln.toml`](vientiane-line9.aln.toml) | `line-9` | 2,763.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
