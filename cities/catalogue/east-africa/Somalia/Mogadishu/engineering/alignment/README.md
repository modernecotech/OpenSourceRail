# Mogadishu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mogadishu-line1.aln.toml`](mogadishu-line1.aln.toml) | `line-1` | 33,442.5 m | 21 |
| [`mogadishu-line10.aln.toml`](mogadishu-line10.aln.toml) | `line-10` | 3,199.7 m | 3 |
| [`mogadishu-line11.aln.toml`](mogadishu-line11.aln.toml) | `line-11` | 7,438.7 m | 5 |
| [`mogadishu-line12.aln.toml`](mogadishu-line12.aln.toml) | `line-12` | 6,808.6 m | 7 |
| [`mogadishu-line2.aln.toml`](mogadishu-line2.aln.toml) | `line-2` | 22,039.7 m | 15 |
| [`mogadishu-line3.aln.toml`](mogadishu-line3.aln.toml) | `line-3` | 13,901.8 m | 8 |
| [`mogadishu-line4.aln.toml`](mogadishu-line4.aln.toml) | `line-4` | 45,088.8 m | 25 |
| [`mogadishu-line5.aln.toml`](mogadishu-line5.aln.toml) | `line-5` | 3,573.4 m | 5 |
| [`mogadishu-line6.aln.toml`](mogadishu-line6.aln.toml) | `line-6` | 4,899.1 m | 4 |
| [`mogadishu-line7.aln.toml`](mogadishu-line7.aln.toml) | `line-7` | 4,045.0 m | 3 |
| [`mogadishu-line8.aln.toml`](mogadishu-line8.aln.toml) | `line-8` | 8,457.3 m | 6 |
| [`mogadishu-line9.aln.toml`](mogadishu-line9.aln.toml) | `line-9` | 4,017.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
