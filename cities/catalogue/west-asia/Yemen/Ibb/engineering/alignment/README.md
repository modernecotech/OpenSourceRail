# Ibb Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ibb-line1.aln.toml`](ibb-line1.aln.toml) | `line-1` | 10,413.4 m | 7 |
| [`ibb-line10.aln.toml`](ibb-line10.aln.toml) | `line-10` | 2,488.8 m | 2 |
| [`ibb-line11.aln.toml`](ibb-line11.aln.toml) | `line-11` | 3,609.0 m | 3 |
| [`ibb-line2.aln.toml`](ibb-line2.aln.toml) | `line-2` | 17,762.8 m | 11 |
| [`ibb-line3.aln.toml`](ibb-line3.aln.toml) | `line-3` | 11,322.2 m | 7 |
| [`ibb-line4.aln.toml`](ibb-line4.aln.toml) | `line-4` | 3,219.7 m | 3 |
| [`ibb-line5.aln.toml`](ibb-line5.aln.toml) | `line-5` | 2,643.3 m | 2 |
| [`ibb-line6.aln.toml`](ibb-line6.aln.toml) | `line-6` | 10,814.3 m | 6 |
| [`ibb-line7.aln.toml`](ibb-line7.aln.toml) | `line-7` | 3,749.9 m | 3 |
| [`ibb-line8.aln.toml`](ibb-line8.aln.toml) | `line-8` | 7,792.7 m | 5 |
| [`ibb-line9.aln.toml`](ibb-line9.aln.toml) | `line-9` | 3,691.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
