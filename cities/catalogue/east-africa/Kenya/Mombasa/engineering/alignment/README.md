# Mombasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mombasa-line1.aln.toml`](mombasa-line1.aln.toml) | `line-1` | 34,485.4 m | 22 |
| [`mombasa-line10.aln.toml`](mombasa-line10.aln.toml) | `line-10` | 7,318.7 m | 6 |
| [`mombasa-line11.aln.toml`](mombasa-line11.aln.toml) | `line-11` | 8,148.2 m | 7 |
| [`mombasa-line12.aln.toml`](mombasa-line12.aln.toml) | `line-12` | 10,329.8 m | 8 |
| [`mombasa-line13.aln.toml`](mombasa-line13.aln.toml) | `line-13` | 8,341.1 m | 7 |
| [`mombasa-line14.aln.toml`](mombasa-line14.aln.toml) | `line-14` | 6,736.6 m | 6 |
| [`mombasa-line15.aln.toml`](mombasa-line15.aln.toml) | `line-15` | 10,501.0 m | 7 |
| [`mombasa-line16.aln.toml`](mombasa-line16.aln.toml) | `line-16` | 10,890.2 m | 8 |
| [`mombasa-line17.aln.toml`](mombasa-line17.aln.toml) | `line-17` | 7,128.1 m | 7 |
| [`mombasa-line2.aln.toml`](mombasa-line2.aln.toml) | `line-2` | 21,594.8 m | 15 |
| [`mombasa-line3.aln.toml`](mombasa-line3.aln.toml) | `line-3` | 17,014.4 m | 23 |
| [`mombasa-line4.aln.toml`](mombasa-line4.aln.toml) | `line-4` | 61,464.7 m | 42 |
| [`mombasa-line5.aln.toml`](mombasa-line5.aln.toml) | `line-5` | 18,545.4 m | 18 |
| [`mombasa-line6.aln.toml`](mombasa-line6.aln.toml) | `line-6` | 112,932.6 m | 81 |
| [`mombasa-line7.aln.toml`](mombasa-line7.aln.toml) | `line-7` | 5,568.9 m | 4 |
| [`mombasa-line8.aln.toml`](mombasa-line8.aln.toml) | `line-8` | 5,421.1 m | 5 |
| [`mombasa-line9.aln.toml`](mombasa-line9.aln.toml) | `line-9` | 6,563.2 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
