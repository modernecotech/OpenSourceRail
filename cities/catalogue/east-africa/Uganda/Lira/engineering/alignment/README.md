# Lira Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lira-line1.aln.toml`](lira-line1.aln.toml) | `line-1` | 11,826.6 m | 7 |
| [`lira-line10.aln.toml`](lira-line10.aln.toml) | `line-10` | 2,083.7 m | 2 |
| [`lira-line11.aln.toml`](lira-line11.aln.toml) | `line-11` | 2,070.8 m | 2 |
| [`lira-line2.aln.toml`](lira-line2.aln.toml) | `line-2` | 13,314.9 m | 8 |
| [`lira-line3.aln.toml`](lira-line3.aln.toml) | `line-3` | 13,669.3 m | 9 |
| [`lira-line4.aln.toml`](lira-line4.aln.toml) | `line-4` | 3,223.7 m | 3 |
| [`lira-line5.aln.toml`](lira-line5.aln.toml) | `line-5` | 3,604.2 m | 3 |
| [`lira-line6.aln.toml`](lira-line6.aln.toml) | `line-6` | 8,799.6 m | 5 |
| [`lira-line7.aln.toml`](lira-line7.aln.toml) | `line-7` | 8,557.0 m | 6 |
| [`lira-line8.aln.toml`](lira-line8.aln.toml) | `line-8` | 6,565.9 m | 4 |
| [`lira-line9.aln.toml`](lira-line9.aln.toml) | `line-9` | 3,575.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
