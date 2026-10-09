# Tetouan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tetouan-line1.aln.toml`](tetouan-line1.aln.toml) | `line-1` | 16,053.1 m | 11 |
| [`tetouan-line2.aln.toml`](tetouan-line2.aln.toml) | `line-2` | 20,024.8 m | 13 |
| [`tetouan-line3.aln.toml`](tetouan-line3.aln.toml) | `line-3` | 11,732.8 m | 8 |
| [`tetouan-line4.aln.toml`](tetouan-line4.aln.toml) | `line-4` | 6,338.4 m | 5 |
| [`tetouan-line5.aln.toml`](tetouan-line5.aln.toml) | `line-5` | 6,292.8 m | 4 |
| [`tetouan-line6.aln.toml`](tetouan-line6.aln.toml) | `line-6` | 6,469.0 m | 5 |
| [`tetouan-line7.aln.toml`](tetouan-line7.aln.toml) | `line-7` | 5,442.2 m | 4 |
| [`tetouan-line8.aln.toml`](tetouan-line8.aln.toml) | `line-8` | 3,797.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
