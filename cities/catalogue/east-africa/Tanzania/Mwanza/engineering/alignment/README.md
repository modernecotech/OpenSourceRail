# Mwanza Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mwanza-line1.aln.toml`](mwanza-line1.aln.toml) | `line-1` | 18,012.2 m | 16 |
| [`mwanza-line10.aln.toml`](mwanza-line10.aln.toml) | `line-10` | 4,269.8 m | 3 |
| [`mwanza-line11.aln.toml`](mwanza-line11.aln.toml) | `line-11` | 5,121.3 m | 4 |
| [`mwanza-line12.aln.toml`](mwanza-line12.aln.toml) | `line-12` | 8,815.8 m | 5 |
| [`mwanza-line13.aln.toml`](mwanza-line13.aln.toml) | `line-13` | 7,801.8 m | 5 |
| [`mwanza-line14.aln.toml`](mwanza-line14.aln.toml) | `line-14` | 4,137.3 m | 4 |
| [`mwanza-line15.aln.toml`](mwanza-line15.aln.toml) | `line-15` | 8,946.5 m | 6 |
| [`mwanza-line16.aln.toml`](mwanza-line16.aln.toml) | `line-16` | 4,427.7 m | 4 |
| [`mwanza-line17.aln.toml`](mwanza-line17.aln.toml) | `line-17` | 4,934.6 m | 4 |
| [`mwanza-line18.aln.toml`](mwanza-line18.aln.toml) | `line-18` | 6,172.3 m | 4 |
| [`mwanza-line19.aln.toml`](mwanza-line19.aln.toml) | `line-19` | 6,402.1 m | 6 |
| [`mwanza-line2.aln.toml`](mwanza-line2.aln.toml) | `line-2` | 35,086.0 m | 25 |
| [`mwanza-line20.aln.toml`](mwanza-line20.aln.toml) | `line-20` | 10,975.5 m | 7 |
| [`mwanza-line3.aln.toml`](mwanza-line3.aln.toml) | `line-3` | 37,195.0 m | 30 |
| [`mwanza-line4.aln.toml`](mwanza-line4.aln.toml) | `line-4` | 18,975.1 m | 17 |
| [`mwanza-line5.aln.toml`](mwanza-line5.aln.toml) | `line-5` | 26,002.0 m | 22 |
| [`mwanza-line6.aln.toml`](mwanza-line6.aln.toml) | `line-6` | 42,059.4 m | 28 |
| [`mwanza-line7.aln.toml`](mwanza-line7.aln.toml) | `line-7` | 3,601.3 m | 3 |
| [`mwanza-line8.aln.toml`](mwanza-line8.aln.toml) | `line-8` | 3,854.8 m | 4 |
| [`mwanza-line9.aln.toml`](mwanza-line9.aln.toml) | `line-9` | 7,242.4 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
