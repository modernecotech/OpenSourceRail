# Karbala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karbala-line1.aln.toml`](karbala-line1.aln.toml) | `line-1` | 23,564.1 m | 9 |
| [`karbala-line2.aln.toml`](karbala-line2.aln.toml) | `line-2` | 18,141.3 m | 7 |
| [`karbala-line3.aln.toml`](karbala-line3.aln.toml) | `line-3` | 16,326.7 m | 6 |
| [`karbala-line4.aln.toml`](karbala-line4.aln.toml) | `line-4` | 18,421.5 m | 7 |
| [`karbala-line5.aln.toml`](karbala-line5.aln.toml) | `line-5` | 21,951.7 m | 9 |
| [`karbala-line6.aln.toml`](karbala-line6.aln.toml) | `line-6` | 56,571.2 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
