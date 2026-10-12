# Beirut Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`beirut-line1.aln.toml`](beirut-line1.aln.toml) | `line-1` | 32,921.6 m | 16 |
| [`beirut-line2.aln.toml`](beirut-line2.aln.toml) | `line-2` | 13,721.4 m | 7 |
| [`beirut-line3.aln.toml`](beirut-line3.aln.toml) | `line-3` | 21,083.2 m | 8 |
| [`beirut-line4.aln.toml`](beirut-line4.aln.toml) | `line-4` | 17,375.9 m | 9 |
| [`beirut-line5.aln.toml`](beirut-line5.aln.toml) | `line-5` | 18,494.1 m | 9 |
| [`beirut-line6.aln.toml`](beirut-line6.aln.toml) | `line-6` | 36,740.5 m | 16 |
| [`beirut-line7.aln.toml`](beirut-line7.aln.toml) | `line-7` | 5,600.7 m | 3 |
| [`beirut-line8.aln.toml`](beirut-line8.aln.toml) | `line-8` | 12,783.1 m | 5 |
| [`beirut-line9.aln.toml`](beirut-line9.aln.toml) | `line-9` | 6,038.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
