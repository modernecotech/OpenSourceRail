# Mbale Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mbale-line1.aln.toml`](mbale-line1.aln.toml) | `line-1` | 7,376.0 m | 6 |
| [`mbale-line2.aln.toml`](mbale-line2.aln.toml) | `line-2` | 10,250.9 m | 7 |
| [`mbale-line3.aln.toml`](mbale-line3.aln.toml) | `line-3` | 3,592.0 m | 4 |
| [`mbale-line4.aln.toml`](mbale-line4.aln.toml) | `line-4` | 2,768.5 m | 2 |
| [`mbale-line5.aln.toml`](mbale-line5.aln.toml) | `line-5` | 5,245.9 m | 4 |
| [`mbale-line6.aln.toml`](mbale-line6.aln.toml) | `line-6` | 3,865.1 m | 3 |
| [`mbale-line7.aln.toml`](mbale-line7.aln.toml) | `line-7` | 3,762.5 m | 3 |
| [`mbale-line8.aln.toml`](mbale-line8.aln.toml) | `line-8` | 3,000.2 m | 3 |
| [`mbale-line9.aln.toml`](mbale-line9.aln.toml) | `line-9` | 2,029.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
