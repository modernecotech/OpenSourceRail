# Visakhapatnam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`visakhapatnam-line1.aln.toml`](visakhapatnam-line1.aln.toml) | `line-1` | 41,660.5 m | 14 |
| [`visakhapatnam-line2.aln.toml`](visakhapatnam-line2.aln.toml) | `line-2` | 45,923.4 m | 14 |
| [`visakhapatnam-line3.aln.toml`](visakhapatnam-line3.aln.toml) | `line-3` | 32,490.4 m | 10 |
| [`visakhapatnam-line4.aln.toml`](visakhapatnam-line4.aln.toml) | `line-4` | 25,671.7 m | 8 |
| [`visakhapatnam-line5.aln.toml`](visakhapatnam-line5.aln.toml) | `line-5` | 21,478.1 m | 8 |
| [`visakhapatnam-line6.aln.toml`](visakhapatnam-line6.aln.toml) | `line-6` | 69,621.6 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
