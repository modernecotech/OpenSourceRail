# Nacala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nacala-line1.aln.toml`](nacala-line1.aln.toml) | `line-1` | 10,809.3 m | 6 |
| [`nacala-line10.aln.toml`](nacala-line10.aln.toml) | `line-10` | 5,046.4 m | 3 |
| [`nacala-line11.aln.toml`](nacala-line11.aln.toml) | `line-11` | 2,605.9 m | 2 |
| [`nacala-line12.aln.toml`](nacala-line12.aln.toml) | `line-12` | 9,246.9 m | 6 |
| [`nacala-line13.aln.toml`](nacala-line13.aln.toml) | `line-13` | 2,772.0 m | 2 |
| [`nacala-line2.aln.toml`](nacala-line2.aln.toml) | `line-2` | 23,562.2 m | 15 |
| [`nacala-line3.aln.toml`](nacala-line3.aln.toml) | `line-3` | 9,667.6 m | 6 |
| [`nacala-line4.aln.toml`](nacala-line4.aln.toml) | `line-4` | 3,205.9 m | 3 |
| [`nacala-line5.aln.toml`](nacala-line5.aln.toml) | `line-5` | 3,918.2 m | 3 |
| [`nacala-line6.aln.toml`](nacala-line6.aln.toml) | `line-6` | 4,620.5 m | 3 |
| [`nacala-line7.aln.toml`](nacala-line7.aln.toml) | `line-7` | 2,020.0 m | 2 |
| [`nacala-line8.aln.toml`](nacala-line8.aln.toml) | `line-8` | 6,159.0 m | 4 |
| [`nacala-line9.aln.toml`](nacala-line9.aln.toml) | `line-9` | 2,791.6 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
