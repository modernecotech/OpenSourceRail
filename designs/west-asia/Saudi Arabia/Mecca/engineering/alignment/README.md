# Mecca Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mecca-line1.aln.toml`](mecca-line1.aln.toml) | `line-1` | 31,152.8 m | 13 |
| [`mecca-line2.aln.toml`](mecca-line2.aln.toml) | `line-2` | 25,258.2 m | 9 |
| [`mecca-line3.aln.toml`](mecca-line3.aln.toml) | `line-3` | 37,118.7 m | 13 |
| [`mecca-line4.aln.toml`](mecca-line4.aln.toml) | `line-4` | 33,905.6 m | 12 |
| [`mecca-line5.aln.toml`](mecca-line5.aln.toml) | `line-5` | 24,305.1 m | 8 |
| [`mecca-line6.aln.toml`](mecca-line6.aln.toml) | `line-6` | 71,361.9 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
