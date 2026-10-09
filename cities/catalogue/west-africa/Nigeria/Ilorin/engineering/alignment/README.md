# Ilorin Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ilorin-line1.aln.toml`](ilorin-line1.aln.toml) | `line-1` | 13,109.4 m | 9 |
| [`ilorin-line10.aln.toml`](ilorin-line10.aln.toml) | `line-10` | 6,337.1 m | 4 |
| [`ilorin-line11.aln.toml`](ilorin-line11.aln.toml) | `line-11` | 4,700.7 m | 3 |
| [`ilorin-line2.aln.toml`](ilorin-line2.aln.toml) | `line-2` | 15,814.8 m | 9 |
| [`ilorin-line3.aln.toml`](ilorin-line3.aln.toml) | `line-3` | 11,845.5 m | 7 |
| [`ilorin-line4.aln.toml`](ilorin-line4.aln.toml) | `line-4` | 3,960.5 m | 3 |
| [`ilorin-line5.aln.toml`](ilorin-line5.aln.toml) | `line-5` | 3,403.9 m | 3 |
| [`ilorin-line6.aln.toml`](ilorin-line6.aln.toml) | `line-6` | 11,118.6 m | 7 |
| [`ilorin-line7.aln.toml`](ilorin-line7.aln.toml) | `line-7` | 3,181.1 m | 3 |
| [`ilorin-line8.aln.toml`](ilorin-line8.aln.toml) | `line-8` | 3,146.5 m | 3 |
| [`ilorin-line9.aln.toml`](ilorin-line9.aln.toml) | `line-9` | 3,228.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
