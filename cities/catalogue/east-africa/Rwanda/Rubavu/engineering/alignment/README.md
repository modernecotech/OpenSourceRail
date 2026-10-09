# Rubavu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rubavu-line1.aln.toml`](rubavu-line1.aln.toml) | `line-1` | 11,038.0 m | 6 |
| [`rubavu-line10.aln.toml`](rubavu-line10.aln.toml) | `line-10` | 2,236.8 m | 2 |
| [`rubavu-line2.aln.toml`](rubavu-line2.aln.toml) | `line-2` | 12,440.8 m | 10 |
| [`rubavu-line3.aln.toml`](rubavu-line3.aln.toml) | `line-3` | 13,309.1 m | 9 |
| [`rubavu-line4.aln.toml`](rubavu-line4.aln.toml) | `line-4` | 2,682.5 m | 2 |
| [`rubavu-line5.aln.toml`](rubavu-line5.aln.toml) | `line-5` | 7,412.6 m | 5 |
| [`rubavu-line6.aln.toml`](rubavu-line6.aln.toml) | `line-6` | 7,088.3 m | 5 |
| [`rubavu-line7.aln.toml`](rubavu-line7.aln.toml) | `line-7` | 6,415.5 m | 4 |
| [`rubavu-line8.aln.toml`](rubavu-line8.aln.toml) | `line-8` | 6,814.0 m | 4 |
| [`rubavu-line9.aln.toml`](rubavu-line9.aln.toml) | `line-9` | 3,829.6 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
