# Comilla Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`comilla-line1.aln.toml`](comilla-line1.aln.toml) | `line-1` | 15,612.8 m | 9 |
| [`comilla-line2.aln.toml`](comilla-line2.aln.toml) | `line-2` | 16,814.5 m | 10 |
| [`comilla-line3.aln.toml`](comilla-line3.aln.toml) | `line-3` | 11,613.9 m | 8 |
| [`comilla-line4.aln.toml`](comilla-line4.aln.toml) | `line-4` | 2,950.2 m | 3 |
| [`comilla-line5.aln.toml`](comilla-line5.aln.toml) | `line-5` | 7,041.6 m | 8 |
| [`comilla-line6.aln.toml`](comilla-line6.aln.toml) | `line-6` | 2,924.2 m | 2 |
| [`comilla-line7.aln.toml`](comilla-line7.aln.toml) | `line-7` | 7,682.9 m | 4 |
| [`comilla-line8.aln.toml`](comilla-line8.aln.toml) | `line-8` | 15,041.3 m | 11 |
| [`comilla-line9.aln.toml`](comilla-line9.aln.toml) | `line-9` | 7,268.4 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
