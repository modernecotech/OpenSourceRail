# Duhok Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`duhok-line1.aln.toml`](duhok-line1.aln.toml) | `line-1` | 17,357.2 m | 10 |
| [`duhok-line2.aln.toml`](duhok-line2.aln.toml) | `line-2` | 16,597.2 m | 11 |
| [`duhok-line3.aln.toml`](duhok-line3.aln.toml) | `line-3` | 19,163.9 m | 11 |
| [`duhok-line4.aln.toml`](duhok-line4.aln.toml) | `line-4` | 2,881.4 m | 3 |
| [`duhok-line5.aln.toml`](duhok-line5.aln.toml) | `line-5` | 6,325.9 m | 5 |
| [`duhok-line6.aln.toml`](duhok-line6.aln.toml) | `line-6` | 2,628.8 m | 2 |
| [`duhok-line7.aln.toml`](duhok-line7.aln.toml) | `line-7` | 2,024.5 m | 3 |
| [`duhok-line8.aln.toml`](duhok-line8.aln.toml) | `line-8` | 7,762.5 m | 6 |
| [`duhok-line9.aln.toml`](duhok-line9.aln.toml) | `line-9` | 9,019.7 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
