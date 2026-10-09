# Beni-Mellal Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`beni-mellal-line1.aln.toml`](beni-mellal-line1.aln.toml) | `line-1` | 8,527.7 m | 6 |
| [`beni-mellal-line2.aln.toml`](beni-mellal-line2.aln.toml) | `line-2` | 9,671.4 m | 6 |
| [`beni-mellal-line3.aln.toml`](beni-mellal-line3.aln.toml) | `line-3` | 8,825.0 m | 5 |
| [`beni-mellal-line4.aln.toml`](beni-mellal-line4.aln.toml) | `line-4` | 2,568.5 m | 2 |
| [`beni-mellal-line5.aln.toml`](beni-mellal-line5.aln.toml) | `line-5` | 4,094.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
