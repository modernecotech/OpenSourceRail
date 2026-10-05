# Karbala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karbala-line1.aln.toml`](karbala-line1.aln.toml) | `line-1` | 23,341.0 m | 9 |
| [`karbala-line2.aln.toml`](karbala-line2.aln.toml) | `line-2` | 18,246.1 m | 7 |
| [`karbala-line3.aln.toml`](karbala-line3.aln.toml) | `line-3` | 16,839.8 m | 5 |
| [`karbala-line4.aln.toml`](karbala-line4.aln.toml) | `line-4` | 18,131.2 m | 7 |
| [`karbala-line5.aln.toml`](karbala-line5.aln.toml) | `line-5` | 21,934.4 m | 6 |
| [`karbala-line6.aln.toml`](karbala-line6.aln.toml) | `line-6` | 55,552.2 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
