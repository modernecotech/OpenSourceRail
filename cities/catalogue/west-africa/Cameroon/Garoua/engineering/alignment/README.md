# Garoua Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`garoua-line1.aln.toml`](garoua-line1.aln.toml) | `line-1` | 10,218.5 m | 7 |
| [`garoua-line2.aln.toml`](garoua-line2.aln.toml) | `line-2` | 7,924.5 m | 6 |
| [`garoua-line3.aln.toml`](garoua-line3.aln.toml) | `line-3` | 7,012.3 m | 7 |
| [`garoua-line4.aln.toml`](garoua-line4.aln.toml) | `line-4` | 4,638.7 m | 4 |
| [`garoua-line5.aln.toml`](garoua-line5.aln.toml) | `line-5` | 5,470.4 m | 4 |
| [`garoua-line6.aln.toml`](garoua-line6.aln.toml) | `line-6` | 3,517.3 m | 3 |
| [`garoua-line7.aln.toml`](garoua-line7.aln.toml) | `line-7` | 5,510.8 m | 4 |
| [`garoua-line8.aln.toml`](garoua-line8.aln.toml) | `line-8` | 4,846.8 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
