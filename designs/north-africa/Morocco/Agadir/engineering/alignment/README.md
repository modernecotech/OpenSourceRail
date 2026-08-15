# Agadir Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`agadir-line1.aln.toml`](agadir-line1.aln.toml) | `line-1` | 28,576.3 m | 12 |
| [`agadir-line2.aln.toml`](agadir-line2.aln.toml) | `line-2` | 25,864.8 m | 9 |
| [`agadir-line3.aln.toml`](agadir-line3.aln.toml) | `line-3` | 27,049.5 m | 9 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
