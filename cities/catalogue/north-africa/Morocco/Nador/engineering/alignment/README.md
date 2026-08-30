# Nador Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nador-line1.aln.toml`](nador-line1.aln.toml) | `line-1` | 9,996.0 m | 5 |
| [`nador-line2.aln.toml`](nador-line2.aln.toml) | `line-2` | 15,367.9 m | 7 |
| [`nador-line3.aln.toml`](nador-line3.aln.toml) | `line-3` | 8,982.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
