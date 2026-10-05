# Idlib Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`idlib-line1.aln.toml`](idlib-line1.aln.toml) | `line-1` | 11,748.5 m | 5 |
| [`idlib-line2.aln.toml`](idlib-line2.aln.toml) | `line-2` | 7,953.6 m | 4 |
| [`idlib-line3.aln.toml`](idlib-line3.aln.toml) | `line-3` | 8,582.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
