# Arua Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`arua-line1.aln.toml`](arua-line1.aln.toml) | `line-1` | 8,774.0 m | 6 |
| [`arua-line10.aln.toml`](arua-line10.aln.toml) | `line-10` | 5,890.1 m | 4 |
| [`arua-line11.aln.toml`](arua-line11.aln.toml) | `line-11` | 4,159.9 m | 3 |
| [`arua-line12.aln.toml`](arua-line12.aln.toml) | `line-12` | 2,884.5 m | 2 |
| [`arua-line2.aln.toml`](arua-line2.aln.toml) | `line-2` | 13,548.7 m | 9 |
| [`arua-line3.aln.toml`](arua-line3.aln.toml) | `line-3` | 10,514.7 m | 10 |
| [`arua-line4.aln.toml`](arua-line4.aln.toml) | `line-4` | 2,661.7 m | 2 |
| [`arua-line5.aln.toml`](arua-line5.aln.toml) | `line-5` | 2,454.2 m | 2 |
| [`arua-line6.aln.toml`](arua-line6.aln.toml) | `line-6` | 2,459.1 m | 2 |
| [`arua-line7.aln.toml`](arua-line7.aln.toml) | `line-7` | 3,666.3 m | 3 |
| [`arua-line8.aln.toml`](arua-line8.aln.toml) | `line-8` | 3,945.3 m | 3 |
| [`arua-line9.aln.toml`](arua-line9.aln.toml) | `line-9` | 3,540.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
