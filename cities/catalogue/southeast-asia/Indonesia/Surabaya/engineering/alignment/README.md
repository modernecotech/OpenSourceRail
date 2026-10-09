# Surabaya Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`surabaya-line1.aln.toml`](surabaya-line1.aln.toml) | `line-1` | 46,048.6 m | 23 |
| [`surabaya-line2.aln.toml`](surabaya-line2.aln.toml) | `line-2` | 36,053.2 m | 19 |
| [`surabaya-line3.aln.toml`](surabaya-line3.aln.toml) | `line-3` | 31,352.1 m | 14 |
| [`surabaya-line4.aln.toml`](surabaya-line4.aln.toml) | `line-4` | 26,569.4 m | 14 |
| [`surabaya-line5.aln.toml`](surabaya-line5.aln.toml) | `line-5` | 35,162.1 m | 18 |
| [`surabaya-line6.aln.toml`](surabaya-line6.aln.toml) | `line-6` | 19,804.5 m | 11 |
| [`surabaya-line7.aln.toml`](surabaya-line7.aln.toml) | `line-7` | 19,732.3 m | 14 |
| [`surabaya-line8.aln.toml`](surabaya-line8.aln.toml) | `line-8` | 18,067.2 m | 9 |
| [`surabaya-line9.aln.toml`](surabaya-line9.aln.toml) | `line-9` | 58,271.5 m | 34 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
