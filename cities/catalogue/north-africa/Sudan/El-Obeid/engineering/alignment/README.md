# El-Obeid Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`el-obeid-line1.aln.toml`](el-obeid-line1.aln.toml) | `line-1` | 13,383.2 m | 10 |
| [`el-obeid-line10.aln.toml`](el-obeid-line10.aln.toml) | `line-10` | 3,439.3 m | 3 |
| [`el-obeid-line2.aln.toml`](el-obeid-line2.aln.toml) | `line-2` | 13,770.7 m | 8 |
| [`el-obeid-line3.aln.toml`](el-obeid-line3.aln.toml) | `line-3` | 11,014.8 m | 6 |
| [`el-obeid-line4.aln.toml`](el-obeid-line4.aln.toml) | `line-4` | 4,997.1 m | 5 |
| [`el-obeid-line5.aln.toml`](el-obeid-line5.aln.toml) | `line-5` | 7,896.4 m | 6 |
| [`el-obeid-line6.aln.toml`](el-obeid-line6.aln.toml) | `line-6` | 10,100.4 m | 7 |
| [`el-obeid-line7.aln.toml`](el-obeid-line7.aln.toml) | `line-7` | 3,011.0 m | 2 |
| [`el-obeid-line8.aln.toml`](el-obeid-line8.aln.toml) | `line-8` | 4,146.5 m | 4 |
| [`el-obeid-line9.aln.toml`](el-obeid-line9.aln.toml) | `line-9` | 3,791.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
