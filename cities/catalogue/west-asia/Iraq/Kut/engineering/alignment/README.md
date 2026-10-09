# Kut Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kut-line1.aln.toml`](kut-line1.aln.toml) | `line-1` | 25,562.9 m | 15 |
| [`kut-line2.aln.toml`](kut-line2.aln.toml) | `line-2` | 6,992.5 m | 6 |
| [`kut-line3.aln.toml`](kut-line3.aln.toml) | `line-3` | 13,673.9 m | 7 |
| [`kut-line4.aln.toml`](kut-line4.aln.toml) | `line-4` | 6,052.7 m | 4 |
| [`kut-line5.aln.toml`](kut-line5.aln.toml) | `line-5` | 3,991.6 m | 4 |
| [`kut-line6.aln.toml`](kut-line6.aln.toml) | `line-6` | 5,535.5 m | 4 |
| [`kut-line7.aln.toml`](kut-line7.aln.toml) | `line-7` | 8,122.9 m | 5 |
| [`kut-line8.aln.toml`](kut-line8.aln.toml) | `line-8` | 5,715.5 m | 4 |
| [`kut-line9.aln.toml`](kut-line9.aln.toml) | `line-9` | 3,378.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
