# Yangon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yangon-line1.aln.toml`](yangon-line1.aln.toml) | `line-1` | 41,016.3 m | 24 |
| [`yangon-line2.aln.toml`](yangon-line2.aln.toml) | `line-2` | 36,832.2 m | 21 |
| [`yangon-line3.aln.toml`](yangon-line3.aln.toml) | `line-3` | 47,017.9 m | 26 |
| [`yangon-line4.aln.toml`](yangon-line4.aln.toml) | `line-4` | 51,687.2 m | 25 |
| [`yangon-line5.aln.toml`](yangon-line5.aln.toml) | `line-5` | 41,982.6 m | 23 |
| [`yangon-line6.aln.toml`](yangon-line6.aln.toml) | `line-6` | 37,277.5 m | 20 |
| [`yangon-line7.aln.toml`](yangon-line7.aln.toml) | `line-7` | 43,467.4 m | 25 |
| [`yangon-line8.aln.toml`](yangon-line8.aln.toml) | `line-8` | 36,320.8 m | 19 |
| [`yangon-line9.aln.toml`](yangon-line9.aln.toml) | `line-9` | 82,485.7 m | 57 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
