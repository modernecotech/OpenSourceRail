# Kanpur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kanpur-line1.aln.toml`](kanpur-line1.aln.toml) | `line-1` | 25,010.1 m | 11 |
| [`kanpur-line2.aln.toml`](kanpur-line2.aln.toml) | `line-2` | 25,039.4 m | 11 |
| [`kanpur-line3.aln.toml`](kanpur-line3.aln.toml) | `line-3` | 64,550.6 m | 31 |
| [`kanpur-line4.aln.toml`](kanpur-line4.aln.toml) | `line-4` | 38,471.4 m | 15 |
| [`kanpur-line5.aln.toml`](kanpur-line5.aln.toml) | `line-5` | 26,489.2 m | 11 |
| [`kanpur-line6.aln.toml`](kanpur-line6.aln.toml) | `line-6` | 45,945.8 m | 14 |
| [`kanpur-line7.aln.toml`](kanpur-line7.aln.toml) | `line-7` | 20,602.2 m | 9 |
| [`kanpur-line8.aln.toml`](kanpur-line8.aln.toml) | `line-8` | 112,968.9 m | 42 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
