# Tanga Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tanga-line1.aln.toml`](tanga-line1.aln.toml) | `line-1` | 17,697.2 m | 6 |
| [`tanga-line2.aln.toml`](tanga-line2.aln.toml) | `line-2` | 15,029.9 m | 8 |
| [`tanga-line3.aln.toml`](tanga-line3.aln.toml) | `line-3` | 13,075.1 m | 7 |
| [`tanga-line4.aln.toml`](tanga-line4.aln.toml) | `line-4` | 4,194.5 m | 2 |
| [`tanga-line5.aln.toml`](tanga-line5.aln.toml) | `line-5` | 4,639.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
