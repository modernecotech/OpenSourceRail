# Bloemfontein Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bloemfontein-line1.aln.toml`](bloemfontein-line1.aln.toml) | `line-1` | 23,847.8 m | 15 |
| [`bloemfontein-line2.aln.toml`](bloemfontein-line2.aln.toml) | `line-2` | 22,291.1 m | 13 |
| [`bloemfontein-line3.aln.toml`](bloemfontein-line3.aln.toml) | `line-3` | 12,414.7 m | 8 |
| [`bloemfontein-line4.aln.toml`](bloemfontein-line4.aln.toml) | `line-4` | 3,514.8 m | 3 |
| [`bloemfontein-line5.aln.toml`](bloemfontein-line5.aln.toml) | `line-5` | 3,214.6 m | 3 |
| [`bloemfontein-line6.aln.toml`](bloemfontein-line6.aln.toml) | `line-6` | 4,161.6 m | 3 |
| [`bloemfontein-line7.aln.toml`](bloemfontein-line7.aln.toml) | `line-7` | 4,909.8 m | 4 |
| [`bloemfontein-line8.aln.toml`](bloemfontein-line8.aln.toml) | `line-8` | 2,529.6 m | 2 |
| [`bloemfontein-line9.aln.toml`](bloemfontein-line9.aln.toml) | `line-9` | 4,568.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
