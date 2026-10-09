# Jinja Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jinja-line1.aln.toml`](jinja-line1.aln.toml) | `line-1` | 12,991.7 m | 9 |
| [`jinja-line10.aln.toml`](jinja-line10.aln.toml) | `line-10` | 4,133.6 m | 3 |
| [`jinja-line11.aln.toml`](jinja-line11.aln.toml) | `line-11` | 2,419.9 m | 2 |
| [`jinja-line12.aln.toml`](jinja-line12.aln.toml) | `line-12` | 3,517.3 m | 3 |
| [`jinja-line13.aln.toml`](jinja-line13.aln.toml) | `line-13` | 2,100.0 m | 3 |
| [`jinja-line14.aln.toml`](jinja-line14.aln.toml) | `line-14` | 2,288.3 m | 2 |
| [`jinja-line2.aln.toml`](jinja-line2.aln.toml) | `line-2` | 17,375.8 m | 17 |
| [`jinja-line3.aln.toml`](jinja-line3.aln.toml) | `line-3` | 12,787.3 m | 9 |
| [`jinja-line4.aln.toml`](jinja-line4.aln.toml) | `line-4` | 4,295.0 m | 3 |
| [`jinja-line5.aln.toml`](jinja-line5.aln.toml) | `line-5` | 6,128.7 m | 8 |
| [`jinja-line6.aln.toml`](jinja-line6.aln.toml) | `line-6` | 5,797.8 m | 4 |
| [`jinja-line7.aln.toml`](jinja-line7.aln.toml) | `line-7` | 4,815.8 m | 4 |
| [`jinja-line8.aln.toml`](jinja-line8.aln.toml) | `line-8` | 3,732.7 m | 3 |
| [`jinja-line9.aln.toml`](jinja-line9.aln.toml) | `line-9` | 2,638.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
