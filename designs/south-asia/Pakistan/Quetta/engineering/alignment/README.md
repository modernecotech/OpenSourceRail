# Quetta Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`quetta-line1.aln.toml`](quetta-line1.aln.toml) | `line-1` | 25,431.2 m | 15 |
| [`quetta-line2.aln.toml`](quetta-line2.aln.toml) | `line-2` | 26,740.0 m | 17 |
| [`quetta-line3.aln.toml`](quetta-line3.aln.toml) | `line-3` | 15,386.1 m | 10 |
| [`quetta-line4.aln.toml`](quetta-line4.aln.toml) | `line-4` | 53,116.6 m | 38 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
