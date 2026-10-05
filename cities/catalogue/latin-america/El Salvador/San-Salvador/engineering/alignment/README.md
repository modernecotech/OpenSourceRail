# San-Salvador Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`san-salvador-line1.aln.toml`](san-salvador-line1.aln.toml) | `line-1` | 27,294.6 m | 11 |
| [`san-salvador-line2.aln.toml`](san-salvador-line2.aln.toml) | `line-2` | 32,129.7 m | 12 |
| [`san-salvador-line3.aln.toml`](san-salvador-line3.aln.toml) | `line-3` | 34,348.7 m | 10 |
| [`san-salvador-line4.aln.toml`](san-salvador-line4.aln.toml) | `line-4` | 36,195.1 m | 12 |
| [`san-salvador-line5.aln.toml`](san-salvador-line5.aln.toml) | `line-5` | 29,744.3 m | 9 |
| [`san-salvador-line6.aln.toml`](san-salvador-line6.aln.toml) | `line-6` | 72,382.4 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
