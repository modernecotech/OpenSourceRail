# Lubumbashi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lubumbashi-line1.aln.toml`](lubumbashi-line1.aln.toml) | `line-1` | 22,282.9 m | 7 |
| [`lubumbashi-line2.aln.toml`](lubumbashi-line2.aln.toml) | `line-2` | 21,763.4 m | 10 |
| [`lubumbashi-line3.aln.toml`](lubumbashi-line3.aln.toml) | `line-3` | 14,631.3 m | 4 |
| [`lubumbashi-line4.aln.toml`](lubumbashi-line4.aln.toml) | `line-4` | 26,156.3 m | 9 |
| [`lubumbashi-line5.aln.toml`](lubumbashi-line5.aln.toml) | `line-5` | 45,151.1 m | 11 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
