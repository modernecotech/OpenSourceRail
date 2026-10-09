# Luxor Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`luxor-line1.aln.toml`](luxor-line1.aln.toml) | `line-1` | 10,123.2 m | 7 |
| [`luxor-line10.aln.toml`](luxor-line10.aln.toml) | `line-10` | 2,286.8 m | 2 |
| [`luxor-line11.aln.toml`](luxor-line11.aln.toml) | `line-11` | 6,068.9 m | 4 |
| [`luxor-line12.aln.toml`](luxor-line12.aln.toml) | `line-12` | 3,095.0 m | 5 |
| [`luxor-line2.aln.toml`](luxor-line2.aln.toml) | `line-2` | 21,836.8 m | 14 |
| [`luxor-line3.aln.toml`](luxor-line3.aln.toml) | `line-3` | 12,607.0 m | 9 |
| [`luxor-line4.aln.toml`](luxor-line4.aln.toml) | `line-4` | 2,893.6 m | 2 |
| [`luxor-line5.aln.toml`](luxor-line5.aln.toml) | `line-5` | 8,760.3 m | 6 |
| [`luxor-line6.aln.toml`](luxor-line6.aln.toml) | `line-6` | 3,899.6 m | 4 |
| [`luxor-line7.aln.toml`](luxor-line7.aln.toml) | `line-7` | 9,728.6 m | 8 |
| [`luxor-line8.aln.toml`](luxor-line8.aln.toml) | `line-8` | 4,562.4 m | 3 |
| [`luxor-line9.aln.toml`](luxor-line9.aln.toml) | `line-9` | 2,041.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
