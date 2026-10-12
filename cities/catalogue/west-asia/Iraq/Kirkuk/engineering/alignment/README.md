# Kirkuk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kirkuk-line1.aln.toml`](kirkuk-line1.aln.toml) | `line-1` | 24,233.4 m | 12 |
| [`kirkuk-line2.aln.toml`](kirkuk-line2.aln.toml) | `line-2` | 23,954.7 m | 9 |
| [`kirkuk-line3.aln.toml`](kirkuk-line3.aln.toml) | `line-3` | 22,028.9 m | 9 |
| [`kirkuk-line4.aln.toml`](kirkuk-line4.aln.toml) | `line-4` | 25,259.1 m | 7 |
| [`kirkuk-line5.aln.toml`](kirkuk-line5.aln.toml) | `line-5` | 58,610.1 m | 24 |
| [`kirkuk-line6.aln.toml`](kirkuk-line6.aln.toml) | `line-6` | 4,745.6 m | 2 |
| [`kirkuk-line7.aln.toml`](kirkuk-line7.aln.toml) | `line-7` | 8,014.4 m | 3 |
| [`kirkuk-line8.aln.toml`](kirkuk-line8.aln.toml) | `line-8` | 7,167.2 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
