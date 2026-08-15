# Kirkuk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kirkuk-line1.aln.toml`](kirkuk-line1.aln.toml) | `line-1` | 23,171.9 m | 13 |
| [`kirkuk-line2.aln.toml`](kirkuk-line2.aln.toml) | `line-2` | 21,518.7 m | 14 |
| [`kirkuk-line3.aln.toml`](kirkuk-line3.aln.toml) | `line-3` | 20,395.0 m | 15 |
| [`kirkuk-line4.aln.toml`](kirkuk-line4.aln.toml) | `line-4` | 23,715.5 m | 13 |
| [`kirkuk-line5.aln.toml`](kirkuk-line5.aln.toml) | `line-5` | 55,141.9 m | 33 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
