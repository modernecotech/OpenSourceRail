# Latakia Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`latakia-line1.aln.toml`](latakia-line1.aln.toml) | `line-1` | 13,266.5 m | 9 |
| [`latakia-line10.aln.toml`](latakia-line10.aln.toml) | `line-10` | 3,845.6 m | 3 |
| [`latakia-line2.aln.toml`](latakia-line2.aln.toml) | `line-2` | 6,690.8 m | 4 |
| [`latakia-line3.aln.toml`](latakia-line3.aln.toml) | `line-3` | 9,265.2 m | 6 |
| [`latakia-line4.aln.toml`](latakia-line4.aln.toml) | `line-4` | 5,221.0 m | 4 |
| [`latakia-line5.aln.toml`](latakia-line5.aln.toml) | `line-5` | 4,758.8 m | 3 |
| [`latakia-line6.aln.toml`](latakia-line6.aln.toml) | `line-6` | 3,589.4 m | 3 |
| [`latakia-line7.aln.toml`](latakia-line7.aln.toml) | `line-7` | 4,538.7 m | 3 |
| [`latakia-line8.aln.toml`](latakia-line8.aln.toml) | `line-8` | 2,584.8 m | 2 |
| [`latakia-line9.aln.toml`](latakia-line9.aln.toml) | `line-9` | 3,092.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
