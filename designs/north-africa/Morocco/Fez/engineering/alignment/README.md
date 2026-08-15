# Fez Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`fez-line1.aln.toml`](fez-line1.aln.toml) | `line-1` | 22,346.5 m | 14 |
| [`fez-line2.aln.toml`](fez-line2.aln.toml) | `line-2` | 20,339.7 m | 15 |
| [`fez-line3.aln.toml`](fez-line3.aln.toml) | `line-3` | 19,754.2 m | 13 |
| [`fez-line4.aln.toml`](fez-line4.aln.toml) | `line-4` | 51,984.5 m | 34 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
