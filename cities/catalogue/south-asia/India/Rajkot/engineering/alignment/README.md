# Rajkot Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rajkot-line1.aln.toml`](rajkot-line1.aln.toml) | `line-1` | 21,095.4 m | 8 |
| [`rajkot-line2.aln.toml`](rajkot-line2.aln.toml) | `line-2` | 12,106.9 m | 6 |
| [`rajkot-line3.aln.toml`](rajkot-line3.aln.toml) | `line-3` | 12,749.1 m | 6 |
| [`rajkot-line4.aln.toml`](rajkot-line4.aln.toml) | `line-4` | 21,778.9 m | 8 |
| [`rajkot-line5.aln.toml`](rajkot-line5.aln.toml) | `line-5` | 50,567.6 m | 15 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
