# Phnom-Penh Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`phnom-penh-line1.aln.toml`](phnom-penh-line1.aln.toml) | `line-1` | 30,917.8 m | 15 |
| [`phnom-penh-line2.aln.toml`](phnom-penh-line2.aln.toml) | `line-2` | 32,984.3 m | 29 |
| [`phnom-penh-line3.aln.toml`](phnom-penh-line3.aln.toml) | `line-3` | 59,407.5 m | 27 |
| [`phnom-penh-line4.aln.toml`](phnom-penh-line4.aln.toml) | `line-4` | 36,760.1 m | 19 |
| [`phnom-penh-line5.aln.toml`](phnom-penh-line5.aln.toml) | `line-5` | 39,419.5 m | 32 |
| [`phnom-penh-line6.aln.toml`](phnom-penh-line6.aln.toml) | `line-6` | 67,459.6 m | 21 |
| [`phnom-penh-line7.aln.toml`](phnom-penh-line7.aln.toml) | `line-7` | 6,468.4 m | 3 |
| [`phnom-penh-line8.aln.toml`](phnom-penh-line8.aln.toml) | `line-8` | 5,357.3 m | 2 |
| [`phnom-penh-line9.aln.toml`](phnom-penh-line9.aln.toml) | `line-9` | 19,753.2 m | 11 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
