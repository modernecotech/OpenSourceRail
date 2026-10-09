# Bahawalpur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bahawalpur-line1.aln.toml`](bahawalpur-line1.aln.toml) | `line-1` | 14,492.1 m | 8 |
| [`bahawalpur-line10.aln.toml`](bahawalpur-line10.aln.toml) | `line-10` | 2,240.0 m | 2 |
| [`bahawalpur-line2.aln.toml`](bahawalpur-line2.aln.toml) | `line-2` | 12,957.9 m | 8 |
| [`bahawalpur-line3.aln.toml`](bahawalpur-line3.aln.toml) | `line-3` | 10,091.3 m | 8 |
| [`bahawalpur-line4.aln.toml`](bahawalpur-line4.aln.toml) | `line-4` | 5,143.3 m | 4 |
| [`bahawalpur-line5.aln.toml`](bahawalpur-line5.aln.toml) | `line-5` | 3,529.0 m | 3 |
| [`bahawalpur-line6.aln.toml`](bahawalpur-line6.aln.toml) | `line-6` | 4,623.0 m | 3 |
| [`bahawalpur-line7.aln.toml`](bahawalpur-line7.aln.toml) | `line-7` | 4,297.3 m | 3 |
| [`bahawalpur-line8.aln.toml`](bahawalpur-line8.aln.toml) | `line-8` | 13,351.5 m | 9 |
| [`bahawalpur-line9.aln.toml`](bahawalpur-line9.aln.toml) | `line-9` | 3,300.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
