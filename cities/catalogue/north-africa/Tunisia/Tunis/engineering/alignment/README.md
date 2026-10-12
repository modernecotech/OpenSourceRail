# Tunis Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tunis-line1.aln.toml`](tunis-line1.aln.toml) | `line-1` | 40,993.7 m | 13 |
| [`tunis-line2.aln.toml`](tunis-line2.aln.toml) | `line-2` | 31,990.6 m | 13 |
| [`tunis-line3.aln.toml`](tunis-line3.aln.toml) | `line-3` | 48,306.0 m | 12 |
| [`tunis-line4.aln.toml`](tunis-line4.aln.toml) | `line-4` | 33,311.5 m | 13 |
| [`tunis-line5.aln.toml`](tunis-line5.aln.toml) | `line-5` | 81,669.2 m | 23 |
| [`tunis-line6.aln.toml`](tunis-line6.aln.toml) | `line-6` | 12,364.2 m | 4 |
| [`tunis-line7.aln.toml`](tunis-line7.aln.toml) | `line-7` | 13,620.5 m | 5 |
| [`tunis-line8.aln.toml`](tunis-line8.aln.toml) | `line-8` | 6,099.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
