# Kinshasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kinshasa-line1.aln.toml`](kinshasa-line1.aln.toml) | `line-1` | 39,726.1 m | 17 |
| [`kinshasa-line2.aln.toml`](kinshasa-line2.aln.toml) | `line-2` | 36,303.0 m | 15 |
| [`kinshasa-line3.aln.toml`](kinshasa-line3.aln.toml) | `line-3` | 33,945.8 m | 11 |
| [`kinshasa-line4.aln.toml`](kinshasa-line4.aln.toml) | `line-4` | 35,537.9 m | 13 |
| [`kinshasa-line5.aln.toml`](kinshasa-line5.aln.toml) | `line-5` | 52,817.0 m | 19 |
| [`kinshasa-line6.aln.toml`](kinshasa-line6.aln.toml) | `line-6` | 42,311.2 m | 14 |
| [`kinshasa-line7.aln.toml`](kinshasa-line7.aln.toml) | `line-7` | 41,604.8 m | 14 |
| [`kinshasa-line8.aln.toml`](kinshasa-line8.aln.toml) | `line-8` | 35,879.8 m | 11 |
| [`kinshasa-line9.aln.toml`](kinshasa-line9.aln.toml) | `line-9` | 84,007.0 m | 33 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
