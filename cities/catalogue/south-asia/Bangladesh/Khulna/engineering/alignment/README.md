# Khulna Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khulna-line1.aln.toml`](khulna-line1.aln.toml) | `line-1` | 28,717.9 m | 19 |
| [`khulna-line10.aln.toml`](khulna-line10.aln.toml) | `line-10` | 5,842.7 m | 5 |
| [`khulna-line11.aln.toml`](khulna-line11.aln.toml) | `line-11` | 12,721.8 m | 10 |
| [`khulna-line12.aln.toml`](khulna-line12.aln.toml) | `line-12` | 5,588.2 m | 4 |
| [`khulna-line13.aln.toml`](khulna-line13.aln.toml) | `line-13` | 7,418.1 m | 5 |
| [`khulna-line14.aln.toml`](khulna-line14.aln.toml) | `line-14` | 5,338.1 m | 4 |
| [`khulna-line15.aln.toml`](khulna-line15.aln.toml) | `line-15` | 3,932.2 m | 5 |
| [`khulna-line16.aln.toml`](khulna-line16.aln.toml) | `line-16` | 10,055.4 m | 8 |
| [`khulna-line2.aln.toml`](khulna-line2.aln.toml) | `line-2` | 32,531.5 m | 27 |
| [`khulna-line3.aln.toml`](khulna-line3.aln.toml) | `line-3` | 31,572.2 m | 21 |
| [`khulna-line4.aln.toml`](khulna-line4.aln.toml) | `line-4` | 16,610.2 m | 11 |
| [`khulna-line5.aln.toml`](khulna-line5.aln.toml) | `line-5` | 24,810.6 m | 20 |
| [`khulna-line6.aln.toml`](khulna-line6.aln.toml) | `line-6` | 59,142.6 m | 36 |
| [`khulna-line7.aln.toml`](khulna-line7.aln.toml) | `line-7` | 4,027.6 m | 4 |
| [`khulna-line8.aln.toml`](khulna-line8.aln.toml) | `line-8` | 5,336.7 m | 5 |
| [`khulna-line9.aln.toml`](khulna-line9.aln.toml) | `line-9` | 5,380.1 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
