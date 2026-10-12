# Bukavu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bukavu-line1.aln.toml`](bukavu-line1.aln.toml) | `line-1` | 17,644.9 m | 15 |
| [`bukavu-line2.aln.toml`](bukavu-line2.aln.toml) | `line-2` | 26,629.2 m | 12 |
| [`bukavu-line3.aln.toml`](bukavu-line3.aln.toml) | `line-3` | 17,441.4 m | 9 |
| [`bukavu-line4.aln.toml`](bukavu-line4.aln.toml) | `line-4` | 5,969.0 m | 3 |
| [`bukavu-line5.aln.toml`](bukavu-line5.aln.toml) | `line-5` | 4,717.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
