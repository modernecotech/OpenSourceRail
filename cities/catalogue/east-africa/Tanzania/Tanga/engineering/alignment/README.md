# Tanga Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tanga-line1.aln.toml`](tanga-line1.aln.toml) | `line-1` | 17,697.2 m | 12 |
| [`tanga-line2.aln.toml`](tanga-line2.aln.toml) | `line-2` | 13,143.4 m | 10 |
| [`tanga-line3.aln.toml`](tanga-line3.aln.toml) | `line-3` | 10,010.7 m | 8 |
| [`tanga-line4.aln.toml`](tanga-line4.aln.toml) | `line-4` | 2,367.9 m | 2 |
| [`tanga-line5.aln.toml`](tanga-line5.aln.toml) | `line-5` | 5,454.1 m | 4 |
| [`tanga-line6.aln.toml`](tanga-line6.aln.toml) | `line-6` | 2,880.5 m | 2 |
| [`tanga-line7.aln.toml`](tanga-line7.aln.toml) | `line-7` | 5,951.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
