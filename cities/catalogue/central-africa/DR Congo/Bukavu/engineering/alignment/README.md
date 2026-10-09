# Bukavu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bukavu-line1.aln.toml`](bukavu-line1.aln.toml) | `line-1` | 13,594.7 m | 9 |
| [`bukavu-line2.aln.toml`](bukavu-line2.aln.toml) | `line-2` | 22,004.9 m | 14 |
| [`bukavu-line3.aln.toml`](bukavu-line3.aln.toml) | `line-3` | 17,441.4 m | 11 |
| [`bukavu-line4.aln.toml`](bukavu-line4.aln.toml) | `line-4` | 5,623.0 m | 6 |
| [`bukavu-line5.aln.toml`](bukavu-line5.aln.toml) | `line-5` | 3,287.9 m | 3 |
| [`bukavu-line6.aln.toml`](bukavu-line6.aln.toml) | `line-6` | 3,026.2 m | 3 |
| [`bukavu-line7.aln.toml`](bukavu-line7.aln.toml) | `line-7` | 5,937.5 m | 5 |
| [`bukavu-line8.aln.toml`](bukavu-line8.aln.toml) | `line-8` | 5,593.9 m | 4 |
| [`bukavu-line9.aln.toml`](bukavu-line9.aln.toml) | `line-9` | 7,824.2 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
