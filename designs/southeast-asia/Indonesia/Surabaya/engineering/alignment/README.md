# Surabaya Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`surabaya-line1.aln.toml`](surabaya-line1.aln.toml) | `line-1` | 35,122.9 m | 21 |
| [`surabaya-line2.aln.toml`](surabaya-line2.aln.toml) | `line-2` | 33,397.8 m | 18 |
| [`surabaya-line3.aln.toml`](surabaya-line3.aln.toml) | `line-3` | 37,394.2 m | 20 |
| [`surabaya-line4.aln.toml`](surabaya-line4.aln.toml) | `line-4` | 26,291.8 m | 14 |
| [`surabaya-line5.aln.toml`](surabaya-line5.aln.toml) | `line-5` | 33,830.9 m | 19 |
| [`surabaya-line6.aln.toml`](surabaya-line6.aln.toml) | `line-6` | 24,036.7 m | 16 |
| [`surabaya-line7.aln.toml`](surabaya-line7.aln.toml) | `line-7` | 23,089.0 m | 14 |
| [`surabaya-line8.aln.toml`](surabaya-line8.aln.toml) | `line-8` | 20,965.8 m | 14 |
| [`surabaya-line9.aln.toml`](surabaya-line9.aln.toml) | `line-9` | 59,686.3 m | 42 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
