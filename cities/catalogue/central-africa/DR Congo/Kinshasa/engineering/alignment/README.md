# Kinshasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kinshasa-line1.aln.toml`](kinshasa-line1.aln.toml) | `line-1` | 62,617.3 m | 85 |
| [`kinshasa-line10.aln.toml`](kinshasa-line10.aln.toml) | `line-10` | 6,394.1 m | 3 |
| [`kinshasa-line11.aln.toml`](kinshasa-line11.aln.toml) | `line-11` | 6,518.1 m | 3 |
| [`kinshasa-line12.aln.toml`](kinshasa-line12.aln.toml) | `line-12` | 6,542.1 m | 2 |
| [`kinshasa-line13.aln.toml`](kinshasa-line13.aln.toml) | `line-13` | 7,386.7 m | 4 |
| [`kinshasa-line14.aln.toml`](kinshasa-line14.aln.toml) | `line-14` | 6,323.8 m | 2 |
| [`kinshasa-line2.aln.toml`](kinshasa-line2.aln.toml) | `line-2` | 71,493.0 m | 86 |
| [`kinshasa-line3.aln.toml`](kinshasa-line3.aln.toml) | `line-3` | 31,844.7 m | 29 |
| [`kinshasa-line4.aln.toml`](kinshasa-line4.aln.toml) | `line-4` | 61,664.0 m | 72 |
| [`kinshasa-line5.aln.toml`](kinshasa-line5.aln.toml) | `line-5` | 55,130.1 m | 60 |
| [`kinshasa-line6.aln.toml`](kinshasa-line6.aln.toml) | `line-6` | 70,011.1 m | 40 |
| [`kinshasa-line7.aln.toml`](kinshasa-line7.aln.toml) | `line-7` | 91,767.8 m | 87 |
| [`kinshasa-line8.aln.toml`](kinshasa-line8.aln.toml) | `line-8` | 36,680.1 m | 16 |
| [`kinshasa-line9.aln.toml`](kinshasa-line9.aln.toml) | `line-9` | 125,475.5 m | 128 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
