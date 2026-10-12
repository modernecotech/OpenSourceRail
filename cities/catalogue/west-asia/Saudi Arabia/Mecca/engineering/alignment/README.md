# Mecca Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mecca-line1.aln.toml`](mecca-line1.aln.toml) | `line-1` | 32,859.6 m | 12 |
| [`mecca-line2.aln.toml`](mecca-line2.aln.toml) | `line-2` | 27,819.1 m | 7 |
| [`mecca-line3.aln.toml`](mecca-line3.aln.toml) | `line-3` | 32,648.0 m | 11 |
| [`mecca-line4.aln.toml`](mecca-line4.aln.toml) | `line-4` | 35,006.1 m | 10 |
| [`mecca-line5.aln.toml`](mecca-line5.aln.toml) | `line-5` | 26,099.6 m | 8 |
| [`mecca-line6.aln.toml`](mecca-line6.aln.toml) | `line-6` | 72,756.3 m | 16 |
| [`mecca-line7.aln.toml`](mecca-line7.aln.toml) | `line-7` | 6,481.6 m | 2 |
| [`mecca-line8.aln.toml`](mecca-line8.aln.toml) | `line-8` | 4,960.7 m | 3 |
| [`mecca-line9.aln.toml`](mecca-line9.aln.toml) | `line-9` | 11,500.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
