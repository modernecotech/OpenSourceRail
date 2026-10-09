# Nakuru Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nakuru-line1.aln.toml`](nakuru-line1.aln.toml) | `line-1` | 11,455.8 m | 7 |
| [`nakuru-line10.aln.toml`](nakuru-line10.aln.toml) | `line-10` | 4,960.1 m | 4 |
| [`nakuru-line11.aln.toml`](nakuru-line11.aln.toml) | `line-11` | 3,640.2 m | 3 |
| [`nakuru-line12.aln.toml`](nakuru-line12.aln.toml) | `line-12` | 7,475.5 m | 5 |
| [`nakuru-line13.aln.toml`](nakuru-line13.aln.toml) | `line-13` | 3,635.0 m | 3 |
| [`nakuru-line2.aln.toml`](nakuru-line2.aln.toml) | `line-2` | 20,413.1 m | 13 |
| [`nakuru-line3.aln.toml`](nakuru-line3.aln.toml) | `line-3` | 16,235.0 m | 11 |
| [`nakuru-line4.aln.toml`](nakuru-line4.aln.toml) | `line-4` | 2,370.5 m | 3 |
| [`nakuru-line5.aln.toml`](nakuru-line5.aln.toml) | `line-5` | 6,909.2 m | 5 |
| [`nakuru-line6.aln.toml`](nakuru-line6.aln.toml) | `line-6` | 2,671.4 m | 2 |
| [`nakuru-line7.aln.toml`](nakuru-line7.aln.toml) | `line-7` | 6,130.4 m | 4 |
| [`nakuru-line8.aln.toml`](nakuru-line8.aln.toml) | `line-8` | 5,812.2 m | 4 |
| [`nakuru-line9.aln.toml`](nakuru-line9.aln.toml) | `line-9` | 3,775.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
