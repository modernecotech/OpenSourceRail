# Tangier Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tangier-line1.aln.toml`](tangier-line1.aln.toml) | `line-1` | 25,014.9 m | 16 |
| [`tangier-line2.aln.toml`](tangier-line2.aln.toml) | `line-2` | 36,912.2 m | 17 |
| [`tangier-line3.aln.toml`](tangier-line3.aln.toml) | `line-3` | 22,677.8 m | 11 |
| [`tangier-line4.aln.toml`](tangier-line4.aln.toml) | `line-4` | 26,842.6 m | 8 |
| [`tangier-line5.aln.toml`](tangier-line5.aln.toml) | `line-5` | 61,081.0 m | 21 |
| [`tangier-line6.aln.toml`](tangier-line6.aln.toml) | `line-6` | 9,510.3 m | 3 |
| [`tangier-line7.aln.toml`](tangier-line7.aln.toml) | `line-7` | 8,480.1 m | 6 |
| [`tangier-line8.aln.toml`](tangier-line8.aln.toml) | `line-8` | 13,064.3 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
