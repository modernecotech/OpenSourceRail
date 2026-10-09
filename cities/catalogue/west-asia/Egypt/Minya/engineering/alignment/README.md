# Minya Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`minya-line1.aln.toml`](minya-line1.aln.toml) | `line-1` | 14,580.4 m | 8 |
| [`minya-line2.aln.toml`](minya-line2.aln.toml) | `line-2` | 14,377.8 m | 10 |
| [`minya-line3.aln.toml`](minya-line3.aln.toml) | `line-3` | 11,990.8 m | 8 |
| [`minya-line4.aln.toml`](minya-line4.aln.toml) | `line-4` | 4,737.1 m | 4 |
| [`minya-line5.aln.toml`](minya-line5.aln.toml) | `line-5` | 2,161.7 m | 2 |
| [`minya-line6.aln.toml`](minya-line6.aln.toml) | `line-6` | 5,713.3 m | 4 |
| [`minya-line7.aln.toml`](minya-line7.aln.toml) | `line-7` | 7,001.6 m | 4 |
| [`minya-line8.aln.toml`](minya-line8.aln.toml) | `line-8` | 8,162.6 m | 4 |
| [`minya-line9.aln.toml`](minya-line9.aln.toml) | `line-9` | 13,082.3 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
