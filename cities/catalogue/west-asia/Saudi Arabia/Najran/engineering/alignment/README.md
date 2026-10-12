# Najran Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najran-line1.aln.toml`](najran-line1.aln.toml) | `line-1` | 19,018.4 m | 5 |
| [`najran-line2.aln.toml`](najran-line2.aln.toml) | `line-2` | 21,830.1 m | 6 |
| [`najran-line3.aln.toml`](najran-line3.aln.toml) | `line-3` | 15,275.6 m | 6 |
| [`najran-line4.aln.toml`](najran-line4.aln.toml) | `line-4` | 7,362.2 m | 3 |
| [`najran-line5.aln.toml`](najran-line5.aln.toml) | `line-5` | 5,726.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
