# Tetouan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tetouan-line1.aln.toml`](tetouan-line1.aln.toml) | `line-1` | 18,551.5 m | 7 |
| [`tetouan-line2.aln.toml`](tetouan-line2.aln.toml) | `line-2` | 23,236.2 m | 8 |
| [`tetouan-line3.aln.toml`](tetouan-line3.aln.toml) | `line-3` | 12,266.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
