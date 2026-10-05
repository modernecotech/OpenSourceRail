# Mombasa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mombasa-line1.aln.toml`](mombasa-line1.aln.toml) | `line-1` | 14,584.8 m | 8 |
| [`mombasa-line2.aln.toml`](mombasa-line2.aln.toml) | `line-2` | 22,245.9 m | 8 |
| [`mombasa-line3.aln.toml`](mombasa-line3.aln.toml) | `line-3` | 11,676.0 m | 5 |
| [`mombasa-line4.aln.toml`](mombasa-line4.aln.toml) | `line-4` | 17,320.6 m | 5 |
| [`mombasa-line5.aln.toml`](mombasa-line5.aln.toml) | `line-5` | 19,313.1 m | 8 |
| [`mombasa-line6.aln.toml`](mombasa-line6.aln.toml) | `line-6` | 52,956.3 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
