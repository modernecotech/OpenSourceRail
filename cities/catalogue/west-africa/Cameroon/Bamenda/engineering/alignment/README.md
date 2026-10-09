# Bamenda Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bamenda-line1.aln.toml`](bamenda-line1.aln.toml) | `line-1` | 16,696.3 m | 13 |
| [`bamenda-line10.aln.toml`](bamenda-line10.aln.toml) | `line-10` | 2,035.4 m | 2 |
| [`bamenda-line11.aln.toml`](bamenda-line11.aln.toml) | `line-11` | 8,555.8 m | 7 |
| [`bamenda-line12.aln.toml`](bamenda-line12.aln.toml) | `line-12` | 3,405.9 m | 3 |
| [`bamenda-line13.aln.toml`](bamenda-line13.aln.toml) | `line-13` | 2,085.1 m | 2 |
| [`bamenda-line2.aln.toml`](bamenda-line2.aln.toml) | `line-2` | 14,396.4 m | 10 |
| [`bamenda-line3.aln.toml`](bamenda-line3.aln.toml) | `line-3` | 10,479.0 m | 9 |
| [`bamenda-line4.aln.toml`](bamenda-line4.aln.toml) | `line-4` | 3,611.0 m | 3 |
| [`bamenda-line5.aln.toml`](bamenda-line5.aln.toml) | `line-5` | 2,819.7 m | 2 |
| [`bamenda-line6.aln.toml`](bamenda-line6.aln.toml) | `line-6` | 2,976.0 m | 3 |
| [`bamenda-line7.aln.toml`](bamenda-line7.aln.toml) | `line-7` | 4,627.6 m | 3 |
| [`bamenda-line8.aln.toml`](bamenda-line8.aln.toml) | `line-8` | 2,760.5 m | 2 |
| [`bamenda-line9.aln.toml`](bamenda-line9.aln.toml) | `line-9` | 8,590.8 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
