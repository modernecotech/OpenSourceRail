# Raqqa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`raqqa-line1.aln.toml`](raqqa-line1.aln.toml) | `line-1` | 13,339.1 m | 12 |
| [`raqqa-line2.aln.toml`](raqqa-line2.aln.toml) | `line-2` | 11,917.3 m | 8 |
| [`raqqa-line3.aln.toml`](raqqa-line3.aln.toml) | `line-3` | 15,672.3 m | 11 |
| [`raqqa-line4.aln.toml`](raqqa-line4.aln.toml) | `line-4` | 4,197.9 m | 4 |
| [`raqqa-line5.aln.toml`](raqqa-line5.aln.toml) | `line-5` | 6,590.1 m | 9 |
| [`raqqa-line6.aln.toml`](raqqa-line6.aln.toml) | `line-6` | 5,007.8 m | 4 |
| [`raqqa-line7.aln.toml`](raqqa-line7.aln.toml) | `line-7` | 6,812.9 m | 5 |
| [`raqqa-line8.aln.toml`](raqqa-line8.aln.toml) | `line-8` | 10,102.1 m | 10 |
| [`raqqa-line9.aln.toml`](raqqa-line9.aln.toml) | `line-9` | 7,882.1 m | 8 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
