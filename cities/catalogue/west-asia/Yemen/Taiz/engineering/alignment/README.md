# Taiz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`taiz-line1.aln.toml`](taiz-line1.aln.toml) | `line-1` | 16,491.3 m | 12 |
| [`taiz-line10.aln.toml`](taiz-line10.aln.toml) | `line-10` | 5,163.6 m | 4 |
| [`taiz-line11.aln.toml`](taiz-line11.aln.toml) | `line-11` | 4,531.0 m | 3 |
| [`taiz-line2.aln.toml`](taiz-line2.aln.toml) | `line-2` | 6,133.0 m | 4 |
| [`taiz-line3.aln.toml`](taiz-line3.aln.toml) | `line-3` | 15,253.0 m | 13 |
| [`taiz-line4.aln.toml`](taiz-line4.aln.toml) | `line-4` | 2,684.5 m | 2 |
| [`taiz-line5.aln.toml`](taiz-line5.aln.toml) | `line-5` | 2,485.7 m | 2 |
| [`taiz-line6.aln.toml`](taiz-line6.aln.toml) | `line-6` | 3,058.2 m | 3 |
| [`taiz-line7.aln.toml`](taiz-line7.aln.toml) | `line-7` | 5,552.8 m | 4 |
| [`taiz-line8.aln.toml`](taiz-line8.aln.toml) | `line-8` | 4,380.0 m | 5 |
| [`taiz-line9.aln.toml`](taiz-line9.aln.toml) | `line-9` | 6,752.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
