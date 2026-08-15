# Kanpur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kanpur-line1.aln.toml`](kanpur-line1.aln.toml) | `line-1` | 27,324.8 m | 17 |
| [`kanpur-line2.aln.toml`](kanpur-line2.aln.toml) | `line-2` | 29,122.9 m | 18 |
| [`kanpur-line3.aln.toml`](kanpur-line3.aln.toml) | `line-3` | 51,835.8 m | 26 |
| [`kanpur-line4.aln.toml`](kanpur-line4.aln.toml) | `line-4` | 43,076.2 m | 25 |
| [`kanpur-line5.aln.toml`](kanpur-line5.aln.toml) | `line-5` | 32,355.1 m | 19 |
| [`kanpur-line6.aln.toml`](kanpur-line6.aln.toml) | `line-6` | 51,378.3 m | 29 |
| [`kanpur-line7.aln.toml`](kanpur-line7.aln.toml) | `line-7` | 23,254.6 m | 12 |
| [`kanpur-line8.aln.toml`](kanpur-line8.aln.toml) | `line-8` | 94,172.0 m | 57 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
