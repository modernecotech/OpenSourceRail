# Mogadishu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mogadishu-line1.aln.toml`](mogadishu-line1.aln.toml) | `line-1` | 33,442.5 m | 12 |
| [`mogadishu-line2.aln.toml`](mogadishu-line2.aln.toml) | `line-2` | 22,039.7 m | 10 |
| [`mogadishu-line3.aln.toml`](mogadishu-line3.aln.toml) | `line-3` | 13,901.8 m | 6 |
| [`mogadishu-line4.aln.toml`](mogadishu-line4.aln.toml) | `line-4` | 45,128.8 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
