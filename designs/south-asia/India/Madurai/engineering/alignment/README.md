# Madurai Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`madurai-line1.aln.toml`](madurai-line1.aln.toml) | `line-1` | 36,836.2 m | 11 |
| [`madurai-line2.aln.toml`](madurai-line2.aln.toml) | `line-2` | 33,101.1 m | 11 |
| [`madurai-line3.aln.toml`](madurai-line3.aln.toml) | `line-3` | 29,607.1 m | 9 |
| [`madurai-line4.aln.toml`](madurai-line4.aln.toml) | `line-4` | 26,522.7 m | 10 |
| [`madurai-line5.aln.toml`](madurai-line5.aln.toml) | `line-5` | 26,783.5 m | 10 |
| [`madurai-line6.aln.toml`](madurai-line6.aln.toml) | `line-6` | 71,437.7 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
