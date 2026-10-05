# Mwanza Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mwanza-line1.aln.toml`](mwanza-line1.aln.toml) | `line-1` | 18,376.1 m | 7 |
| [`mwanza-line2.aln.toml`](mwanza-line2.aln.toml) | `line-2` | 19,945.4 m | 8 |
| [`mwanza-line3.aln.toml`](mwanza-line3.aln.toml) | `line-3` | 16,066.1 m | 6 |
| [`mwanza-line4.aln.toml`](mwanza-line4.aln.toml) | `line-4` | 23,828.5 m | 9 |
| [`mwanza-line5.aln.toml`](mwanza-line5.aln.toml) | `line-5` | 25,430.2 m | 9 |
| [`mwanza-line6.aln.toml`](mwanza-line6.aln.toml) | `line-6` | 42,059.4 m | 14 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
