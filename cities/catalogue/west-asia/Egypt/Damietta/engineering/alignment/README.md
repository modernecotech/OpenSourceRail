# Damietta Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`damietta-line1.aln.toml`](damietta-line1.aln.toml) | `line-1` | 23,096.8 m | 15 |
| [`damietta-line10.aln.toml`](damietta-line10.aln.toml) | `line-10` | 13,179.3 m | 10 |
| [`damietta-line11.aln.toml`](damietta-line11.aln.toml) | `line-11` | 15,077.2 m | 10 |
| [`damietta-line2.aln.toml`](damietta-line2.aln.toml) | `line-2` | 17,755.0 m | 11 |
| [`damietta-line3.aln.toml`](damietta-line3.aln.toml) | `line-3` | 27,252.3 m | 16 |
| [`damietta-line4.aln.toml`](damietta-line4.aln.toml) | `line-4` | 2,837.1 m | 2 |
| [`damietta-line5.aln.toml`](damietta-line5.aln.toml) | `line-5` | 3,044.5 m | 2 |
| [`damietta-line6.aln.toml`](damietta-line6.aln.toml) | `line-6` | 6,422.6 m | 6 |
| [`damietta-line7.aln.toml`](damietta-line7.aln.toml) | `line-7` | 5,803.7 m | 4 |
| [`damietta-line8.aln.toml`](damietta-line8.aln.toml) | `line-8` | 3,355.0 m | 4 |
| [`damietta-line9.aln.toml`](damietta-line9.aln.toml) | `line-9` | 4,063.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
