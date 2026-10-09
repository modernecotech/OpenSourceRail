# Biratnagar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`biratnagar-line1.aln.toml`](biratnagar-line1.aln.toml) | `line-1` | 12,018.5 m | 7 |
| [`biratnagar-line2.aln.toml`](biratnagar-line2.aln.toml) | `line-2` | 4,279.4 m | 3 |
| [`biratnagar-line3.aln.toml`](biratnagar-line3.aln.toml) | `line-3` | 9,044.9 m | 6 |
| [`biratnagar-line4.aln.toml`](biratnagar-line4.aln.toml) | `line-4` | 6,385.6 m | 4 |
| [`biratnagar-line5.aln.toml`](biratnagar-line5.aln.toml) | `line-5` | 9,157.9 m | 5 |
| [`biratnagar-line6.aln.toml`](biratnagar-line6.aln.toml) | `line-6` | 8,529.2 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
