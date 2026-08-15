# Jinja Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jinja-line1.aln.toml`](jinja-line1.aln.toml) | `line-1` | 15,752.7 m | 11 |
| [`jinja-line2.aln.toml`](jinja-line2.aln.toml) | `line-2` | 12,303.4 m | 9 |
| [`jinja-line3.aln.toml`](jinja-line3.aln.toml) | `line-3` | 14,008.4 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
