# Pemba-Mz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`pemba-mz-line1.aln.toml`](pemba-mz-line1.aln.toml) | `line-1` | 11,145.0 m | 7 |
| [`pemba-mz-line2.aln.toml`](pemba-mz-line2.aln.toml) | `line-2` | 6,927.2 m | 7 |
| [`pemba-mz-line3.aln.toml`](pemba-mz-line3.aln.toml) | `line-3` | 7,644.1 m | 5 |
| [`pemba-mz-line4.aln.toml`](pemba-mz-line4.aln.toml) | `line-4` | 4,265.6 m | 4 |
| [`pemba-mz-line5.aln.toml`](pemba-mz-line5.aln.toml) | `line-5` | 2,299.4 m | 2 |
| [`pemba-mz-line6.aln.toml`](pemba-mz-line6.aln.toml) | `line-6` | 2,323.1 m | 2 |
| [`pemba-mz-line7.aln.toml`](pemba-mz-line7.aln.toml) | `line-7` | 7,832.4 m | 6 |
| [`pemba-mz-line8.aln.toml`](pemba-mz-line8.aln.toml) | `line-8` | 5,069.8 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
