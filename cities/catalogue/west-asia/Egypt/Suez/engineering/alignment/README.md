# Suez Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`suez-line1.aln.toml`](suez-line1.aln.toml) | `line-1` | 25,027.6 m | 9 |
| [`suez-line2.aln.toml`](suez-line2.aln.toml) | `line-2` | 16,232.6 m | 5 |
| [`suez-line3.aln.toml`](suez-line3.aln.toml) | `line-3` | 17,000.1 m | 5 |
| [`suez-line4.aln.toml`](suez-line4.aln.toml) | `line-4` | 4,654.5 m | 2 |
| [`suez-line5.aln.toml`](suez-line5.aln.toml) | `line-5` | 8,419.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
