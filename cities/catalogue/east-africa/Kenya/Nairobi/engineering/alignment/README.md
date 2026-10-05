# Nairobi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nairobi-line1.aln.toml`](nairobi-line1.aln.toml) | `line-1` | 51,611.6 m | 17 |
| [`nairobi-line2.aln.toml`](nairobi-line2.aln.toml) | `line-2` | 43,850.7 m | 14 |
| [`nairobi-line3.aln.toml`](nairobi-line3.aln.toml) | `line-3` | 44,218.7 m | 13 |
| [`nairobi-line4.aln.toml`](nairobi-line4.aln.toml) | `line-4` | 27,808.4 m | 9 |
| [`nairobi-line5.aln.toml`](nairobi-line5.aln.toml) | `line-5` | 42,594.8 m | 10 |
| [`nairobi-line6.aln.toml`](nairobi-line6.aln.toml) | `line-6` | 55,092.2 m | 16 |
| [`nairobi-line7.aln.toml`](nairobi-line7.aln.toml) | `line-7` | 46,743.3 m | 14 |
| [`nairobi-line8.aln.toml`](nairobi-line8.aln.toml) | `line-8` | 38,904.1 m | 10 |
| [`nairobi-line9.aln.toml`](nairobi-line9.aln.toml) | `line-9` | 100,459.5 m | 29 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
