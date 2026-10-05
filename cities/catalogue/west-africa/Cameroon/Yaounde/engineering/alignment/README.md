# Yaounde Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yaounde-line1.aln.toml`](yaounde-line1.aln.toml) | `line-1` | 38,666.3 m | 13 |
| [`yaounde-line2.aln.toml`](yaounde-line2.aln.toml) | `line-2` | 43,625.1 m | 14 |
| [`yaounde-line3.aln.toml`](yaounde-line3.aln.toml) | `line-3` | 30,016.9 m | 11 |
| [`yaounde-line4.aln.toml`](yaounde-line4.aln.toml) | `line-4` | 16,577.3 m | 9 |
| [`yaounde-line5.aln.toml`](yaounde-line5.aln.toml) | `line-5` | 62,969.0 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
