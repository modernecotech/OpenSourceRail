# San-Salvador Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`san-salvador-line1.aln.toml`](san-salvador-line1.aln.toml) | `line-1` | 27,197.7 m | 12 |
| [`san-salvador-line2.aln.toml`](san-salvador-line2.aln.toml) | `line-2` | 40,925.1 m | 11 |
| [`san-salvador-line3.aln.toml`](san-salvador-line3.aln.toml) | `line-3` | 40,647.8 m | 16 |
| [`san-salvador-line4.aln.toml`](san-salvador-line4.aln.toml) | `line-4` | 35,921.9 m | 11 |
| [`san-salvador-line5.aln.toml`](san-salvador-line5.aln.toml) | `line-5` | 29,506.3 m | 14 |
| [`san-salvador-line6.aln.toml`](san-salvador-line6.aln.toml) | `line-6` | 74,786.0 m | 19 |
| [`san-salvador-line7.aln.toml`](san-salvador-line7.aln.toml) | `line-7` | 6,642.2 m | 2 |
| [`san-salvador-line8.aln.toml`](san-salvador-line8.aln.toml) | `line-8` | 5,057.3 m | 2 |
| [`san-salvador-line9.aln.toml`](san-salvador-line9.aln.toml) | `line-9` | 11,014.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
