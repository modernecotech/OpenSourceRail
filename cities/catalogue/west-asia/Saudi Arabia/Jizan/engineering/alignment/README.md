# Jizan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jizan-line1.aln.toml`](jizan-line1.aln.toml) | `line-1` | 20,381.8 m | 14 |
| [`jizan-line10.aln.toml`](jizan-line10.aln.toml) | `line-10` | 2,756.5 m | 2 |
| [`jizan-line11.aln.toml`](jizan-line11.aln.toml) | `line-11` | 4,820.7 m | 3 |
| [`jizan-line2.aln.toml`](jizan-line2.aln.toml) | `line-2` | 7,365.6 m | 7 |
| [`jizan-line3.aln.toml`](jizan-line3.aln.toml) | `line-3` | 17,538.1 m | 13 |
| [`jizan-line4.aln.toml`](jizan-line4.aln.toml) | `line-4` | 4,762.6 m | 3 |
| [`jizan-line5.aln.toml`](jizan-line5.aln.toml) | `line-5` | 6,775.8 m | 5 |
| [`jizan-line6.aln.toml`](jizan-line6.aln.toml) | `line-6` | 5,196.5 m | 4 |
| [`jizan-line7.aln.toml`](jizan-line7.aln.toml) | `line-7` | 2,560.2 m | 2 |
| [`jizan-line8.aln.toml`](jizan-line8.aln.toml) | `line-8` | 3,446.5 m | 3 |
| [`jizan-line9.aln.toml`](jizan-line9.aln.toml) | `line-9` | 3,563.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
