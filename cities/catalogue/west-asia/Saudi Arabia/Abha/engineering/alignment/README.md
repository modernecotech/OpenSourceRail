# Abha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`abha-line1.aln.toml`](abha-line1.aln.toml) | `line-1` | 17,539.8 m | 11 |
| [`abha-line10.aln.toml`](abha-line10.aln.toml) | `line-10` | 8,307.2 m | 6 |
| [`abha-line2.aln.toml`](abha-line2.aln.toml) | `line-2` | 20,347.3 m | 11 |
| [`abha-line3.aln.toml`](abha-line3.aln.toml) | `line-3` | 13,411.3 m | 8 |
| [`abha-line4.aln.toml`](abha-line4.aln.toml) | `line-4` | 4,017.9 m | 3 |
| [`abha-line5.aln.toml`](abha-line5.aln.toml) | `line-5` | 10,048.4 m | 7 |
| [`abha-line6.aln.toml`](abha-line6.aln.toml) | `line-6` | 6,663.0 m | 4 |
| [`abha-line7.aln.toml`](abha-line7.aln.toml) | `line-7` | 7,725.8 m | 5 |
| [`abha-line8.aln.toml`](abha-line8.aln.toml) | `line-8` | 7,107.4 m | 5 |
| [`abha-line9.aln.toml`](abha-line9.aln.toml) | `line-9` | 6,463.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
