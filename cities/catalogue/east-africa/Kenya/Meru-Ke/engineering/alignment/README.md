# Meru-Ke Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`meru-ke-line1.aln.toml`](meru-ke-line1.aln.toml) | `line-1` | 11,477.0 m | 8 |
| [`meru-ke-line2.aln.toml`](meru-ke-line2.aln.toml) | `line-2` | 3,221.9 m | 3 |
| [`meru-ke-line3.aln.toml`](meru-ke-line3.aln.toml) | `line-3` | 8,080.1 m | 5 |
| [`meru-ke-line4.aln.toml`](meru-ke-line4.aln.toml) | `line-4` | 2,100.8 m | 2 |
| [`meru-ke-line5.aln.toml`](meru-ke-line5.aln.toml) | `line-5` | 3,382.7 m | 3 |
| [`meru-ke-line6.aln.toml`](meru-ke-line6.aln.toml) | `line-6` | 2,507.4 m | 2 |
| [`meru-ke-line7.aln.toml`](meru-ke-line7.aln.toml) | `line-7` | 7,291.3 m | 5 |
| [`meru-ke-line8.aln.toml`](meru-ke-line8.aln.toml) | `line-8` | 2,900.5 m | 2 |
| [`meru-ke-line9.aln.toml`](meru-ke-line9.aln.toml) | `line-9` | 4,517.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
