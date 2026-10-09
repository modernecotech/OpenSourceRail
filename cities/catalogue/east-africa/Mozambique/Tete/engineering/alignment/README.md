# Tete Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tete-line1.aln.toml`](tete-line1.aln.toml) | `line-1` | 19,149.3 m | 14 |
| [`tete-line10.aln.toml`](tete-line10.aln.toml) | `line-10` | 3,307.9 m | 3 |
| [`tete-line11.aln.toml`](tete-line11.aln.toml) | `line-11` | 4,899.6 m | 4 |
| [`tete-line12.aln.toml`](tete-line12.aln.toml) | `line-12` | 7,647.8 m | 6 |
| [`tete-line2.aln.toml`](tete-line2.aln.toml) | `line-2` | 11,747.6 m | 11 |
| [`tete-line3.aln.toml`](tete-line3.aln.toml) | `line-3` | 9,650.0 m | 10 |
| [`tete-line4.aln.toml`](tete-line4.aln.toml) | `line-4` | 2,757.1 m | 3 |
| [`tete-line5.aln.toml`](tete-line5.aln.toml) | `line-5` | 3,178.2 m | 3 |
| [`tete-line6.aln.toml`](tete-line6.aln.toml) | `line-6` | 3,510.2 m | 4 |
| [`tete-line7.aln.toml`](tete-line7.aln.toml) | `line-7` | 2,223.1 m | 2 |
| [`tete-line8.aln.toml`](tete-line8.aln.toml) | `line-8` | 7,755.0 m | 5 |
| [`tete-line9.aln.toml`](tete-line9.aln.toml) | `line-9` | 4,333.6 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
