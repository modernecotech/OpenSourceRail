# Hillah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hillah-line1.aln.toml`](hillah-line1.aln.toml) | `line-1` | 17,504.8 m | 7 |
| [`hillah-line2.aln.toml`](hillah-line2.aln.toml) | `line-2` | 17,059.9 m | 7 |
| [`hillah-line3.aln.toml`](hillah-line3.aln.toml) | `line-3` | 17,722.7 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
