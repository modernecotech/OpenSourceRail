# Dar-Es-Salaam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dar-es-salaam-line1.aln.toml`](dar-es-salaam-line1.aln.toml) | `line-1` | 54,952.2 m | 29 |
| [`dar-es-salaam-line2.aln.toml`](dar-es-salaam-line2.aln.toml) | `line-2` | 58,982.9 m | 31 |
| [`dar-es-salaam-line3.aln.toml`](dar-es-salaam-line3.aln.toml) | `line-3` | 49,039.8 m | 23 |
| [`dar-es-salaam-line4.aln.toml`](dar-es-salaam-line4.aln.toml) | `line-4` | 48,041.9 m | 25 |
| [`dar-es-salaam-line5.aln.toml`](dar-es-salaam-line5.aln.toml) | `line-5` | 35,918.4 m | 20 |
| [`dar-es-salaam-line6.aln.toml`](dar-es-salaam-line6.aln.toml) | `line-6` | 39,533.7 m | 18 |
| [`dar-es-salaam-line7.aln.toml`](dar-es-salaam-line7.aln.toml) | `line-7` | 34,235.5 m | 17 |
| [`dar-es-salaam-line8.aln.toml`](dar-es-salaam-line8.aln.toml) | `line-8` | 37,385.9 m | 19 |
| [`dar-es-salaam-line9.aln.toml`](dar-es-salaam-line9.aln.toml) | `line-9` | 85,641.4 m | 52 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
