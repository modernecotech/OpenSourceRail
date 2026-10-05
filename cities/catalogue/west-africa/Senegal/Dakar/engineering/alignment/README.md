# Dakar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dakar-line1.aln.toml`](dakar-line1.aln.toml) | `line-1` | 34,940.9 m | 12 |
| [`dakar-line2.aln.toml`](dakar-line2.aln.toml) | `line-2` | 28,560.4 m | 22 |
| [`dakar-line3.aln.toml`](dakar-line3.aln.toml) | `line-3` | 27,183.8 m | 8 |
| [`dakar-line4.aln.toml`](dakar-line4.aln.toml) | `line-4` | 22,412.5 m | 16 |
| [`dakar-line5.aln.toml`](dakar-line5.aln.toml) | `line-5` | 35,934.0 m | 24 |
| [`dakar-line6.aln.toml`](dakar-line6.aln.toml) | `line-6` | 61,918.6 m | 34 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
