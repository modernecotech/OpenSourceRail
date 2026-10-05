# Lusaka Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lusaka-line1.aln.toml`](lusaka-line1.aln.toml) | `line-1` | 32,206.9 m | 12 |
| [`lusaka-line2.aln.toml`](lusaka-line2.aln.toml) | `line-2` | 21,714.6 m | 7 |
| [`lusaka-line3.aln.toml`](lusaka-line3.aln.toml) | `line-3` | 25,249.0 m | 9 |
| [`lusaka-line4.aln.toml`](lusaka-line4.aln.toml) | `line-4` | 18,536.4 m | 8 |
| [`lusaka-line5.aln.toml`](lusaka-line5.aln.toml) | `line-5` | 20,289.5 m | 8 |
| [`lusaka-line6.aln.toml`](lusaka-line6.aln.toml) | `line-6` | 27,622.6 m | 10 |
| [`lusaka-line7.aln.toml`](lusaka-line7.aln.toml) | `line-7` | 25,355.9 m | 7 |
| [`lusaka-line8.aln.toml`](lusaka-line8.aln.toml) | `line-8` | 67,828.6 m | 20 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
