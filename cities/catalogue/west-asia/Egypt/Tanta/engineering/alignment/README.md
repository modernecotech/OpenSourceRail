# Tanta Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tanta-line1.aln.toml`](tanta-line1.aln.toml) | `line-1` | 15,263.9 m | 9 |
| [`tanta-line10.aln.toml`](tanta-line10.aln.toml) | `line-10` | 2,013.6 m | 2 |
| [`tanta-line11.aln.toml`](tanta-line11.aln.toml) | `line-11` | 12,610.1 m | 8 |
| [`tanta-line12.aln.toml`](tanta-line12.aln.toml) | `line-12` | 6,502.6 m | 5 |
| [`tanta-line2.aln.toml`](tanta-line2.aln.toml) | `line-2` | 27,026.3 m | 16 |
| [`tanta-line3.aln.toml`](tanta-line3.aln.toml) | `line-3` | 28,372.0 m | 16 |
| [`tanta-line4.aln.toml`](tanta-line4.aln.toml) | `line-4` | 5,983.8 m | 5 |
| [`tanta-line5.aln.toml`](tanta-line5.aln.toml) | `line-5` | 12,763.9 m | 8 |
| [`tanta-line6.aln.toml`](tanta-line6.aln.toml) | `line-6` | 11,205.2 m | 7 |
| [`tanta-line7.aln.toml`](tanta-line7.aln.toml) | `line-7` | 9,135.2 m | 6 |
| [`tanta-line8.aln.toml`](tanta-line8.aln.toml) | `line-8` | 6,636.7 m | 4 |
| [`tanta-line9.aln.toml`](tanta-line9.aln.toml) | `line-9` | 2,845.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
