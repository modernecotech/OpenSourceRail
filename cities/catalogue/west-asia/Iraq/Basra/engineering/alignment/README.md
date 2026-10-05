# Basra Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`basra-line1.aln.toml`](basra-line1.aln.toml) | `line-1` | 38,796.4 m | 12 |
| [`basra-line2.aln.toml`](basra-line2.aln.toml) | `line-2` | 17,314.0 m | 6 |
| [`basra-line3.aln.toml`](basra-line3.aln.toml) | `line-3` | 38,893.4 m | 12 |
| [`basra-line4.aln.toml`](basra-line4.aln.toml) | `line-4` | 34,392.5 m | 11 |
| [`basra-line5.aln.toml`](basra-line5.aln.toml) | `line-5` | 35,280.4 m | 13 |
| [`basra-line6.aln.toml`](basra-line6.aln.toml) | `line-6` | 26,070.7 m | 8 |
| [`basra-line7.aln.toml`](basra-line7.aln.toml) | `line-7` | 77,293.1 m | 23 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
