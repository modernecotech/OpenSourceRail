# Yangon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yangon-line1.aln.toml`](yangon-line1.aln.toml) | `line-1` | 35,759.6 m | 17 |
| [`yangon-line2.aln.toml`](yangon-line2.aln.toml) | `line-2` | 31,787.9 m | 14 |
| [`yangon-line3.aln.toml`](yangon-line3.aln.toml) | `line-3` | 59,438.5 m | 33 |
| [`yangon-line4.aln.toml`](yangon-line4.aln.toml) | `line-4` | 53,999.3 m | 18 |
| [`yangon-line5.aln.toml`](yangon-line5.aln.toml) | `line-5` | 48,451.7 m | 27 |
| [`yangon-line6.aln.toml`](yangon-line6.aln.toml) | `line-6` | 35,136.0 m | 14 |
| [`yangon-line7.aln.toml`](yangon-line7.aln.toml) | `line-7` | 36,122.0 m | 21 |
| [`yangon-line8.aln.toml`](yangon-line8.aln.toml) | `line-8` | 51,626.0 m | 33 |
| [`yangon-line9.aln.toml`](yangon-line9.aln.toml) | `line-9` | 95,474.2 m | 52 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
