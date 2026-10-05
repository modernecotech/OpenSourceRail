# Yaounde Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yaounde-line1.aln.toml`](yaounde-line1.aln.toml) | `line-1` | 37,701.0 m | 12 |
| [`yaounde-line2.aln.toml`](yaounde-line2.aln.toml) | `line-2` | 42,109.9 m | 13 |
| [`yaounde-line3.aln.toml`](yaounde-line3.aln.toml) | `line-3` | 29,924.2 m | 10 |
| [`yaounde-line4.aln.toml`](yaounde-line4.aln.toml) | `line-4` | 17,010.4 m | 7 |
| [`yaounde-line5.aln.toml`](yaounde-line5.aln.toml) | `line-5` | 62,619.1 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
