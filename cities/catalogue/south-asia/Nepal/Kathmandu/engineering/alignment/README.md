# Kathmandu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kathmandu-line1.aln.toml`](kathmandu-line1.aln.toml) | `line-1` | 37,445.6 m | 11 |
| [`kathmandu-line2.aln.toml`](kathmandu-line2.aln.toml) | `line-2` | 28,918.1 m | 11 |
| [`kathmandu-line3.aln.toml`](kathmandu-line3.aln.toml) | `line-3` | 20,217.7 m | 8 |
| [`kathmandu-line4.aln.toml`](kathmandu-line4.aln.toml) | `line-4` | 23,329.2 m | 9 |
| [`kathmandu-line5.aln.toml`](kathmandu-line5.aln.toml) | `line-5` | 31,422.1 m | 10 |
| [`kathmandu-line6.aln.toml`](kathmandu-line6.aln.toml) | `line-6` | 55,932.9 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
