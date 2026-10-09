# Kisangani Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kisangani-line1.aln.toml`](kisangani-line1.aln.toml) | `line-1` | 22,214.6 m | 21 |
| [`kisangani-line2.aln.toml`](kisangani-line2.aln.toml) | `line-2` | 13,784.5 m | 26 |
| [`kisangani-line3.aln.toml`](kisangani-line3.aln.toml) | `line-3` | 3,649.6 m | 3 |
| [`kisangani-line4.aln.toml`](kisangani-line4.aln.toml) | `line-4` | 3,635.6 m | 3 |
| [`kisangani-line5.aln.toml`](kisangani-line5.aln.toml) | `line-5` | 5,933.9 m | 7 |
| [`kisangani-line6.aln.toml`](kisangani-line6.aln.toml) | `line-6` | 3,369.4 m | 3 |
| [`kisangani-line7.aln.toml`](kisangani-line7.aln.toml) | `line-7` | 7,102.8 m | 4 |
| [`kisangani-line8.aln.toml`](kisangani-line8.aln.toml) | `line-8` | 4,471.4 m | 3 |
| [`kisangani-line9.aln.toml`](kisangani-line9.aln.toml) | `line-9` | 8,664.7 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
