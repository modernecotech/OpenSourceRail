# Huambo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`huambo-line1.aln.toml`](huambo-line1.aln.toml) | `line-1` | 19,276.9 m | 13 |
| [`huambo-line10.aln.toml`](huambo-line10.aln.toml) | `line-10` | 2,486.3 m | 2 |
| [`huambo-line11.aln.toml`](huambo-line11.aln.toml) | `line-11` | 2,532.8 m | 2 |
| [`huambo-line12.aln.toml`](huambo-line12.aln.toml) | `line-12` | 3,907.6 m | 3 |
| [`huambo-line13.aln.toml`](huambo-line13.aln.toml) | `line-13` | 2,165.1 m | 2 |
| [`huambo-line2.aln.toml`](huambo-line2.aln.toml) | `line-2` | 9,957.4 m | 7 |
| [`huambo-line3.aln.toml`](huambo-line3.aln.toml) | `line-3` | 13,609.5 m | 10 |
| [`huambo-line4.aln.toml`](huambo-line4.aln.toml) | `line-4` | 4,570.2 m | 3 |
| [`huambo-line5.aln.toml`](huambo-line5.aln.toml) | `line-5` | 2,717.1 m | 2 |
| [`huambo-line6.aln.toml`](huambo-line6.aln.toml) | `line-6` | 7,444.4 m | 5 |
| [`huambo-line7.aln.toml`](huambo-line7.aln.toml) | `line-7` | 2,156.8 m | 2 |
| [`huambo-line8.aln.toml`](huambo-line8.aln.toml) | `line-8` | 8,924.5 m | 6 |
| [`huambo-line9.aln.toml`](huambo-line9.aln.toml) | `line-9` | 5,787.8 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
