# Jaffna Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jaffna-line1.aln.toml`](jaffna-line1.aln.toml) | `line-1` | 10,992.8 m | 9 |
| [`jaffna-line10.aln.toml`](jaffna-line10.aln.toml) | `line-10` | 3,598.5 m | 3 |
| [`jaffna-line11.aln.toml`](jaffna-line11.aln.toml) | `line-11` | 3,889.0 m | 3 |
| [`jaffna-line12.aln.toml`](jaffna-line12.aln.toml) | `line-12` | 8,469.3 m | 6 |
| [`jaffna-line2.aln.toml`](jaffna-line2.aln.toml) | `line-2` | 19,805.6 m | 11 |
| [`jaffna-line3.aln.toml`](jaffna-line3.aln.toml) | `line-3` | 16,005.8 m | 11 |
| [`jaffna-line4.aln.toml`](jaffna-line4.aln.toml) | `line-4` | 4,832.0 m | 4 |
| [`jaffna-line5.aln.toml`](jaffna-line5.aln.toml) | `line-5` | 8,580.4 m | 5 |
| [`jaffna-line6.aln.toml`](jaffna-line6.aln.toml) | `line-6` | 3,298.8 m | 3 |
| [`jaffna-line7.aln.toml`](jaffna-line7.aln.toml) | `line-7` | 4,447.6 m | 3 |
| [`jaffna-line8.aln.toml`](jaffna-line8.aln.toml) | `line-8` | 4,560.2 m | 4 |
| [`jaffna-line9.aln.toml`](jaffna-line9.aln.toml) | `line-9` | 3,330.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
