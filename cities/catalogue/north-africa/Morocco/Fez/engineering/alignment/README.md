# Fez Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`fez-line1.aln.toml`](fez-line1.aln.toml) | `line-1` | 24,478.8 m | 23 |
| [`fez-line2.aln.toml`](fez-line2.aln.toml) | `line-2` | 22,596.4 m | 12 |
| [`fez-line3.aln.toml`](fez-line3.aln.toml) | `line-3` | 21,538.4 m | 7 |
| [`fez-line4.aln.toml`](fez-line4.aln.toml) | `line-4` | 54,990.5 m | 34 |
| [`fez-line5.aln.toml`](fez-line5.aln.toml) | `line-5` | 6,607.2 m | 3 |
| [`fez-line6.aln.toml`](fez-line6.aln.toml) | `line-6` | 11,804.8 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
