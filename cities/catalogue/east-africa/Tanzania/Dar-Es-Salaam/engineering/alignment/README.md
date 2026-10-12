# Dar-Es-Salaam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dar-es-salaam-line1.aln.toml`](dar-es-salaam-line1.aln.toml) | `line-1` | 57,488.2 m | 32 |
| [`dar-es-salaam-line10.aln.toml`](dar-es-salaam-line10.aln.toml) | `line-10` | 6,186.2 m | 3 |
| [`dar-es-salaam-line11.aln.toml`](dar-es-salaam-line11.aln.toml) | `line-11` | 8,219.8 m | 3 |
| [`dar-es-salaam-line12.aln.toml`](dar-es-salaam-line12.aln.toml) | `line-12` | 8,768.3 m | 3 |
| [`dar-es-salaam-line13.aln.toml`](dar-es-salaam-line13.aln.toml) | `line-13` | 13,106.0 m | 3 |
| [`dar-es-salaam-line14.aln.toml`](dar-es-salaam-line14.aln.toml) | `line-14` | 21,905.7 m | 7 |
| [`dar-es-salaam-line2.aln.toml`](dar-es-salaam-line2.aln.toml) | `line-2` | 71,959.9 m | 34 |
| [`dar-es-salaam-line3.aln.toml`](dar-es-salaam-line3.aln.toml) | `line-3` | 46,645.2 m | 18 |
| [`dar-es-salaam-line4.aln.toml`](dar-es-salaam-line4.aln.toml) | `line-4` | 51,976.2 m | 44 |
| [`dar-es-salaam-line5.aln.toml`](dar-es-salaam-line5.aln.toml) | `line-5` | 29,132.1 m | 15 |
| [`dar-es-salaam-line6.aln.toml`](dar-es-salaam-line6.aln.toml) | `line-6` | 43,074.1 m | 18 |
| [`dar-es-salaam-line7.aln.toml`](dar-es-salaam-line7.aln.toml) | `line-7` | 27,595.3 m | 12 |
| [`dar-es-salaam-line8.aln.toml`](dar-es-salaam-line8.aln.toml) | `line-8` | 37,715.5 m | 36 |
| [`dar-es-salaam-line9.aln.toml`](dar-es-salaam-line9.aln.toml) | `line-9` | 187,217.9 m | 81 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
