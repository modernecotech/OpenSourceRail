# Jodhpur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jodhpur-line1.aln.toml`](jodhpur-line1.aln.toml) | `line-1` | 28,912.8 m | 17 |
| [`jodhpur-line2.aln.toml`](jodhpur-line2.aln.toml) | `line-2` | 21,449.3 m | 14 |
| [`jodhpur-line3.aln.toml`](jodhpur-line3.aln.toml) | `line-3` | 22,528.1 m | 13 |
| [`jodhpur-line4.aln.toml`](jodhpur-line4.aln.toml) | `line-4` | 26,265.1 m | 16 |
| [`jodhpur-line5.aln.toml`](jodhpur-line5.aln.toml) | `line-5` | 51,018.1 m | 34 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
