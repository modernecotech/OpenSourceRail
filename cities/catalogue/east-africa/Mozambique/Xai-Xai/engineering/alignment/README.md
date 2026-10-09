# Xai-Xai Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`xai-xai-line1.aln.toml`](xai-xai-line1.aln.toml) | `line-1` | 5,972.7 m | 4 |
| [`xai-xai-line2.aln.toml`](xai-xai-line2.aln.toml) | `line-2` | 6,717.0 m | 5 |
| [`xai-xai-line3.aln.toml`](xai-xai-line3.aln.toml) | `line-3` | 4,332.4 m | 4 |
| [`xai-xai-line4.aln.toml`](xai-xai-line4.aln.toml) | `line-4` | 2,396.2 m | 2 |
| [`xai-xai-line5.aln.toml`](xai-xai-line5.aln.toml) | `line-5` | 4,779.7 m | 4 |
| [`xai-xai-line6.aln.toml`](xai-xai-line6.aln.toml) | `line-6` | 5,436.5 m | 4 |
| [`xai-xai-line7.aln.toml`](xai-xai-line7.aln.toml) | `line-7` | 3,399.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
