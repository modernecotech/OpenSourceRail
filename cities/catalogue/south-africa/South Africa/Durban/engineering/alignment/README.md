# Durban Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`durban-line1.aln.toml`](durban-line1.aln.toml) | `line-1` | 50,916.9 m | 20 |
| [`durban-line2.aln.toml`](durban-line2.aln.toml) | `line-2` | 36,056.6 m | 15 |
| [`durban-line3.aln.toml`](durban-line3.aln.toml) | `line-3` | 37,744.4 m | 17 |
| [`durban-line4.aln.toml`](durban-line4.aln.toml) | `line-4` | 27,510.5 m | 20 |
| [`durban-line5.aln.toml`](durban-line5.aln.toml) | `line-5` | 35,940.3 m | 16 |
| [`durban-line6.aln.toml`](durban-line6.aln.toml) | `line-6` | 33,537.7 m | 20 |
| [`durban-line7.aln.toml`](durban-line7.aln.toml) | `line-7` | 28,922.7 m | 13 |
| [`durban-line8.aln.toml`](durban-line8.aln.toml) | `line-8` | 24,705.9 m | 12 |
| [`durban-line9.aln.toml`](durban-line9.aln.toml) | `line-9` | 83,562.1 m | 28 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
