# Najaf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najaf-line1.aln.toml`](najaf-line1.aln.toml) | `line-1` | 19,268.3 m | 9 |
| [`najaf-line2.aln.toml`](najaf-line2.aln.toml) | `line-2` | 37,190.7 m | 18 |
| [`najaf-line3.aln.toml`](najaf-line3.aln.toml) | `line-3` | 17,563.9 m | 10 |
| [`najaf-line4.aln.toml`](najaf-line4.aln.toml) | `line-4` | 28,384.2 m | 9 |
| [`najaf-line5.aln.toml`](najaf-line5.aln.toml) | `line-5` | 27,344.6 m | 9 |
| [`najaf-line6.aln.toml`](najaf-line6.aln.toml) | `line-6` | 32,230.5 m | 18 |
| [`najaf-line7.aln.toml`](najaf-line7.aln.toml) | `line-7` | 5,093.0 m | 3 |
| [`najaf-line8.aln.toml`](najaf-line8.aln.toml) | `line-8` | 14,061.6 m | 4 |
| [`najaf-line9.aln.toml`](najaf-line9.aln.toml) | `line-9` | 12,212.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
