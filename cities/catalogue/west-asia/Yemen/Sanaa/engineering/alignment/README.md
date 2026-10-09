# Sanaa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sanaa-line1.aln.toml`](sanaa-line1.aln.toml) | `line-1` | 37,288.9 m | 22 |
| [`sanaa-line10.aln.toml`](sanaa-line10.aln.toml) | `line-10` | 8,763.0 m | 8 |
| [`sanaa-line11.aln.toml`](sanaa-line11.aln.toml) | `line-11` | 6,278.5 m | 7 |
| [`sanaa-line12.aln.toml`](sanaa-line12.aln.toml) | `line-12` | 5,450.4 m | 4 |
| [`sanaa-line13.aln.toml`](sanaa-line13.aln.toml) | `line-13` | 9,707.2 m | 8 |
| [`sanaa-line2.aln.toml`](sanaa-line2.aln.toml) | `line-2` | 17,975.6 m | 13 |
| [`sanaa-line3.aln.toml`](sanaa-line3.aln.toml) | `line-3` | 29,346.0 m | 21 |
| [`sanaa-line4.aln.toml`](sanaa-line4.aln.toml) | `line-4` | 22,083.9 m | 16 |
| [`sanaa-line5.aln.toml`](sanaa-line5.aln.toml) | `line-5` | 31,022.7 m | 20 |
| [`sanaa-line6.aln.toml`](sanaa-line6.aln.toml) | `line-6` | 20,382.9 m | 15 |
| [`sanaa-line7.aln.toml`](sanaa-line7.aln.toml) | `line-7` | 56,049.2 m | 35 |
| [`sanaa-line8.aln.toml`](sanaa-line8.aln.toml) | `line-8` | 7,497.6 m | 9 |
| [`sanaa-line9.aln.toml`](sanaa-line9.aln.toml) | `line-9` | 5,665.8 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
