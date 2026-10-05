# Kinshasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kinshasa-line1.aln.toml`](kinshasa-line1.aln.toml) | `line-1` | 62,822.2 m | 70 |
| [`kinshasa-line2.aln.toml`](kinshasa-line2.aln.toml) | `line-2` | 66,911.7 m | 74 |
| [`kinshasa-line3.aln.toml`](kinshasa-line3.aln.toml) | `line-3` | 31,844.7 m | 32 |
| [`kinshasa-line4.aln.toml`](kinshasa-line4.aln.toml) | `line-4` | 64,091.9 m | 68 |
| [`kinshasa-line5.aln.toml`](kinshasa-line5.aln.toml) | `line-5` | 48,631.2 m | 20 |
| [`kinshasa-line6.aln.toml`](kinshasa-line6.aln.toml) | `line-6` | 49,382.3 m | 53 |
| [`kinshasa-line7.aln.toml`](kinshasa-line7.aln.toml) | `line-7` | 91,682.6 m | 55 |
| [`kinshasa-line8.aln.toml`](kinshasa-line8.aln.toml) | `line-8` | 35,992.8 m | 16 |
| [`kinshasa-line9.aln.toml`](kinshasa-line9.aln.toml) | `line-9` | 106,678.7 m | 95 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
