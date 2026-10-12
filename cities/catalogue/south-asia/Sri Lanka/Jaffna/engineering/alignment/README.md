# Jaffna Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jaffna-line1.aln.toml`](jaffna-line1.aln.toml) | `line-1` | 13,711.4 m | 8 |
| [`jaffna-line2.aln.toml`](jaffna-line2.aln.toml) | `line-2` | 25,205.0 m | 7 |
| [`jaffna-line3.aln.toml`](jaffna-line3.aln.toml) | `line-3` | 17,052.3 m | 9 |
| [`jaffna-line4.aln.toml`](jaffna-line4.aln.toml) | `line-4` | 5,904.8 m | 3 |
| [`jaffna-line5.aln.toml`](jaffna-line5.aln.toml) | `line-5` | 4,372.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
