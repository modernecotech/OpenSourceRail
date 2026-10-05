# Bandung Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bandung-line1.aln.toml`](bandung-line1.aln.toml) | `line-1` | 33,074.1 m | 12 |
| [`bandung-line2.aln.toml`](bandung-line2.aln.toml) | `line-2` | 36,997.8 m | 13 |
| [`bandung-line3.aln.toml`](bandung-line3.aln.toml) | `line-3` | 17,435.6 m | 7 |
| [`bandung-line4.aln.toml`](bandung-line4.aln.toml) | `line-4` | 28,880.3 m | 10 |
| [`bandung-line5.aln.toml`](bandung-line5.aln.toml) | `line-5` | 28,070.8 m | 11 |
| [`bandung-line6.aln.toml`](bandung-line6.aln.toml) | `line-6` | 66,393.3 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
