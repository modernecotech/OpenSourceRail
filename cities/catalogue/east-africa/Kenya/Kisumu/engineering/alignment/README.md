# Kisumu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kisumu-line1.aln.toml`](kisumu-line1.aln.toml) | `line-1` | 12,767.7 m | 7 |
| [`kisumu-line10.aln.toml`](kisumu-line10.aln.toml) | `line-10` | 8,010.7 m | 5 |
| [`kisumu-line11.aln.toml`](kisumu-line11.aln.toml) | `line-11` | 4,917.3 m | 4 |
| [`kisumu-line12.aln.toml`](kisumu-line12.aln.toml) | `line-12` | 2,238.8 m | 2 |
| [`kisumu-line2.aln.toml`](kisumu-line2.aln.toml) | `line-2` | 23,033.7 m | 14 |
| [`kisumu-line3.aln.toml`](kisumu-line3.aln.toml) | `line-3` | 7,929.1 m | 6 |
| [`kisumu-line4.aln.toml`](kisumu-line4.aln.toml) | `line-4` | 3,608.2 m | 4 |
| [`kisumu-line5.aln.toml`](kisumu-line5.aln.toml) | `line-5` | 7,519.6 m | 6 |
| [`kisumu-line6.aln.toml`](kisumu-line6.aln.toml) | `line-6` | 4,605.8 m | 5 |
| [`kisumu-line7.aln.toml`](kisumu-line7.aln.toml) | `line-7` | 2,163.7 m | 2 |
| [`kisumu-line8.aln.toml`](kisumu-line8.aln.toml) | `line-8` | 5,641.3 m | 4 |
| [`kisumu-line9.aln.toml`](kisumu-line9.aln.toml) | `line-9` | 3,559.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
