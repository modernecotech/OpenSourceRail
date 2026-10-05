# Jeddah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jeddah-line1.aln.toml`](jeddah-line1.aln.toml) | `line-1` | 44,961.8 m | 14 |
| [`jeddah-line2.aln.toml`](jeddah-line2.aln.toml) | `line-2` | 25,610.3 m | 7 |
| [`jeddah-line3.aln.toml`](jeddah-line3.aln.toml) | `line-3` | 38,114.3 m | 13 |
| [`jeddah-line4.aln.toml`](jeddah-line4.aln.toml) | `line-4` | 39,794.9 m | 13 |
| [`jeddah-line5.aln.toml`](jeddah-line5.aln.toml) | `line-5` | 32,126.2 m | 11 |
| [`jeddah-line6.aln.toml`](jeddah-line6.aln.toml) | `line-6` | 29,441.8 m | 10 |
| [`jeddah-line7.aln.toml`](jeddah-line7.aln.toml) | `line-7` | 23,482.8 m | 8 |
| [`jeddah-line8.aln.toml`](jeddah-line8.aln.toml) | `line-8` | 24,373.5 m | 9 |
| [`jeddah-line9.aln.toml`](jeddah-line9.aln.toml) | `line-9` | 74,186.0 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
