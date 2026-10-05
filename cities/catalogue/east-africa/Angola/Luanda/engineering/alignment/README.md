# Luanda Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`luanda-line1.aln.toml`](luanda-line1.aln.toml) | `line-1` | 52,373.1 m | 19 |
| [`luanda-line2.aln.toml`](luanda-line2.aln.toml) | `line-2` | 26,849.5 m | 12 |
| [`luanda-line3.aln.toml`](luanda-line3.aln.toml) | `line-3` | 39,213.0 m | 14 |
| [`luanda-line4.aln.toml`](luanda-line4.aln.toml) | `line-4` | 47,020.9 m | 18 |
| [`luanda-line5.aln.toml`](luanda-line5.aln.toml) | `line-5` | 37,911.9 m | 16 |
| [`luanda-line6.aln.toml`](luanda-line6.aln.toml) | `line-6` | 27,065.5 m | 15 |
| [`luanda-line7.aln.toml`](luanda-line7.aln.toml) | `line-7` | 31,723.9 m | 13 |
| [`luanda-line8.aln.toml`](luanda-line8.aln.toml) | `line-8` | 31,655.0 m | 17 |
| [`luanda-line9.aln.toml`](luanda-line9.aln.toml) | `line-9` | 65,807.8 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
