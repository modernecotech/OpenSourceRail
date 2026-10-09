# Kafr-El-Sheikh Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kafr-el-sheikh-line1.aln.toml`](kafr-el-sheikh-line1.aln.toml) | `line-1` | 13,581.8 m | 8 |
| [`kafr-el-sheikh-line2.aln.toml`](kafr-el-sheikh-line2.aln.toml) | `line-2` | 8,161.5 m | 5 |
| [`kafr-el-sheikh-line3.aln.toml`](kafr-el-sheikh-line3.aln.toml) | `line-3` | 4,495.4 m | 4 |
| [`kafr-el-sheikh-line4.aln.toml`](kafr-el-sheikh-line4.aln.toml) | `line-4` | 2,995.0 m | 3 |
| [`kafr-el-sheikh-line5.aln.toml`](kafr-el-sheikh-line5.aln.toml) | `line-5` | 5,666.7 m | 4 |
| [`kafr-el-sheikh-line6.aln.toml`](kafr-el-sheikh-line6.aln.toml) | `line-6` | 7,366.4 m | 5 |
| [`kafr-el-sheikh-line7.aln.toml`](kafr-el-sheikh-line7.aln.toml) | `line-7` | 5,226.2 m | 4 |
| [`kafr-el-sheikh-line8.aln.toml`](kafr-el-sheikh-line8.aln.toml) | `line-8` | 3,123.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
