# Mwanza Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mwanza-line1.aln.toml`](mwanza-line1.aln.toml) | `line-1` | 17,819.1 m | 8 |
| [`mwanza-line2.aln.toml`](mwanza-line2.aln.toml) | `line-2` | 24,197.5 m | 13 |
| [`mwanza-line3.aln.toml`](mwanza-line3.aln.toml) | `line-3` | 27,441.9 m | 13 |
| [`mwanza-line4.aln.toml`](mwanza-line4.aln.toml) | `line-4` | 18,975.1 m | 10 |
| [`mwanza-line5.aln.toml`](mwanza-line5.aln.toml) | `line-5` | 26,002.0 m | 10 |
| [`mwanza-line6.aln.toml`](mwanza-line6.aln.toml) | `line-6` | 56,079.3 m | 20 |
| [`mwanza-line7.aln.toml`](mwanza-line7.aln.toml) | `line-7` | 4,856.5 m | 2 |
| [`mwanza-line8.aln.toml`](mwanza-line8.aln.toml) | `line-8` | 18,670.7 m | 10 |
| [`mwanza-line9.aln.toml`](mwanza-line9.aln.toml) | `line-9` | 5,500.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
