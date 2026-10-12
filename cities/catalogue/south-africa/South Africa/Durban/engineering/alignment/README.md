# Durban Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`durban-line1.aln.toml`](durban-line1.aln.toml) | `line-1` | 62,105.7 m | 22 |
| [`durban-line10.aln.toml`](durban-line10.aln.toml) | `line-10` | 10,307.5 m | 4 |
| [`durban-line11.aln.toml`](durban-line11.aln.toml) | `line-11` | 6,341.6 m | 2 |
| [`durban-line12.aln.toml`](durban-line12.aln.toml) | `line-12` | 11,743.1 m | 4 |
| [`durban-line13.aln.toml`](durban-line13.aln.toml) | `line-13` | 8,444.7 m | 4 |
| [`durban-line14.aln.toml`](durban-line14.aln.toml) | `line-14` | 6,350.7 m | 3 |
| [`durban-line2.aln.toml`](durban-line2.aln.toml) | `line-2` | 47,576.8 m | 20 |
| [`durban-line3.aln.toml`](durban-line3.aln.toml) | `line-3` | 52,139.6 m | 28 |
| [`durban-line4.aln.toml`](durban-line4.aln.toml) | `line-4` | 27,430.5 m | 15 |
| [`durban-line5.aln.toml`](durban-line5.aln.toml) | `line-5` | 35,940.3 m | 12 |
| [`durban-line6.aln.toml`](durban-line6.aln.toml) | `line-6` | 32,882.8 m | 16 |
| [`durban-line7.aln.toml`](durban-line7.aln.toml) | `line-7` | 34,074.9 m | 18 |
| [`durban-line8.aln.toml`](durban-line8.aln.toml) | `line-8` | 30,180.8 m | 24 |
| [`durban-line9.aln.toml`](durban-line9.aln.toml) | `line-9` | 92,768.8 m | 29 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
