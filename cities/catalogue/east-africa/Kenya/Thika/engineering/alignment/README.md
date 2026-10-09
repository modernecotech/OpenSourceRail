# Thika Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`thika-line1.aln.toml`](thika-line1.aln.toml) | `line-1` | 26,108.8 m | 16 |
| [`thika-line10.aln.toml`](thika-line10.aln.toml) | `line-10` | 2,579.4 m | 2 |
| [`thika-line11.aln.toml`](thika-line11.aln.toml) | `line-11` | 13,637.7 m | 8 |
| [`thika-line12.aln.toml`](thika-line12.aln.toml) | `line-12` | 3,129.8 m | 2 |
| [`thika-line13.aln.toml`](thika-line13.aln.toml) | `line-13` | 12,343.6 m | 8 |
| [`thika-line14.aln.toml`](thika-line14.aln.toml) | `line-14` | 2,209.4 m | 3 |
| [`thika-line15.aln.toml`](thika-line15.aln.toml) | `line-15` | 12,113.9 m | 6 |
| [`thika-line2.aln.toml`](thika-line2.aln.toml) | `line-2` | 18,324.1 m | 12 |
| [`thika-line3.aln.toml`](thika-line3.aln.toml) | `line-3` | 23,755.4 m | 14 |
| [`thika-line4.aln.toml`](thika-line4.aln.toml) | `line-4` | 2,268.5 m | 2 |
| [`thika-line5.aln.toml`](thika-line5.aln.toml) | `line-5` | 5,287.5 m | 4 |
| [`thika-line6.aln.toml`](thika-line6.aln.toml) | `line-6` | 2,539.7 m | 2 |
| [`thika-line7.aln.toml`](thika-line7.aln.toml) | `line-7` | 3,044.5 m | 3 |
| [`thika-line8.aln.toml`](thika-line8.aln.toml) | `line-8` | 2,928.8 m | 2 |
| [`thika-line9.aln.toml`](thika-line9.aln.toml) | `line-9` | 4,565.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
