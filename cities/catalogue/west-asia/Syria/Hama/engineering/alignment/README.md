# Hama Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hama-line1.aln.toml`](hama-line1.aln.toml) | `line-1` | 17,764.8 m | 11 |
| [`hama-line10.aln.toml`](hama-line10.aln.toml) | `line-10` | 2,040.0 m | 2 |
| [`hama-line11.aln.toml`](hama-line11.aln.toml) | `line-11` | 4,947.9 m | 4 |
| [`hama-line2.aln.toml`](hama-line2.aln.toml) | `line-2` | 9,845.6 m | 9 |
| [`hama-line3.aln.toml`](hama-line3.aln.toml) | `line-3` | 14,109.7 m | 9 |
| [`hama-line4.aln.toml`](hama-line4.aln.toml) | `line-4` | 3,734.8 m | 3 |
| [`hama-line5.aln.toml`](hama-line5.aln.toml) | `line-5` | 7,398.5 m | 5 |
| [`hama-line6.aln.toml`](hama-line6.aln.toml) | `line-6` | 5,158.1 m | 3 |
| [`hama-line7.aln.toml`](hama-line7.aln.toml) | `line-7` | 8,274.1 m | 5 |
| [`hama-line8.aln.toml`](hama-line8.aln.toml) | `line-8` | 6,866.4 m | 4 |
| [`hama-line9.aln.toml`](hama-line9.aln.toml) | `line-9` | 3,116.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
