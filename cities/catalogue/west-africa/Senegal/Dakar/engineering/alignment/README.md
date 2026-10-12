# Dakar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dakar-line1.aln.toml`](dakar-line1.aln.toml) | `line-1` | 45,186.8 m | 11 |
| [`dakar-line2.aln.toml`](dakar-line2.aln.toml) | `line-2` | 28,520.4 m | 21 |
| [`dakar-line3.aln.toml`](dakar-line3.aln.toml) | `line-3` | 32,514.5 m | 10 |
| [`dakar-line4.aln.toml`](dakar-line4.aln.toml) | `line-4` | 29,298.9 m | 36 |
| [`dakar-line5.aln.toml`](dakar-line5.aln.toml) | `line-5` | 35,934.0 m | 23 |
| [`dakar-line6.aln.toml`](dakar-line6.aln.toml) | `line-6` | 71,555.8 m | 53 |
| [`dakar-line7.aln.toml`](dakar-line7.aln.toml) | `line-7` | 7,529.1 m | 4 |
| [`dakar-line8.aln.toml`](dakar-line8.aln.toml) | `line-8` | 11,364.3 m | 5 |
| [`dakar-line9.aln.toml`](dakar-line9.aln.toml) | `line-9` | 5,314.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
