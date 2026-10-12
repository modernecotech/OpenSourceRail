# Mosul Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mosul-line1.aln.toml`](mosul-line1.aln.toml) | `line-1` | 35,639.9 m | 13 |
| [`mosul-line2.aln.toml`](mosul-line2.aln.toml) | `line-2` | 28,711.5 m | 10 |
| [`mosul-line3.aln.toml`](mosul-line3.aln.toml) | `line-3` | 30,402.7 m | 13 |
| [`mosul-line4.aln.toml`](mosul-line4.aln.toml) | `line-4` | 25,604.2 m | 10 |
| [`mosul-line5.aln.toml`](mosul-line5.aln.toml) | `line-5` | 19,977.5 m | 8 |
| [`mosul-line6.aln.toml`](mosul-line6.aln.toml) | `line-6` | 69,447.5 m | 21 |
| [`mosul-line7.aln.toml`](mosul-line7.aln.toml) | `line-7` | 4,843.6 m | 2 |
| [`mosul-line8.aln.toml`](mosul-line8.aln.toml) | `line-8` | 7,474.1 m | 5 |
| [`mosul-line9.aln.toml`](mosul-line9.aln.toml) | `line-9` | 8,298.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
