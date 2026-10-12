# Karbala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karbala-line1.aln.toml`](karbala-line1.aln.toml) | `line-1` | 23,575.8 m | 8 |
| [`karbala-line2.aln.toml`](karbala-line2.aln.toml) | `line-2` | 17,996.4 m | 8 |
| [`karbala-line3.aln.toml`](karbala-line3.aln.toml) | `line-3` | 19,230.8 m | 8 |
| [`karbala-line4.aln.toml`](karbala-line4.aln.toml) | `line-4` | 21,934.3 m | 7 |
| [`karbala-line5.aln.toml`](karbala-line5.aln.toml) | `line-5` | 25,184.2 m | 11 |
| [`karbala-line6.aln.toml`](karbala-line6.aln.toml) | `line-6` | 56,571.2 m | 18 |
| [`karbala-line7.aln.toml`](karbala-line7.aln.toml) | `line-7` | 4,143.3 m | 2 |
| [`karbala-line8.aln.toml`](karbala-line8.aln.toml) | `line-8` | 7,789.5 m | 4 |
| [`karbala-line9.aln.toml`](karbala-line9.aln.toml) | `line-9` | 7,994.6 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
