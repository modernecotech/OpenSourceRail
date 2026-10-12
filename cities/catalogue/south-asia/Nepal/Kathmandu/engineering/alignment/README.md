# Kathmandu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kathmandu-line1.aln.toml`](kathmandu-line1.aln.toml) | `line-1` | 38,145.2 m | 35 |
| [`kathmandu-line2.aln.toml`](kathmandu-line2.aln.toml) | `line-2` | 29,416.1 m | 17 |
| [`kathmandu-line3.aln.toml`](kathmandu-line3.aln.toml) | `line-3` | 22,047.7 m | 23 |
| [`kathmandu-line4.aln.toml`](kathmandu-line4.aln.toml) | `line-4` | 25,121.2 m | 16 |
| [`kathmandu-line5.aln.toml`](kathmandu-line5.aln.toml) | `line-5` | 31,461.2 m | 19 |
| [`kathmandu-line6.aln.toml`](kathmandu-line6.aln.toml) | `line-6` | 56,419.6 m | 25 |
| [`kathmandu-line7.aln.toml`](kathmandu-line7.aln.toml) | `line-7` | 6,311.9 m | 2 |
| [`kathmandu-line8.aln.toml`](kathmandu-line8.aln.toml) | `line-8` | 24,113.5 m | 8 |
| [`kathmandu-line9.aln.toml`](kathmandu-line9.aln.toml) | `line-9` | 4,860.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
