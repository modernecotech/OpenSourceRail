# Karachi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karachi-line1.aln.toml`](karachi-line1.aln.toml) | `line-1` | 51,589.9 m | 29 |
| [`karachi-line10.aln.toml`](karachi-line10.aln.toml) | `line-10` | 7,528.9 m | 3 |
| [`karachi-line11.aln.toml`](karachi-line11.aln.toml) | `line-11` | 12,296.9 m | 5 |
| [`karachi-line12.aln.toml`](karachi-line12.aln.toml) | `line-12` | 11,469.7 m | 4 |
| [`karachi-line13.aln.toml`](karachi-line13.aln.toml) | `line-13` | 9,732.3 m | 3 |
| [`karachi-line14.aln.toml`](karachi-line14.aln.toml) | `line-14` | 6,532.7 m | 3 |
| [`karachi-line2.aln.toml`](karachi-line2.aln.toml) | `line-2` | 34,919.0 m | 17 |
| [`karachi-line3.aln.toml`](karachi-line3.aln.toml) | `line-3` | 46,503.2 m | 16 |
| [`karachi-line4.aln.toml`](karachi-line4.aln.toml) | `line-4` | 41,369.9 m | 18 |
| [`karachi-line5.aln.toml`](karachi-line5.aln.toml) | `line-5` | 50,706.8 m | 15 |
| [`karachi-line6.aln.toml`](karachi-line6.aln.toml) | `line-6` | 45,815.1 m | 29 |
| [`karachi-line7.aln.toml`](karachi-line7.aln.toml) | `line-7` | 41,001.0 m | 17 |
| [`karachi-line8.aln.toml`](karachi-line8.aln.toml) | `line-8` | 59,973.9 m | 27 |
| [`karachi-line9.aln.toml`](karachi-line9.aln.toml) | `line-9` | 146,041.7 m | 56 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
