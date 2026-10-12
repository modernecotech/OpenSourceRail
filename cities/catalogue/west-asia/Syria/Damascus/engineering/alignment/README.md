# Damascus Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`damascus-line1.aln.toml`](damascus-line1.aln.toml) | `line-1` | 28,545.7 m | 17 |
| [`damascus-line2.aln.toml`](damascus-line2.aln.toml) | `line-2` | 28,911.6 m | 10 |
| [`damascus-line3.aln.toml`](damascus-line3.aln.toml) | `line-3` | 29,375.2 m | 10 |
| [`damascus-line4.aln.toml`](damascus-line4.aln.toml) | `line-4` | 26,713.9 m | 13 |
| [`damascus-line5.aln.toml`](damascus-line5.aln.toml) | `line-5` | 30,114.7 m | 24 |
| [`damascus-line6.aln.toml`](damascus-line6.aln.toml) | `line-6` | 67,734.2 m | 29 |
| [`damascus-line7.aln.toml`](damascus-line7.aln.toml) | `line-7` | 5,516.1 m | 3 |
| [`damascus-line8.aln.toml`](damascus-line8.aln.toml) | `line-8` | 4,944.2 m | 3 |
| [`damascus-line9.aln.toml`](damascus-line9.aln.toml) | `line-9` | 6,298.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
