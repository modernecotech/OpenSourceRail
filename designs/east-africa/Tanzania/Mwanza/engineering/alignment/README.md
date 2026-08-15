# Mwanza Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mwanza-line1.aln.toml`](mwanza-line1.aln.toml) | `line-1` | 25,590.2 m | 19 |
| [`mwanza-line2.aln.toml`](mwanza-line2.aln.toml) | `line-2` | 22,974.7 m | 16 |
| [`mwanza-line3.aln.toml`](mwanza-line3.aln.toml) | `line-3` | 18,299.0 m | 11 |
| [`mwanza-line4.aln.toml`](mwanza-line4.aln.toml) | `line-4` | 25,960.3 m | 16 |
| [`mwanza-line5.aln.toml`](mwanza-line5.aln.toml) | `line-5` | 29,878.5 m | 16 |
| [`mwanza-line6.aln.toml`](mwanza-line6.aln.toml) | `line-6` | 53,214.5 m | 35 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
