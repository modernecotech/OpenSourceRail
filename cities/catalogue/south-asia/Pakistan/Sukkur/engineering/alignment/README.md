# Sukkur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sukkur-line1.aln.toml`](sukkur-line1.aln.toml) | `line-1` | 20,751.8 m | 15 |
| [`sukkur-line10.aln.toml`](sukkur-line10.aln.toml) | `line-10` | 4,636.5 m | 3 |
| [`sukkur-line11.aln.toml`](sukkur-line11.aln.toml) | `line-11` | 2,072.2 m | 2 |
| [`sukkur-line12.aln.toml`](sukkur-line12.aln.toml) | `line-12` | 2,353.0 m | 2 |
| [`sukkur-line2.aln.toml`](sukkur-line2.aln.toml) | `line-2` | 8,927.5 m | 7 |
| [`sukkur-line3.aln.toml`](sukkur-line3.aln.toml) | `line-3` | 9,100.9 m | 8 |
| [`sukkur-line4.aln.toml`](sukkur-line4.aln.toml) | `line-4` | 4,313.3 m | 4 |
| [`sukkur-line5.aln.toml`](sukkur-line5.aln.toml) | `line-5` | 4,773.9 m | 3 |
| [`sukkur-line6.aln.toml`](sukkur-line6.aln.toml) | `line-6` | 6,977.0 m | 5 |
| [`sukkur-line7.aln.toml`](sukkur-line7.aln.toml) | `line-7` | 4,357.1 m | 3 |
| [`sukkur-line8.aln.toml`](sukkur-line8.aln.toml) | `line-8` | 2,812.2 m | 2 |
| [`sukkur-line9.aln.toml`](sukkur-line9.aln.toml) | `line-9` | 4,650.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
