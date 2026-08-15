# Durban Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`durban-line1.aln.toml`](durban-line1.aln.toml) | `line-1` | 57,230.1 m | 35 |
| [`durban-line2.aln.toml`](durban-line2.aln.toml) | `line-2` | 44,103.1 m | 27 |
| [`durban-line3.aln.toml`](durban-line3.aln.toml) | `line-3` | 48,866.7 m | 28 |
| [`durban-line4.aln.toml`](durban-line4.aln.toml) | `line-4` | 26,400.8 m | 16 |
| [`durban-line5.aln.toml`](durban-line5.aln.toml) | `line-5` | 37,939.1 m | 22 |
| [`durban-line6.aln.toml`](durban-line6.aln.toml) | `line-6` | 32,264.4 m | 18 |
| [`durban-line7.aln.toml`](durban-line7.aln.toml) | `line-7` | 32,905.8 m | 18 |
| [`durban-line8.aln.toml`](durban-line8.aln.toml) | `line-8` | 28,997.2 m | 18 |
| [`durban-line9.aln.toml`](durban-line9.aln.toml) | `line-9` | 92,320.4 m | 64 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
