# Sanaa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sanaa-line1.aln.toml`](sanaa-line1.aln.toml) | `line-1` | 37,288.9 m | 13 |
| [`sanaa-line2.aln.toml`](sanaa-line2.aln.toml) | `line-2` | 17,975.6 m | 9 |
| [`sanaa-line3.aln.toml`](sanaa-line3.aln.toml) | `line-3` | 29,346.0 m | 12 |
| [`sanaa-line4.aln.toml`](sanaa-line4.aln.toml) | `line-4` | 22,083.9 m | 12 |
| [`sanaa-line5.aln.toml`](sanaa-line5.aln.toml) | `line-5` | 31,022.7 m | 15 |
| [`sanaa-line6.aln.toml`](sanaa-line6.aln.toml) | `line-6` | 20,382.9 m | 9 |
| [`sanaa-line7.aln.toml`](sanaa-line7.aln.toml) | `line-7` | 56,049.2 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
