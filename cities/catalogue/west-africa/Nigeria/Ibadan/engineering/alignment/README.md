# Ibadan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ibadan-line1.aln.toml`](ibadan-line1.aln.toml) | `line-1` | 21,295.0 m | 11 |
| [`ibadan-line2.aln.toml`](ibadan-line2.aln.toml) | `line-2` | 17,180.3 m | 8 |
| [`ibadan-line3.aln.toml`](ibadan-line3.aln.toml) | `line-3` | 15,772.7 m | 8 |
| [`ibadan-line4.aln.toml`](ibadan-line4.aln.toml) | `line-4` | 25,289.9 m | 8 |
| [`ibadan-line5.aln.toml`](ibadan-line5.aln.toml) | `line-5` | 26,830.9 m | 10 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
