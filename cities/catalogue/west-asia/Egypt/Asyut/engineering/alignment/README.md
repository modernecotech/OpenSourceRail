# Asyut Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`asyut-line1.aln.toml`](asyut-line1.aln.toml) | `line-1` | 7,048.9 m | 5 |
| [`asyut-line10.aln.toml`](asyut-line10.aln.toml) | `line-10` | 3,919.1 m | 3 |
| [`asyut-line2.aln.toml`](asyut-line2.aln.toml) | `line-2` | 17,867.8 m | 12 |
| [`asyut-line3.aln.toml`](asyut-line3.aln.toml) | `line-3` | 21,053.0 m | 14 |
| [`asyut-line4.aln.toml`](asyut-line4.aln.toml) | `line-4` | 5,190.9 m | 4 |
| [`asyut-line5.aln.toml`](asyut-line5.aln.toml) | `line-5` | 10,297.1 m | 7 |
| [`asyut-line6.aln.toml`](asyut-line6.aln.toml) | `line-6` | 3,079.7 m | 2 |
| [`asyut-line7.aln.toml`](asyut-line7.aln.toml) | `line-7` | 4,003.1 m | 3 |
| [`asyut-line8.aln.toml`](asyut-line8.aln.toml) | `line-8` | 5,975.8 m | 4 |
| [`asyut-line9.aln.toml`](asyut-line9.aln.toml) | `line-9` | 11,488.8 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
