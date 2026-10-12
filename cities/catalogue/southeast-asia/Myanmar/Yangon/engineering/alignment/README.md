# Yangon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yangon-line1.aln.toml`](yangon-line1.aln.toml) | `line-1` | 44,909.2 m | 19 |
| [`yangon-line10.aln.toml`](yangon-line10.aln.toml) | `line-10` | 8,310.4 m | 4 |
| [`yangon-line11.aln.toml`](yangon-line11.aln.toml) | `line-11` | 7,609.7 m | 5 |
| [`yangon-line12.aln.toml`](yangon-line12.aln.toml) | `line-12` | 12,280.4 m | 6 |
| [`yangon-line13.aln.toml`](yangon-line13.aln.toml) | `line-13` | 15,105.9 m | 5 |
| [`yangon-line14.aln.toml`](yangon-line14.aln.toml) | `line-14` | 7,839.1 m | 3 |
| [`yangon-line2.aln.toml`](yangon-line2.aln.toml) | `line-2` | 40,371.5 m | 16 |
| [`yangon-line3.aln.toml`](yangon-line3.aln.toml) | `line-3` | 59,438.5 m | 31 |
| [`yangon-line4.aln.toml`](yangon-line4.aln.toml) | `line-4` | 52,083.7 m | 17 |
| [`yangon-line5.aln.toml`](yangon-line5.aln.toml) | `line-5` | 48,480.0 m | 25 |
| [`yangon-line6.aln.toml`](yangon-line6.aln.toml) | `line-6` | 38,567.4 m | 12 |
| [`yangon-line7.aln.toml`](yangon-line7.aln.toml) | `line-7` | 48,366.1 m | 24 |
| [`yangon-line8.aln.toml`](yangon-line8.aln.toml) | `line-8` | 56,199.7 m | 32 |
| [`yangon-line9.aln.toml`](yangon-line9.aln.toml) | `line-9` | 102,604.3 m | 53 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
