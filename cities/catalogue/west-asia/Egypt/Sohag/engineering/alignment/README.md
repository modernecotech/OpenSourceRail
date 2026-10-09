# Sohag Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sohag-line1.aln.toml`](sohag-line1.aln.toml) | `line-1` | 6,592.5 m | 6 |
| [`sohag-line2.aln.toml`](sohag-line2.aln.toml) | `line-2` | 12,854.3 m | 7 |
| [`sohag-line3.aln.toml`](sohag-line3.aln.toml) | `line-3` | 14,760.1 m | 9 |
| [`sohag-line4.aln.toml`](sohag-line4.aln.toml) | `line-4` | 6,011.9 m | 5 |
| [`sohag-line5.aln.toml`](sohag-line5.aln.toml) | `line-5` | 9,312.7 m | 6 |
| [`sohag-line6.aln.toml`](sohag-line6.aln.toml) | `line-6` | 6,302.4 m | 4 |
| [`sohag-line7.aln.toml`](sohag-line7.aln.toml) | `line-7` | 8,213.6 m | 5 |
| [`sohag-line8.aln.toml`](sohag-line8.aln.toml) | `line-8` | 3,436.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
