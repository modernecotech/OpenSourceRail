# Colombo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`colombo-line1.aln.toml`](colombo-line1.aln.toml) | `line-1` | 29,410.3 m | 12 |
| [`colombo-line2.aln.toml`](colombo-line2.aln.toml) | `line-2` | 23,123.5 m | 10 |
| [`colombo-line3.aln.toml`](colombo-line3.aln.toml) | `line-3` | 37,524.0 m | 17 |
| [`colombo-line4.aln.toml`](colombo-line4.aln.toml) | `line-4` | 22,840.5 m | 11 |
| [`colombo-line5.aln.toml`](colombo-line5.aln.toml) | `line-5` | 29,185.1 m | 13 |
| [`colombo-line6.aln.toml`](colombo-line6.aln.toml) | `line-6` | 27,128.7 m | 13 |
| [`colombo-line7.aln.toml`](colombo-line7.aln.toml) | `line-7` | 25,100.9 m | 15 |
| [`colombo-line8.aln.toml`](colombo-line8.aln.toml) | `line-8` | 20,226.2 m | 9 |
| [`colombo-line9.aln.toml`](colombo-line9.aln.toml) | `line-9` | 71,145.2 m | 39 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
