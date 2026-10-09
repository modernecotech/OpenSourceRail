# Hoima Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hoima-line1.aln.toml`](hoima-line1.aln.toml) | `line-1` | 10,323.7 m | 7 |
| [`hoima-line2.aln.toml`](hoima-line2.aln.toml) | `line-2` | 8,106.3 m | 5 |
| [`hoima-line3.aln.toml`](hoima-line3.aln.toml) | `line-3` | 5,385.1 m | 5 |
| [`hoima-line4.aln.toml`](hoima-line4.aln.toml) | `line-4` | 6,964.2 m | 5 |
| [`hoima-line5.aln.toml`](hoima-line5.aln.toml) | `line-5` | 7,916.3 m | 6 |
| [`hoima-line6.aln.toml`](hoima-line6.aln.toml) | `line-6` | 2,020.8 m | 2 |
| [`hoima-line7.aln.toml`](hoima-line7.aln.toml) | `line-7` | 4,028.4 m | 3 |
| [`hoima-line8.aln.toml`](hoima-line8.aln.toml) | `line-8` | 2,417.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
