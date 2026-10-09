# Mazar-E-Sharif Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mazar-e-sharif-line1.aln.toml`](mazar-e-sharif-line1.aln.toml) | `line-1` | 13,185.7 m | 7 |
| [`mazar-e-sharif-line2.aln.toml`](mazar-e-sharif-line2.aln.toml) | `line-2` | 24,197.1 m | 17 |
| [`mazar-e-sharif-line3.aln.toml`](mazar-e-sharif-line3.aln.toml) | `line-3` | 19,782.1 m | 15 |
| [`mazar-e-sharif-line4.aln.toml`](mazar-e-sharif-line4.aln.toml) | `line-4` | 3,268.8 m | 3 |
| [`mazar-e-sharif-line5.aln.toml`](mazar-e-sharif-line5.aln.toml) | `line-5` | 2,075.4 m | 2 |
| [`mazar-e-sharif-line6.aln.toml`](mazar-e-sharif-line6.aln.toml) | `line-6` | 6,332.7 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
