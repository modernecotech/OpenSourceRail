# Lobito Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lobito-line1.aln.toml`](lobito-line1.aln.toml) | `line-1` | 19,720.7 m | 12 |
| [`lobito-line2.aln.toml`](lobito-line2.aln.toml) | `line-2` | 5,303.7 m | 6 |
| [`lobito-line3.aln.toml`](lobito-line3.aln.toml) | `line-3` | 5,719.6 m | 5 |
| [`lobito-line4.aln.toml`](lobito-line4.aln.toml) | `line-4` | 4,452.0 m | 4 |
| [`lobito-line5.aln.toml`](lobito-line5.aln.toml) | `line-5` | 4,894.2 m | 4 |
| [`lobito-line6.aln.toml`](lobito-line6.aln.toml) | `line-6` | 6,905.5 m | 5 |
| [`lobito-line7.aln.toml`](lobito-line7.aln.toml) | `line-7` | 6,665.8 m | 5 |
| [`lobito-line8.aln.toml`](lobito-line8.aln.toml) | `line-8` | 6,466.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
