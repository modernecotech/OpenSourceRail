# Yangon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yangon-line1.aln.toml`](yangon-line1.aln.toml) | `line-1` | 34,884.4 m | 11 |
| [`yangon-line2.aln.toml`](yangon-line2.aln.toml) | `line-2` | 30,925.3 m | 10 |
| [`yangon-line3.aln.toml`](yangon-line3.aln.toml) | `line-3` | 38,707.4 m | 12 |
| [`yangon-line4.aln.toml`](yangon-line4.aln.toml) | `line-4` | 47,218.4 m | 15 |
| [`yangon-line5.aln.toml`](yangon-line5.aln.toml) | `line-5` | 37,696.6 m | 13 |
| [`yangon-line6.aln.toml`](yangon-line6.aln.toml) | `line-6` | 34,503.2 m | 11 |
| [`yangon-line7.aln.toml`](yangon-line7.aln.toml) | `line-7` | 35,305.0 m | 12 |
| [`yangon-line8.aln.toml`](yangon-line8.aln.toml) | `line-8` | 32,582.0 m | 12 |
| [`yangon-line9.aln.toml`](yangon-line9.aln.toml) | `line-9` | 71,269.1 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
