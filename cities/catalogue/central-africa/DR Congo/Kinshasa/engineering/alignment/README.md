# Kinshasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kinshasa-line1.aln.toml`](kinshasa-line1.aln.toml) | `line-1` | 32,412.1 m | 13 |
| [`kinshasa-line2.aln.toml`](kinshasa-line2.aln.toml) | `line-2` | 30,636.8 m | 12 |
| [`kinshasa-line3.aln.toml`](kinshasa-line3.aln.toml) | `line-3` | 30,514.1 m | 10 |
| [`kinshasa-line4.aln.toml`](kinshasa-line4.aln.toml) | `line-4` | 26,943.3 m | 11 |
| [`kinshasa-line5.aln.toml`](kinshasa-line5.aln.toml) | `line-5` | 47,615.4 m | 15 |
| [`kinshasa-line6.aln.toml`](kinshasa-line6.aln.toml) | `line-6` | 38,864.1 m | 13 |
| [`kinshasa-line7.aln.toml`](kinshasa-line7.aln.toml) | `line-7` | 37,289.8 m | 12 |
| [`kinshasa-line8.aln.toml`](kinshasa-line8.aln.toml) | `line-8` | 34,492.0 m | 10 |
| [`kinshasa-line9.aln.toml`](kinshasa-line9.aln.toml) | `line-9` | 73,490.1 m | 24 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
