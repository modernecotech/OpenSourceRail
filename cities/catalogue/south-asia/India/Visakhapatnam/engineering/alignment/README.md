# Visakhapatnam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`visakhapatnam-line1.aln.toml`](visakhapatnam-line1.aln.toml) | `line-1` | 45,521.4 m | 13 |
| [`visakhapatnam-line2.aln.toml`](visakhapatnam-line2.aln.toml) | `line-2` | 49,735.4 m | 13 |
| [`visakhapatnam-line3.aln.toml`](visakhapatnam-line3.aln.toml) | `line-3` | 33,349.7 m | 12 |
| [`visakhapatnam-line4.aln.toml`](visakhapatnam-line4.aln.toml) | `line-4` | 28,000.3 m | 14 |
| [`visakhapatnam-line5.aln.toml`](visakhapatnam-line5.aln.toml) | `line-5` | 22,943.7 m | 12 |
| [`visakhapatnam-line6.aln.toml`](visakhapatnam-line6.aln.toml) | `line-6` | 71,493.3 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
