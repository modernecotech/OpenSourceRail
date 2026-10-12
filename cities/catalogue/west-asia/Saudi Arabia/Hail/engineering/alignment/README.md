# Hail Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hail-line1.aln.toml`](hail-line1.aln.toml) | `line-1` | 28,308.8 m | 10 |
| [`hail-line2.aln.toml`](hail-line2.aln.toml) | `line-2` | 23,595.5 m | 11 |
| [`hail-line3.aln.toml`](hail-line3.aln.toml) | `line-3` | 15,926.2 m | 9 |
| [`hail-line4.aln.toml`](hail-line4.aln.toml) | `line-4` | 5,885.0 m | 3 |
| [`hail-line5.aln.toml`](hail-line5.aln.toml) | `line-5` | 4,617.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
