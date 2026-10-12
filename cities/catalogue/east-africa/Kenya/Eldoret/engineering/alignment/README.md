# Eldoret Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`eldoret-line1.aln.toml`](eldoret-line1.aln.toml) | `line-1` | 24,145.5 m | 9 |
| [`eldoret-line2.aln.toml`](eldoret-line2.aln.toml) | `line-2` | 14,309.2 m | 15 |
| [`eldoret-line3.aln.toml`](eldoret-line3.aln.toml) | `line-3` | 24,172.7 m | 20 |
| [`eldoret-line4.aln.toml`](eldoret-line4.aln.toml) | `line-4` | 4,911.0 m | 3 |
| [`eldoret-line5.aln.toml`](eldoret-line5.aln.toml) | `line-5` | 7,098.4 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
