# Agra Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`agra-line1.aln.toml`](agra-line1.aln.toml) | `line-1` | 23,285.7 m | 15 |
| [`agra-line2.aln.toml`](agra-line2.aln.toml) | `line-2` | 23,989.3 m | 13 |
| [`agra-line3.aln.toml`](agra-line3.aln.toml) | `line-3` | 22,575.1 m | 15 |
| [`agra-line4.aln.toml`](agra-line4.aln.toml) | `line-4` | 30,703.8 m | 19 |
| [`agra-line5.aln.toml`](agra-line5.aln.toml) | `line-5` | 59,663.9 m | 36 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
