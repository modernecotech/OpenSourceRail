# Beirut Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`beirut-line1.aln.toml`](beirut-line1.aln.toml) | `line-1` | 30,967.0 m | 11 |
| [`beirut-line2.aln.toml`](beirut-line2.aln.toml) | `line-2` | 13,721.4 m | 8 |
| [`beirut-line3.aln.toml`](beirut-line3.aln.toml) | `line-3` | 17,383.2 m | 8 |
| [`beirut-line4.aln.toml`](beirut-line4.aln.toml) | `line-4` | 15,894.6 m | 8 |
| [`beirut-line5.aln.toml`](beirut-line5.aln.toml) | `line-5` | 15,455.2 m | 8 |
| [`beirut-line6.aln.toml`](beirut-line6.aln.toml) | `line-6` | 28,820.5 m | 12 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
