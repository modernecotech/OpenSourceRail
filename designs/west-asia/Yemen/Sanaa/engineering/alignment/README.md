# Sanaa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sanaa-line1.aln.toml`](sanaa-line1.aln.toml) | `line-1` | 41,473.1 m | 22 |
| [`sanaa-line2.aln.toml`](sanaa-line2.aln.toml) | `line-2` | 20,949.9 m | 14 |
| [`sanaa-line3.aln.toml`](sanaa-line3.aln.toml) | `line-3` | 32,034.1 m | 19 |
| [`sanaa-line4.aln.toml`](sanaa-line4.aln.toml) | `line-4` | 24,742.8 m | 16 |
| [`sanaa-line5.aln.toml`](sanaa-line5.aln.toml) | `line-5` | 33,848.8 m | 19 |
| [`sanaa-line6.aln.toml`](sanaa-line6.aln.toml) | `line-6` | 20,943.9 m | 11 |
| [`sanaa-line7.aln.toml`](sanaa-line7.aln.toml) | `line-7` | 59,092.0 m | 39 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
