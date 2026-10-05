# Madurai Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`madurai-line1.aln.toml`](madurai-line1.aln.toml) | `line-1` | 36,493.0 m | 15 |
| [`madurai-line2.aln.toml`](madurai-line2.aln.toml) | `line-2` | 26,467.8 m | 11 |
| [`madurai-line3.aln.toml`](madurai-line3.aln.toml) | `line-3` | 27,579.7 m | 10 |
| [`madurai-line4.aln.toml`](madurai-line4.aln.toml) | `line-4` | 22,910.2 m | 8 |
| [`madurai-line5.aln.toml`](madurai-line5.aln.toml) | `line-5` | 23,830.1 m | 13 |
| [`madurai-line6.aln.toml`](madurai-line6.aln.toml) | `line-6` | 67,424.2 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
