# Kinshasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kinshasa-line1.aln.toml`](kinshasa-line1.aln.toml) | `line-1` | 62,822.2 m | 77 |
| [`kinshasa-line10.aln.toml`](kinshasa-line10.aln.toml) | `line-10` | 6,315.8 m | 7 |
| [`kinshasa-line11.aln.toml`](kinshasa-line11.aln.toml) | `line-11` | 6,345.2 m | 5 |
| [`kinshasa-line12.aln.toml`](kinshasa-line12.aln.toml) | `line-12` | 6,269.6 m | 6 |
| [`kinshasa-line13.aln.toml`](kinshasa-line13.aln.toml) | `line-13` | 9,666.2 m | 8 |
| [`kinshasa-line14.aln.toml`](kinshasa-line14.aln.toml) | `line-14` | 7,476.7 m | 5 |
| [`kinshasa-line15.aln.toml`](kinshasa-line15.aln.toml) | `line-15` | 7,902.9 m | 5 |
| [`kinshasa-line16.aln.toml`](kinshasa-line16.aln.toml) | `line-16` | 7,764.4 m | 9 |
| [`kinshasa-line17.aln.toml`](kinshasa-line17.aln.toml) | `line-17` | 6,554.7 m | 7 |
| [`kinshasa-line18.aln.toml`](kinshasa-line18.aln.toml) | `line-18` | 8,680.3 m | 5 |
| [`kinshasa-line19.aln.toml`](kinshasa-line19.aln.toml) | `line-19` | 13,168.4 m | 8 |
| [`kinshasa-line2.aln.toml`](kinshasa-line2.aln.toml) | `line-2` | 66,911.7 m | 77 |
| [`kinshasa-line20.aln.toml`](kinshasa-line20.aln.toml) | `line-20` | 6,289.0 m | 4 |
| [`kinshasa-line3.aln.toml`](kinshasa-line3.aln.toml) | `line-3` | 31,844.7 m | 37 |
| [`kinshasa-line4.aln.toml`](kinshasa-line4.aln.toml) | `line-4` | 64,091.9 m | 72 |
| [`kinshasa-line5.aln.toml`](kinshasa-line5.aln.toml) | `line-5` | 48,631.2 m | 29 |
| [`kinshasa-line6.aln.toml`](kinshasa-line6.aln.toml) | `line-6` | 49,320.8 m | 61 |
| [`kinshasa-line7.aln.toml`](kinshasa-line7.aln.toml) | `line-7` | 91,682.6 m | 74 |
| [`kinshasa-line8.aln.toml`](kinshasa-line8.aln.toml) | `line-8` | 35,992.8 m | 26 |
| [`kinshasa-line9.aln.toml`](kinshasa-line9.aln.toml) | `line-9` | 106,678.7 m | 109 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
