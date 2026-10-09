# Mandalay Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mandalay-line1.aln.toml`](mandalay-line1.aln.toml) | `line-1` | 38,333.2 m | 23 |
| [`mandalay-line10.aln.toml`](mandalay-line10.aln.toml) | `line-10` | 7,986.1 m | 6 |
| [`mandalay-line11.aln.toml`](mandalay-line11.aln.toml) | `line-11` | 10,606.9 m | 7 |
| [`mandalay-line12.aln.toml`](mandalay-line12.aln.toml) | `line-12` | 6,660.7 m | 6 |
| [`mandalay-line13.aln.toml`](mandalay-line13.aln.toml) | `line-13` | 12,070.6 m | 9 |
| [`mandalay-line14.aln.toml`](mandalay-line14.aln.toml) | `line-14` | 9,112.8 m | 6 |
| [`mandalay-line15.aln.toml`](mandalay-line15.aln.toml) | `line-15` | 5,432.7 m | 4 |
| [`mandalay-line16.aln.toml`](mandalay-line16.aln.toml) | `line-16` | 9,151.9 m | 6 |
| [`mandalay-line17.aln.toml`](mandalay-line17.aln.toml) | `line-17` | 4,795.6 m | 4 |
| [`mandalay-line18.aln.toml`](mandalay-line18.aln.toml) | `line-18` | 4,672.4 m | 4 |
| [`mandalay-line19.aln.toml`](mandalay-line19.aln.toml) | `line-19` | 5,874.2 m | 6 |
| [`mandalay-line2.aln.toml`](mandalay-line2.aln.toml) | `line-2` | 30,801.1 m | 20 |
| [`mandalay-line20.aln.toml`](mandalay-line20.aln.toml) | `line-20` | 8,474.7 m | 6 |
| [`mandalay-line3.aln.toml`](mandalay-line3.aln.toml) | `line-3` | 33,776.6 m | 21 |
| [`mandalay-line4.aln.toml`](mandalay-line4.aln.toml) | `line-4` | 21,760.1 m | 15 |
| [`mandalay-line5.aln.toml`](mandalay-line5.aln.toml) | `line-5` | 23,366.3 m | 14 |
| [`mandalay-line6.aln.toml`](mandalay-line6.aln.toml) | `line-6` | 84,921.0 m | 51 |
| [`mandalay-line7.aln.toml`](mandalay-line7.aln.toml) | `line-7` | 7,030.6 m | 5 |
| [`mandalay-line8.aln.toml`](mandalay-line8.aln.toml) | `line-8` | 4,881.1 m | 4 |
| [`mandalay-line9.aln.toml`](mandalay-line9.aln.toml) | `line-9` | 5,077.3 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
