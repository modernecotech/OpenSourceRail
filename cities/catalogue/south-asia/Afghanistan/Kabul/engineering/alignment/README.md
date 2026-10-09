# Kabul Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kabul-line1.aln.toml`](kabul-line1.aln.toml) | `line-1` | 23,499.3 m | 18 |
| [`kabul-line10.aln.toml`](kabul-line10.aln.toml) | `line-10` | 4,860.1 m | 4 |
| [`kabul-line11.aln.toml`](kabul-line11.aln.toml) | `line-11` | 5,417.9 m | 4 |
| [`kabul-line12.aln.toml`](kabul-line12.aln.toml) | `line-12` | 7,621.3 m | 6 |
| [`kabul-line13.aln.toml`](kabul-line13.aln.toml) | `line-13` | 4,593.9 m | 3 |
| [`kabul-line14.aln.toml`](kabul-line14.aln.toml) | `line-14` | 5,026.4 m | 4 |
| [`kabul-line15.aln.toml`](kabul-line15.aln.toml) | `line-15` | 3,940.0 m | 3 |
| [`kabul-line16.aln.toml`](kabul-line16.aln.toml) | `line-16` | 4,467.9 m | 4 |
| [`kabul-line17.aln.toml`](kabul-line17.aln.toml) | `line-17` | 9,994.9 m | 6 |
| [`kabul-line18.aln.toml`](kabul-line18.aln.toml) | `line-18` | 4,252.4 m | 5 |
| [`kabul-line19.aln.toml`](kabul-line19.aln.toml) | `line-19` | 5,007.9 m | 3 |
| [`kabul-line2.aln.toml`](kabul-line2.aln.toml) | `line-2` | 26,115.9 m | 16 |
| [`kabul-line20.aln.toml`](kabul-line20.aln.toml) | `line-20` | 11,553.7 m | 7 |
| [`kabul-line21.aln.toml`](kabul-line21.aln.toml) | `line-21` | 6,123.9 m | 4 |
| [`kabul-line22.aln.toml`](kabul-line22.aln.toml) | `line-22` | 9,586.4 m | 6 |
| [`kabul-line3.aln.toml`](kabul-line3.aln.toml) | `line-3` | 18,511.2 m | 14 |
| [`kabul-line4.aln.toml`](kabul-line4.aln.toml) | `line-4` | 26,025.9 m | 16 |
| [`kabul-line5.aln.toml`](kabul-line5.aln.toml) | `line-5` | 29,103.9 m | 19 |
| [`kabul-line6.aln.toml`](kabul-line6.aln.toml) | `line-6` | 18,502.3 m | 11 |
| [`kabul-line7.aln.toml`](kabul-line7.aln.toml) | `line-7` | 53,040.2 m | 33 |
| [`kabul-line8.aln.toml`](kabul-line8.aln.toml) | `line-8` | 5,056.1 m | 4 |
| [`kabul-line9.aln.toml`](kabul-line9.aln.toml) | `line-9` | 5,002.2 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
