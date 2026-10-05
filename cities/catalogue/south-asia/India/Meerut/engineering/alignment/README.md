# Meerut Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`meerut-line1.aln.toml`](meerut-line1.aln.toml) | `line-1` | 21,717.0 m | 10 |
| [`meerut-line2.aln.toml`](meerut-line2.aln.toml) | `line-2` | 26,946.7 m | 11 |
| [`meerut-line3.aln.toml`](meerut-line3.aln.toml) | `line-3` | 25,128.1 m | 8 |
| [`meerut-line4.aln.toml`](meerut-line4.aln.toml) | `line-4` | 53,407.7 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
