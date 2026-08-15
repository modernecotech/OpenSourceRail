# Lusaka Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lusaka-line1.aln.toml`](lusaka-line1.aln.toml) | `line-1` | 38,518.1 m | 23 |
| [`lusaka-line2.aln.toml`](lusaka-line2.aln.toml) | `line-2` | 26,247.1 m | 15 |
| [`lusaka-line3.aln.toml`](lusaka-line3.aln.toml) | `line-3` | 27,488.8 m | 18 |
| [`lusaka-line4.aln.toml`](lusaka-line4.aln.toml) | `line-4` | 23,845.8 m | 14 |
| [`lusaka-line5.aln.toml`](lusaka-line5.aln.toml) | `line-5` | 28,408.5 m | 17 |
| [`lusaka-line6.aln.toml`](lusaka-line6.aln.toml) | `line-6` | 32,437.3 m | 18 |
| [`lusaka-line7.aln.toml`](lusaka-line7.aln.toml) | `line-7` | 28,663.1 m | 16 |
| [`lusaka-line8.aln.toml`](lusaka-line8.aln.toml) | `line-8` | 73,911.5 m | 46 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
