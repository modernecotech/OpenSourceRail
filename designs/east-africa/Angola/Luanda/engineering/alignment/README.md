# Luanda Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`luanda-line1.aln.toml`](luanda-line1.aln.toml) | `line-1` | 58,631.9 m | 34 |
| [`luanda-line2.aln.toml`](luanda-line2.aln.toml) | `line-2` | 29,998.5 m | 19 |
| [`luanda-line3.aln.toml`](luanda-line3.aln.toml) | `line-3` | 43,871.7 m | 26 |
| [`luanda-line4.aln.toml`](luanda-line4.aln.toml) | `line-4` | 42,563.3 m | 22 |
| [`luanda-line5.aln.toml`](luanda-line5.aln.toml) | `line-5` | 39,942.8 m | 22 |
| [`luanda-line6.aln.toml`](luanda-line6.aln.toml) | `line-6` | 31,132.9 m | 17 |
| [`luanda-line7.aln.toml`](luanda-line7.aln.toml) | `line-7` | 33,940.2 m | 19 |
| [`luanda-line8.aln.toml`](luanda-line8.aln.toml) | `line-8` | 32,878.6 m | 19 |
| [`luanda-line9.aln.toml`](luanda-line9.aln.toml) | `line-9` | 77,428.4 m | 51 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
