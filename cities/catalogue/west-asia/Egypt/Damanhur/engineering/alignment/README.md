# Damanhur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`damanhur-line1.aln.toml`](damanhur-line1.aln.toml) | `line-1` | 7,443.7 m | 7 |
| [`damanhur-line10.aln.toml`](damanhur-line10.aln.toml) | `line-10` | 2,438.2 m | 3 |
| [`damanhur-line11.aln.toml`](damanhur-line11.aln.toml) | `line-11` | 2,683.7 m | 2 |
| [`damanhur-line2.aln.toml`](damanhur-line2.aln.toml) | `line-2` | 16,175.8 m | 10 |
| [`damanhur-line3.aln.toml`](damanhur-line3.aln.toml) | `line-3` | 18,310.4 m | 11 |
| [`damanhur-line4.aln.toml`](damanhur-line4.aln.toml) | `line-4` | 2,894.2 m | 4 |
| [`damanhur-line5.aln.toml`](damanhur-line5.aln.toml) | `line-5` | 6,746.7 m | 4 |
| [`damanhur-line6.aln.toml`](damanhur-line6.aln.toml) | `line-6` | 5,732.1 m | 4 |
| [`damanhur-line7.aln.toml`](damanhur-line7.aln.toml) | `line-7` | 4,707.1 m | 3 |
| [`damanhur-line8.aln.toml`](damanhur-line8.aln.toml) | `line-8` | 9,611.3 m | 6 |
| [`damanhur-line9.aln.toml`](damanhur-line9.aln.toml) | `line-9` | 5,500.1 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
