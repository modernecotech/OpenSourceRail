# Suez Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`suez-line1.aln.toml`](suez-line1.aln.toml) | `line-1` | 25,027.6 m | 16 |
| [`suez-line2.aln.toml`](suez-line2.aln.toml) | `line-2` | 16,232.6 m | 8 |
| [`suez-line3.aln.toml`](suez-line3.aln.toml) | `line-3` | 14,633.1 m | 9 |
| [`suez-line4.aln.toml`](suez-line4.aln.toml) | `line-4` | 2,350.5 m | 2 |
| [`suez-line5.aln.toml`](suez-line5.aln.toml) | `line-5` | 3,140.1 m | 3 |
| [`suez-line6.aln.toml`](suez-line6.aln.toml) | `line-6` | 7,961.3 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
