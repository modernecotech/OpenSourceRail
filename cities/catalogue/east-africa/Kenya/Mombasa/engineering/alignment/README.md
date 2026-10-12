# Mombasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mombasa-line1.aln.toml`](mombasa-line1.aln.toml) | `line-1` | 20,914.9 m | 11 |
| [`mombasa-line2.aln.toml`](mombasa-line2.aln.toml) | `line-2` | 21,594.8 m | 7 |
| [`mombasa-line3.aln.toml`](mombasa-line3.aln.toml) | `line-3` | 16,974.4 m | 14 |
| [`mombasa-line4.aln.toml`](mombasa-line4.aln.toml) | `line-4` | 63,679.3 m | 37 |
| [`mombasa-line5.aln.toml`](mombasa-line5.aln.toml) | `line-5` | 21,112.1 m | 21 |
| [`mombasa-line6.aln.toml`](mombasa-line6.aln.toml) | `line-6` | 112,932.6 m | 61 |
| [`mombasa-line7.aln.toml`](mombasa-line7.aln.toml) | `line-7` | 11,927.6 m | 3 |
| [`mombasa-line8.aln.toml`](mombasa-line8.aln.toml) | `line-8` | 5,332.4 m | 2 |
| [`mombasa-line9.aln.toml`](mombasa-line9.aln.toml) | `line-9` | 10,022.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
