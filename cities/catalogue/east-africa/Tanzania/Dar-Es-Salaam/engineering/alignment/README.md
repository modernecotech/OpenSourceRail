# Dar-Es-Salaam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dar-es-salaam-line1.aln.toml`](dar-es-salaam-line1.aln.toml) | `line-1` | 43,949.8 m | 13 |
| [`dar-es-salaam-line2.aln.toml`](dar-es-salaam-line2.aln.toml) | `line-2` | 49,653.0 m | 15 |
| [`dar-es-salaam-line3.aln.toml`](dar-es-salaam-line3.aln.toml) | `line-3` | 45,204.3 m | 13 |
| [`dar-es-salaam-line4.aln.toml`](dar-es-salaam-line4.aln.toml) | `line-4` | 39,607.5 m | 11 |
| [`dar-es-salaam-line5.aln.toml`](dar-es-salaam-line5.aln.toml) | `line-5` | 27,927.9 m | 10 |
| [`dar-es-salaam-line6.aln.toml`](dar-es-salaam-line6.aln.toml) | `line-6` | 31,462.2 m | 10 |
| [`dar-es-salaam-line7.aln.toml`](dar-es-salaam-line7.aln.toml) | `line-7` | 27,987.3 m | 9 |
| [`dar-es-salaam-line8.aln.toml`](dar-es-salaam-line8.aln.toml) | `line-8` | 32,886.8 m | 10 |
| [`dar-es-salaam-line9.aln.toml`](dar-es-salaam-line9.aln.toml) | `line-9` | 80,613.3 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
