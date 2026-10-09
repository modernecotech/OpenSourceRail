# Kigoma Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kigoma-line1.aln.toml`](kigoma-line1.aln.toml) | `line-1` | 9,195.5 m | 6 |
| [`kigoma-line2.aln.toml`](kigoma-line2.aln.toml) | `line-2` | 11,549.4 m | 8 |
| [`kigoma-line3.aln.toml`](kigoma-line3.aln.toml) | `line-3` | 6,067.9 m | 5 |
| [`kigoma-line4.aln.toml`](kigoma-line4.aln.toml) | `line-4` | 3,485.7 m | 3 |
| [`kigoma-line5.aln.toml`](kigoma-line5.aln.toml) | `line-5` | 3,371.3 m | 3 |
| [`kigoma-line6.aln.toml`](kigoma-line6.aln.toml) | `line-6` | 6,990.7 m | 5 |
| [`kigoma-line7.aln.toml`](kigoma-line7.aln.toml) | `line-7` | 5,445.6 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
