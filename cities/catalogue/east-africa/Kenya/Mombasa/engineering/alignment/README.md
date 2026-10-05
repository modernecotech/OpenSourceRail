# Mombasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mombasa-line1.aln.toml`](mombasa-line1.aln.toml) | `line-1` | 34,485.4 m | 16 |
| [`mombasa-line2.aln.toml`](mombasa-line2.aln.toml) | `line-2` | 21,594.8 m | 8 |
| [`mombasa-line3.aln.toml`](mombasa-line3.aln.toml) | `line-3` | 17,014.4 m | 20 |
| [`mombasa-line4.aln.toml`](mombasa-line4.aln.toml) | `line-4` | 61,464.7 m | 34 |
| [`mombasa-line5.aln.toml`](mombasa-line5.aln.toml) | `line-5` | 18,562.0 m | 15 |
| [`mombasa-line6.aln.toml`](mombasa-line6.aln.toml) | `line-6` | 113,012.6 m | 51 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
