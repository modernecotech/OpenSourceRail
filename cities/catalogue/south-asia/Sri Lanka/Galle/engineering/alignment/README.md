# Galle Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`galle-line1.aln.toml`](galle-line1.aln.toml) | `line-1` | 22,406.7 m | 9 |
| [`galle-line2.aln.toml`](galle-line2.aln.toml) | `line-2` | 22,687.6 m | 6 |
| [`galle-line3.aln.toml`](galle-line3.aln.toml) | `line-3` | 18,589.8 m | 8 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
