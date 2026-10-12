# Medina Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`medina-line1.aln.toml`](medina-line1.aln.toml) | `line-1` | 32,733.5 m | 9 |
| [`medina-line2.aln.toml`](medina-line2.aln.toml) | `line-2` | 19,119.4 m | 7 |
| [`medina-line3.aln.toml`](medina-line3.aln.toml) | `line-3` | 22,677.5 m | 8 |
| [`medina-line4.aln.toml`](medina-line4.aln.toml) | `line-4` | 25,534.4 m | 8 |
| [`medina-line5.aln.toml`](medina-line5.aln.toml) | `line-5` | 19,443.1 m | 7 |
| [`medina-line6.aln.toml`](medina-line6.aln.toml) | `line-6` | 62,198.6 m | 16 |
| [`medina-line7.aln.toml`](medina-line7.aln.toml) | `line-7` | 5,742.4 m | 3 |
| [`medina-line8.aln.toml`](medina-line8.aln.toml) | `line-8` | 9,682.6 m | 3 |
| [`medina-line9.aln.toml`](medina-line9.aln.toml) | `line-9` | 5,635.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
