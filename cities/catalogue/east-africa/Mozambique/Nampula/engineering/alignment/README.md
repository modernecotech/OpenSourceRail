# Nampula Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nampula-line1.aln.toml`](nampula-line1.aln.toml) | `line-1` | 16,925.0 m | 5 |
| [`nampula-line2.aln.toml`](nampula-line2.aln.toml) | `line-2` | 18,943.2 m | 7 |
| [`nampula-line3.aln.toml`](nampula-line3.aln.toml) | `line-3` | 10,621.6 m | 5 |
| [`nampula-line4.aln.toml`](nampula-line4.aln.toml) | `line-4` | 6,506.4 m | 3 |
| [`nampula-line5.aln.toml`](nampula-line5.aln.toml) | `line-5` | 4,781.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
