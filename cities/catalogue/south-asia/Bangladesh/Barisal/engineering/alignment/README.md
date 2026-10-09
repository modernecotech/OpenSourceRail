# Barisal Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`barisal-line1.aln.toml`](barisal-line1.aln.toml) | `line-1` | 13,725.7 m | 7 |
| [`barisal-line10.aln.toml`](barisal-line10.aln.toml) | `line-10` | 3,497.3 m | 6 |
| [`barisal-line2.aln.toml`](barisal-line2.aln.toml) | `line-2` | 16,002.5 m | 10 |
| [`barisal-line3.aln.toml`](barisal-line3.aln.toml) | `line-3` | 24,670.2 m | 17 |
| [`barisal-line4.aln.toml`](barisal-line4.aln.toml) | `line-4` | 3,836.7 m | 6 |
| [`barisal-line5.aln.toml`](barisal-line5.aln.toml) | `line-5` | 3,537.6 m | 4 |
| [`barisal-line6.aln.toml`](barisal-line6.aln.toml) | `line-6` | 5,279.3 m | 4 |
| [`barisal-line7.aln.toml`](barisal-line7.aln.toml) | `line-7` | 3,280.5 m | 3 |
| [`barisal-line8.aln.toml`](barisal-line8.aln.toml) | `line-8` | 12,344.4 m | 7 |
| [`barisal-line9.aln.toml`](barisal-line9.aln.toml) | `line-9` | 5,327.2 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
