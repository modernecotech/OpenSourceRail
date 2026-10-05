# Durban Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`durban-line1.aln.toml`](durban-line1.aln.toml) | `line-1` | 48,884.1 m | 20 |
| [`durban-line2.aln.toml`](durban-line2.aln.toml) | `line-2` | 35,401.7 m | 14 |
| [`durban-line3.aln.toml`](durban-line3.aln.toml) | `line-3` | 36,709.6 m | 17 |
| [`durban-line4.aln.toml`](durban-line4.aln.toml) | `line-4` | 27,510.5 m | 20 |
| [`durban-line5.aln.toml`](durban-line5.aln.toml) | `line-5` | 33,766.6 m | 15 |
| [`durban-line6.aln.toml`](durban-line6.aln.toml) | `line-6` | 33,537.7 m | 20 |
| [`durban-line7.aln.toml`](durban-line7.aln.toml) | `line-7` | 28,476.0 m | 13 |
| [`durban-line8.aln.toml`](durban-line8.aln.toml) | `line-8` | 24,152.8 m | 12 |
| [`durban-line9.aln.toml`](durban-line9.aln.toml) | `line-9` | 81,938.4 m | 28 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
