# Chittagong Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`chittagong-line1.aln.toml`](chittagong-line1.aln.toml) | `line-1` | 47,133.3 m | 13 |
| [`chittagong-line10.aln.toml`](chittagong-line10.aln.toml) | `line-10` | 6,420.7 m | 2 |
| [`chittagong-line11.aln.toml`](chittagong-line11.aln.toml) | `line-11` | 7,764.4 m | 3 |
| [`chittagong-line12.aln.toml`](chittagong-line12.aln.toml) | `line-12` | 8,362.6 m | 3 |
| [`chittagong-line2.aln.toml`](chittagong-line2.aln.toml) | `line-2` | 31,869.9 m | 35 |
| [`chittagong-line3.aln.toml`](chittagong-line3.aln.toml) | `line-3` | 61,223.0 m | 40 |
| [`chittagong-line4.aln.toml`](chittagong-line4.aln.toml) | `line-4` | 34,084.9 m | 15 |
| [`chittagong-line5.aln.toml`](chittagong-line5.aln.toml) | `line-5` | 36,550.4 m | 14 |
| [`chittagong-line6.aln.toml`](chittagong-line6.aln.toml) | `line-6` | 26,473.7 m | 9 |
| [`chittagong-line7.aln.toml`](chittagong-line7.aln.toml) | `line-7` | 34,409.3 m | 14 |
| [`chittagong-line8.aln.toml`](chittagong-line8.aln.toml) | `line-8` | 72,764.1 m | 36 |
| [`chittagong-line9.aln.toml`](chittagong-line9.aln.toml) | `line-9` | 13,515.9 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
