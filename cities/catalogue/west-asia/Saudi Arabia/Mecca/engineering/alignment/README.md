# Mecca Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mecca-line1.aln.toml`](mecca-line1.aln.toml) | `line-1` | 27,234.5 m | 11 |
| [`mecca-line2.aln.toml`](mecca-line2.aln.toml) | `line-2` | 24,026.3 m | 9 |
| [`mecca-line3.aln.toml`](mecca-line3.aln.toml) | `line-3` | 32,171.7 m | 11 |
| [`mecca-line4.aln.toml`](mecca-line4.aln.toml) | `line-4` | 29,712.4 m | 11 |
| [`mecca-line5.aln.toml`](mecca-line5.aln.toml) | `line-5` | 23,257.5 m | 8 |
| [`mecca-line6.aln.toml`](mecca-line6.aln.toml) | `line-6` | 64,925.0 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
