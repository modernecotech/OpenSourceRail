# Hodeidah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hodeidah-line1.aln.toml`](hodeidah-line1.aln.toml) | `line-1` | 7,461.6 m | 6 |
| [`hodeidah-line2.aln.toml`](hodeidah-line2.aln.toml) | `line-2` | 9,824.0 m | 6 |
| [`hodeidah-line3.aln.toml`](hodeidah-line3.aln.toml) | `line-3` | 6,141.3 m | 5 |
| [`hodeidah-line4.aln.toml`](hodeidah-line4.aln.toml) | `line-4` | 2,403.7 m | 2 |
| [`hodeidah-line5.aln.toml`](hodeidah-line5.aln.toml) | `line-5` | 9,201.0 m | 6 |
| [`hodeidah-line6.aln.toml`](hodeidah-line6.aln.toml) | `line-6` | 2,083.3 m | 2 |
| [`hodeidah-line7.aln.toml`](hodeidah-line7.aln.toml) | `line-7` | 2,681.9 m | 2 |
| [`hodeidah-line8.aln.toml`](hodeidah-line8.aln.toml) | `line-8` | 4,085.0 m | 3 |
| [`hodeidah-line9.aln.toml`](hodeidah-line9.aln.toml) | `line-9` | 2,700.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
