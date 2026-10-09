# Machakos Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`machakos-line1.aln.toml`](machakos-line1.aln.toml) | `line-1` | 10,623.9 m | 7 |
| [`machakos-line2.aln.toml`](machakos-line2.aln.toml) | `line-2` | 6,830.8 m | 5 |
| [`machakos-line3.aln.toml`](machakos-line3.aln.toml) | `line-3` | 6,206.7 m | 4 |
| [`machakos-line4.aln.toml`](machakos-line4.aln.toml) | `line-4` | 2,815.4 m | 2 |
| [`machakos-line5.aln.toml`](machakos-line5.aln.toml) | `line-5` | 3,362.3 m | 3 |
| [`machakos-line6.aln.toml`](machakos-line6.aln.toml) | `line-6` | 7,862.4 m | 6 |
| [`machakos-line7.aln.toml`](machakos-line7.aln.toml) | `line-7` | 6,034.1 m | 4 |
| [`machakos-line8.aln.toml`](machakos-line8.aln.toml) | `line-8` | 3,113.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
