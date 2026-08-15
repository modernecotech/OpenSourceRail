# Jalalabad-Af Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jalalabad-af-line1.aln.toml`](jalalabad-af-line1.aln.toml) | `line-1` | 11,847.7 m | 7 |
| [`jalalabad-af-line2.aln.toml`](jalalabad-af-line2.aln.toml) | `line-2` | 20,964.8 m | 11 |
| [`jalalabad-af-line3.aln.toml`](jalalabad-af-line3.aln.toml) | `line-3` | 14,179.1 m | 8 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
