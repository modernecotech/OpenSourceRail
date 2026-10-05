# Luanda Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`luanda-line1.aln.toml`](luanda-line1.aln.toml) | `line-1` | 50,339.9 m | 17 |
| [`luanda-line2.aln.toml`](luanda-line2.aln.toml) | `line-2` | 26,709.8 m | 10 |
| [`luanda-line3.aln.toml`](luanda-line3.aln.toml) | `line-3` | 38,251.5 m | 13 |
| [`luanda-line4.aln.toml`](luanda-line4.aln.toml) | `line-4` | 37,090.0 m | 13 |
| [`luanda-line5.aln.toml`](luanda-line5.aln.toml) | `line-5` | 35,910.9 m | 13 |
| [`luanda-line6.aln.toml`](luanda-line6.aln.toml) | `line-6` | 27,020.0 m | 9 |
| [`luanda-line7.aln.toml`](luanda-line7.aln.toml) | `line-7` | 31,491.6 m | 11 |
| [`luanda-line8.aln.toml`](luanda-line8.aln.toml) | `line-8` | 31,477.0 m | 13 |
| [`luanda-line9.aln.toml`](luanda-line9.aln.toml) | `line-9` | 65,807.8 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
