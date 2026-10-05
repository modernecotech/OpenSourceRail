# Tangier Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tangier-line1.aln.toml`](tangier-line1.aln.toml) | `line-1` | 17,051.2 m | 9 |
| [`tangier-line2.aln.toml`](tangier-line2.aln.toml) | `line-2` | 32,256.3 m | 11 |
| [`tangier-line3.aln.toml`](tangier-line3.aln.toml) | `line-3` | 17,515.8 m | 8 |
| [`tangier-line4.aln.toml`](tangier-line4.aln.toml) | `line-4` | 26,842.6 m | 9 |
| [`tangier-line5.aln.toml`](tangier-line5.aln.toml) | `line-5` | 54,317.0 m | 20 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
