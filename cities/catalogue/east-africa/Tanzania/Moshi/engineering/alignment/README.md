# Moshi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`moshi-line1.aln.toml`](moshi-line1.aln.toml) | `line-1` | 12,200.3 m | 8 |
| [`moshi-line2.aln.toml`](moshi-line2.aln.toml) | `line-2` | 9,119.9 m | 6 |
| [`moshi-line3.aln.toml`](moshi-line3.aln.toml) | `line-3` | 6,941.1 m | 7 |
| [`moshi-line4.aln.toml`](moshi-line4.aln.toml) | `line-4` | 2,450.8 m | 2 |
| [`moshi-line5.aln.toml`](moshi-line5.aln.toml) | `line-5` | 3,268.8 m | 3 |
| [`moshi-line6.aln.toml`](moshi-line6.aln.toml) | `line-6` | 3,670.8 m | 3 |
| [`moshi-line7.aln.toml`](moshi-line7.aln.toml) | `line-7` | 6,203.1 m | 4 |
| [`moshi-line8.aln.toml`](moshi-line8.aln.toml) | `line-8` | 2,827.1 m | 2 |
| [`moshi-line9.aln.toml`](moshi-line9.aln.toml) | `line-9` | 8,391.7 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
