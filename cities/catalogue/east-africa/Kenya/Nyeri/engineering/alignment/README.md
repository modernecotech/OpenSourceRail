# Nyeri Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nyeri-line1.aln.toml`](nyeri-line1.aln.toml) | `line-1` | 8,655.5 m | 8 |
| [`nyeri-line10.aln.toml`](nyeri-line10.aln.toml) | `line-10` | 6,897.5 m | 4 |
| [`nyeri-line2.aln.toml`](nyeri-line2.aln.toml) | `line-2` | 14,355.3 m | 10 |
| [`nyeri-line3.aln.toml`](nyeri-line3.aln.toml) | `line-3` | 10,004.0 m | 6 |
| [`nyeri-line4.aln.toml`](nyeri-line4.aln.toml) | `line-4` | 2,970.2 m | 4 |
| [`nyeri-line5.aln.toml`](nyeri-line5.aln.toml) | `line-5` | 5,846.7 m | 6 |
| [`nyeri-line6.aln.toml`](nyeri-line6.aln.toml) | `line-6` | 4,950.8 m | 4 |
| [`nyeri-line7.aln.toml`](nyeri-line7.aln.toml) | `line-7` | 5,164.2 m | 4 |
| [`nyeri-line8.aln.toml`](nyeri-line8.aln.toml) | `line-8` | 4,699.1 m | 4 |
| [`nyeri-line9.aln.toml`](nyeri-line9.aln.toml) | `line-9` | 2,000.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
