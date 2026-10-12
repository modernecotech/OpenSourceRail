# Bamako Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bamako-line1.aln.toml`](bamako-line1.aln.toml) | `line-1` | 47,755.4 m | 31 |
| [`bamako-line2.aln.toml`](bamako-line2.aln.toml) | `line-2` | 29,883.3 m | 16 |
| [`bamako-line3.aln.toml`](bamako-line3.aln.toml) | `line-3` | 16,316.1 m | 9 |
| [`bamako-line4.aln.toml`](bamako-line4.aln.toml) | `line-4` | 53,707.2 m | 30 |
| [`bamako-line5.aln.toml`](bamako-line5.aln.toml) | `line-5` | 19,825.3 m | 11 |
| [`bamako-line6.aln.toml`](bamako-line6.aln.toml) | `line-6` | 111,944.1 m | 59 |
| [`bamako-line7.aln.toml`](bamako-line7.aln.toml) | `line-7` | 8,005.8 m | 3 |
| [`bamako-line8.aln.toml`](bamako-line8.aln.toml) | `line-8` | 10,525.9 m | 4 |
| [`bamako-line9.aln.toml`](bamako-line9.aln.toml) | `line-9` | 14,829.3 m | 10 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
